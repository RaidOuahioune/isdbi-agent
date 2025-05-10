# Islamic Finance Compliance API

This FastAPI server connects to a Neo4j database containing Islamic finance knowledge and uses Gemini LLM to provide RAG-enhanced answers to compliance questions.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create an environment file:
   ```bash
   cp .env.example .env
   ```
   
3. Edit the `.env` file and update the Neo4j credentials and Google API key (if using cloud Gemini)

## Running the server

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Usage

### Health Check
```
GET /health
```

### Ask a Compliance Question
```
POST /api/ask
```

Request body:
```json
{
  "question": "Does the use of riba interest for asset financing allowed in islam?",
  "top_k": 6,
  "temperature": 0.1
}
```

Response:
```json
{
  "answer": "No, the use of riba (interest) for asset financing is not allowed in Islam...",
  "processing_time": 1.245
}
```

## Interactive API Documentation

Once the server is running, you can access the interactive API documentation at:

* Swagger UI: http://localhost:8000/docs
* ReDoc: http://localhost:8000/redoc
