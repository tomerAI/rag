import psycopg2
import numpy as np
import os
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from utils.metrics import QUERY_PROCESSING_TIME, QUERY_COUNT, DB_OPERATION_TIME, MetricsMiddleware
import traceback
from utils.logger import setup_logger


class QueryProcessor:
    def __init__(self, db_params, model_name="gpt-4"):
        self.db_params = db_params
        self.embeddings = OpenAIEmbeddings()
        self.llm = ChatOpenAI(model_name=model_name)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant. Use the following context to answer the question:\n\n{context}"),
            ("human", "{query}")
        ])
        self.logger = setup_logger(__name__)
    
    def _cosine_similarity(self, a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    @MetricsMiddleware.track_time(DB_OPERATION_TIME)
    def query_database(self, query, top_k=3):
        query_embedding = self.embeddings.embed_query(query)
        schema = os.getenv('DBT_SCHEMA')
        
        try:
            with psycopg2.connect(**self.db_params) as conn:
                with conn.cursor() as cur:
                    query = f"""
                        SELECT content,
                               1 - (embedding <=> %s::vector) as similarity
                        FROM {schema}.embeddings
                        WHERE embedding <=> %s::vector < 0.8
                        ORDER BY embedding <=> %s::vector
                        LIMIT %s;
                    """
                    cur.execute(query, (query_embedding, query_embedding, query_embedding, top_k))
                    results = cur.fetchall()
                    
                    return [{
                        'content': row[0],
                        'similarity': float(row[1])
                    } for row in results]
        except Exception as e:
            self.logger.error(f"Error processing query: {str(e)}")
            raise

    @MetricsMiddleware.track_time(QUERY_PROCESSING_TIME)
    def get_answer(self, query):
        QUERY_COUNT.inc()
        relevant_docs = self.query_database(query)
        context = "\n".join(doc['content'] for doc in relevant_docs)
        
        messages = self.prompt.format_messages(
            context=context,
            query=query
        )
        response = self.llm.generate([messages])
        return response.generations[0][0].text