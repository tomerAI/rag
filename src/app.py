import gradio as gr
import os
from query_processor import QueryProcessor

# Database connection parameters
db_params = {
    'host': os.getenv('DBT_HOST'),
    'port': os.getenv('DBT_PORT'),
    'user': os.getenv('DBT_USER'),
    'password': os.getenv('DBT_PASSWORD'),
    'database': os.getenv('DBT_DATABASE')
}

# Initialize the query processor
processor = QueryProcessor(db_params)

def process_query(message):
    try:
        response = processor.get_answer(message)
        return response
    except Exception as e:
        return f"Error: {str(e)}"

# Create the Gradio interface
iface = gr.Interface(
    fn=process_query,
    inputs=gr.Textbox(lines=2, placeholder="Enter your question here..."),
    outputs=gr.Textbox(label="Answer"),
    title="Document Q&A System",
    description="Ask questions about your documents and get AI-powered answers.",
    examples=[
        ["What are the main topics covered in the documents?"],
        ["Can you summarize the key points?"]
    ]
)

if __name__ == "__main__":
    iface.launch(server_name="0.0.0.0", server_port=7860) 