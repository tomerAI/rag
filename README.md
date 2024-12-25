# Document Q&A System

A powerful document question-answering system that uses embeddings and vector search to provide accurate answers based on your documents. The system is containerized using Docker and includes monitoring capabilities.

## Project Structure

```
├── src/                    # Source code directory
│   ├── app.py             # Main application with Gradio interface
│   ├── query_processor.py # Handles document queries
│   ├── embedding_processor.py # Processes document embeddings
│   └── utils/             # Utility functions
├── data/                  # Data storage
├── monitoring/            # Monitoring configuration
├── dbt/                   # Data transformation
├── docker/               # Docker configuration files
├── requirements.txt      # Python dependencies
└── docker-compose.yml    # Docker services configuration
```

## Core Features

1. **Document Processing**
   - Upload documents (.txt, .py, .md)
   - Automatic embedding generation
   - Vector database storage

2. **Question Answering**
   - Natural language query processing
   - Context-aware responses
   - Example questions provided

3. **Infrastructure**
   - Containerized application
   - Monitoring system
   - Database integration

## Getting Started

1. Copy `.env.example` to `.env` and configure your environment variables
2. Build and start the services:
   ```bash
   docker-compose up -d
   ```
3. Access the web interface at `http://localhost:7860`

## Technical Stack

- Python
- Gradio (Web Interface)
- Vector Database
- Docker
- DBT (Data Build Tool)
- Prometheus/Grafana (Monitoring)

## Todo List

1. **API Development**
   - [ ] Build REST API endpoints for data posting to database
   - [ ] Implement authentication and authorization
   - [ ] Add rate limiting
   - [ ] Create API documentation

2. **Privacy and Security**
   - [X] Add PII detection and masking
   - [ ] Create and use PII detection model on danish data

2. **Feature Enhancements**
   - [ ] Add support for more document formats (PDF, DOCX)
   - [ ] Implement batch processing for multiple documents
   - [ ] Add document metadata management
   - [ ] Create document versioning system

3. **Database Optimizations**
   - [ ] Implement database indexing
   - [ ] Add caching layer
   - [ ] Optimize query performance
   - [ ] Add database backup system

4. **User Experience**
   - [ ] Enhance error handling and user feedback
   - [ ] Add progress indicators for long operations
   - [ ] Implement document preview feature
   - [ ] Add user settings and preferences

5. **Testing & Quality**
   - [ ] Add comprehensive unit tests
   - [ ] Implement integration tests
   - [ ] Add load testing
   - [ ] Set up CI/CD pipeline
