import psycopg2
import numpy as np
from langchain_community.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate
from utils.metrics import QUERY_PROCESSING_TIME, QUERY_COUNT, DB_OPERATION_TIME, MetricsMiddleware


class QueryProcessor:
    def __init__(self, db_params, model_name="gpt-4"):
        self.db_params = db_params
        self.embeddings = OpenAIEmbeddings()
        self.llm = ChatOpenAI(model_name=model_name)
        
    def _cosine_similarity(self, a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    @MetricsMiddleware.track_time(DB_OPERATION_TIME)
    def query_database(self, query, top_k=3):
        query_embedding = self.embeddings.embed_query(query)
        
        with psycopg2.connect(**self.db_params) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT content, 1 - (embedding <=> %s) as similarity
                    FROM embeddings
                    ORDER BY embedding <=> %s
                    LIMIT %s
                """, (query_embedding, query_embedding, top_k))
                results = cur.fetchall()
        
        return [content for content, _ in results]
    
    @MetricsMiddleware.track_time(QUERY_PROCESSING_TIME)
    def get_answer(self, query):
        QUERY_COUNT.inc()
        relevant_docs = self.query_database(query)
        context = "\n".join(relevant_docs)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant. Use the following context to answer the question:\n\n{context}"),
            ("human", "{query}")
        ])
        
        messages = prompt.format_messages(context=context, query=query)
        response = self.llm.generate([messages])
        
        return response.generations[0][0].text