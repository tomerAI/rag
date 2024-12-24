import gradio as gr
import os
from query_processor import QueryProcessor
from utils.db import wait_for_db, get_db_params
from utils.logger import setup_logger

logger = setup_logger(__name__)

def initialize_app():
    # Get database parameters
    db_params = get_db_params()
    
    # Wait for database to be ready
    if not wait_for_db(db_params):
        logger.error("Failed to connect to database")
        raise RuntimeError("Database connection failed")

    # Initialize the query processor
    return QueryProcessor(db_params)

def process_query(message, processor):
    try:
        response = processor.get_answer(message)
        return response
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return f"Error: {str(e)}"

def main():
    try:
        from utils.metrics import start_metrics_server
        start_metrics_server()
        processor = initialize_app()
        
        iface = gr.Interface(
            fn=lambda message: process_query(message, processor),
            inputs=gr.Textbox(lines=2, placeholder="Enter your question here..."),
            outputs=gr.Textbox(label="Answer"),
            title="Document Q&A System",
            description="Ask questions about your documents and get AI-powered answers.",
            examples=[
                ["What are the main topics covered in the documents?"],
                ["Can you summarize the key points?"]
            ]
        )
        
        iface.launch(server_name="0.0.0.0", server_port=7860)
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        raise

if __name__ == "__main__":
    main() 