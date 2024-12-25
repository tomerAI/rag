import gradio as gr
import os
from query_processor import QueryProcessor
from embedding_processor import DocumentEmbedder
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

    # Initialize both processors
    query_processor = QueryProcessor(db_params)
    embedding_processor = DocumentEmbedder()
    
    return query_processor, embedding_processor

def process_query(message, processor):
    try:
        response = processor.get_answer(message)
        return response
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return f"Error: {str(e)}"

def process_file(file_obj, embedder):
    try:
        if file_obj is None:
            return "No file uploaded"
            
        # Create temporary file path
        temp_path = file_obj.name
        
        # Process the file
        embeddings = embedder.process_file(temp_path)
        
        # Store embeddings in database
        success = embedder.store_embeddings(embeddings)
        
        if success:
            return f"Successfully processed and stored embeddings for {os.path.basename(temp_path)}"
        else:
            return "Failed to store embeddings in database"
            
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        return f"Error: {str(e)}"

def main():
    try:
        from utils.metrics import start_metrics_server
        start_metrics_server()
        query_processor, embedding_processor = initialize_app()
        
        with gr.Blocks(title="Document Q&A System") as iface:
            gr.Markdown("# Document Q&A System")
            
            with gr.Tab("Ask Questions"):
                query_input = gr.Textbox(lines=2, placeholder="Enter your question here...")
                query_output = gr.Textbox(label="Answer")
                query_button = gr.Button("Ask Question")
                query_button.click(
                    fn=lambda x: process_query(x, query_processor),
                    inputs=query_input,
                    outputs=query_output
                )
                
            with gr.Tab("Upload Documents"):
                file_input = gr.File(
                    label="Upload Document",
                    file_types=[".txt", ".py", ".md"]
                )
                upload_output = gr.Textbox(label="Upload Status")
                upload_button = gr.Button("Process Document")
                upload_button.click(
                    fn=lambda x: process_file(x, embedding_processor),
                    inputs=file_input,
                    outputs=upload_output
                )
                
            gr.Examples(
                examples=[
                    ["What are the main topics covered in the documents?"],
                    ["Can you summarize the key points?"]
                ],
                inputs=query_input
            )
        
        iface.launch(server_name="0.0.0.0", server_port=7860)
        
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        raise

if __name__ == "__main__":
    main() 