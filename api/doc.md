# ISDBI Agent API Documentation

This document provides detailed information about the API endpoints available in the ISDBI Agent system.

## Overview

The ISDBI Agent API exposes various Islamic financial analysis agents as RESTful endpoints. These agents can process scenarios, extract standards information, analyze transactions, and provide standards enhancement proposals.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API does not implement authentication. This is planned for future development.

## Endpoints

### Health Check

```
GET /health
```

Returns a simple health check response to verify the API is running.

**Response**
```json
{
  "status": "healthy"
}
```

### Use Case Processing

```
POST /use-case/process
```

Process a financial scenario and provide accounting guidance.

**Request**
```json
{
  "scenario": "A financial institution wants to structure a home financing product using the diminishing musharakah contract...",
  "standards_info": {
    "extracted_info": "Optional pre-extracted standards information"
  }
}
```

**Response**
```json
{
  "scenario": "A financial institution wants to structure a home financing product...",
  "accounting_guidance": "Based on the scenario provided, the appropriate accounting treatment would be..."
}
```

### Standards Extraction

```
POST /use-case/standards/extract
```

Extract and summarize information from standards documents.

**Request**
```json
{
  "document_text": "Full text of the standards document...",
  "query": "Optional specific query to focus extraction"
}
```

**Response**
```json
{
  "extracted_info": "The extracted and summarized standards information",
  "document_id": "Optional document identifier"
}
```

### Transaction Analysis

```
POST /transaction/analyze
```

Analyze a financial transaction for compliance with Islamic finance principles.

**Request**
```json
{
  "transaction_details": "Details of the transaction to analyze",
  "additional_context": "Optional additional context for analysis"
}
```

**Response**
```json
{
  "analysis": "Detailed analysis of the transaction",
  "compliant": true,
  "rationale": "Rationale for the compliance assessment"
}
```

#### Structured Transaction Input Format

For more detailed transaction analysis, you can provide a structured input format:

```json
{
  "transaction_details": {
    "context": "Description of the transaction context",
    "journal_entries": [
      {
        "debit_account": "Account name to debit",
        "credit_account": "Account name to credit",
        "amount": 1000.00
      }
    ],
    "additional_info": {
      "contract_type": "Murabaha",
      "transaction_date": "2025-05-16"
    }
  }
}
```

### Detailed Transaction Analysis

```
POST /transaction/analyze-detailed
```

Analyze a financial transaction in detail using the specialized transaction analyzer.

**Request**
```json
{
  "transaction_input": "A Sukuk issuance by XYZ Company with a face value of $100 million..."
}
```

OR with structured input:

```json
{
  "transaction_input": {
    "context": "Sukuk issuance",
    "journal_entries": [
      {
        "debit_account": "Cash",
        "credit_account": "Sukuk Liability",
        "amount": 100000000
      }
    ],
    "additional_info": {
      "maturity": "5 years",
      "profit_rate": "4.5%"
    }
  }
}
```

**Response**
```json
{
  "transaction_details": {...},
  "analysis": "This transaction appears to be a Sukuk issuance...",
  "identified_standards": ["FAS 34", "FAS 25"],
  "retrieval_stats": {
    "chunk_count": 15,
    "chunks_summary": ["..."]
  }
}
```

### Standards Enhancement

```
POST /enhancement/standards
```

Generate standards enhancement proposals based on a trigger scenario.

**Request**
```json
{
  "standard_id": "10",
  "trigger_scenario": "A financial institution wants to structure an Istisna'a contract for the development of a large-scale AI software platform...",
  "include_cross_standard_analysis": true
}
```

**Response**
```json
{
  "standard_id": "10",
  "trigger_scenario": "...",
  "review": "The review analysis of the standard...",
  "proposal": "The enhancement proposal...",
  "validation": "The validation results...",
  "original_text": "Original text from the standard...",
  "proposed_text": "Proposed enhanced text...",
  "cross_standard_analysis": "Analysis of impacts on other standards...",
  "compatibility_matrix": {...}
}
```

## Error Handling

All endpoints return standard HTTP status codes:

- 200: Success
- 400: Bad Request - The request was malformed or invalid
- 404: Not Found - The requested resource was not found
- 500: Internal Server Error - An unexpected error occurred on the server

The API includes global exception handling middleware that ensures consistent error responses.

Error responses include details about the error:

```json
{
  "error": "Error message",
  "details": "Additional error details"
}
```

## Security Considerations

### Current Implementation

Currently, the API does not implement authentication or authorization. This should be addressed before deploying to a production environment.

### Recommendations for Production Deployment

1. **Authentication**: Implement OAuth 2.0 or API key-based authentication
2. **Rate Limiting**: Add rate limiting to prevent abuse
3. **HTTPS**: Ensure all traffic is encrypted using HTTPS
4. **Input Validation**: Strict validation of all input data
5. **Logging**: Comprehensive logging for security auditing
6. **Secrets Management**: Use a secure method for managing API keys and other secrets

## Environment Setup

### Prerequisites

- Python 3.12 or higher
- Required Python packages (install using `pip install -r requirements.txt`):
  - fastapi==0.115.12
  - uvicorn==0.34.2
  - python-dotenv==1.1.0
  - langchain and related libraries
  - Other dependencies as listed in requirements.txt

### Environment Variables

The API requires the following environment variables:
- `GEMINI_API_KEY`: Your Google Gemini API key for accessing the LLM services

## Running the API

### Using Docker

The easiest way to run the API is using Docker:

```bash
docker-compose -f docker-compose.api.yml up
```

This will build the Docker image if needed and start the API service on port 8000.

### Using Python Directly

You can also run the API directly using Python:

```bash
cd /path/to/isdbi-agent
python -m api.run
```

For more options, run:

```bash
python -m api.run --help
```

Available configuration options:
- `--host`: Host to run the server on (default: 0.0.0.0)
- `--port`: Port to run the server on (default: 8000)
- `--reload`: Enable auto-reload for development
- `--workers`: Number of worker processes (default: 1)

### Standards Enhancement

```
POST /enhancement/standards
```

Generate standards enhancement proposals based on a trigger scenario.

**Request**
```json
{
  "standard_id": "10",
  "trigger_scenario": "A financial institution wants to structure an Istisna'a contract for the development of a large-scale AI software platform...",
  "include_cross_standard_analysis": true
}
```

**Response**
```json
{
  "standard_id": "10",
  "trigger_scenario": "...",
  "review": "The review analysis of the standard...",
  "proposal": "The enhancement proposal...",
  "validation": "The validation results...",
  "original_text": "Original text from the standard...",
  "proposed_text": "Proposed enhanced text...",
  "cross_standard_analysis": "Analysis of impacts on other standards...",
  "compatibility_matrix": {...}
}
```

### Detailed Transaction Analysis

```
POST /transaction/analyze-detailed
```

Analyze a financial transaction in detail using the specialized transaction analyzer.

**Request**
```json
{
  "transaction_input": "A Sukuk issuance by XYZ Company with a face value of $100 million..."
}
```

OR with structured input:

```json
{
  "transaction_input": {
    "context": "Sukuk issuance",
    "journal_entries": [
      {
        "debit_account": "Cash",
        "credit_account": "Sukuk Liability",
        "amount": 100000000
      }
    ],
    "additional_info": {
      "maturity": "5 years",
      "profit_rate": "4.5%"
    }
  }
}
```

**Response**
```json
{
  "transaction_details": {...},
  "analysis": "This transaction appears to be a Sukuk issuance...",
  "identified_standards": ["FAS 34", "FAS 25"],
  "retrieval_stats": {
    "chunk_count": 15,
    "chunks_summary": ["..."]
  }
}
```

## API Implementation Details

### Architecture Overview

The API is built using FastAPI with a modular architecture:

- **Routers**: Handle endpoint routing and request/response validation
- **Services**: Implement business logic and agent interactions
- **Schemas**: Define Pydantic models for request and response data

The API implements the following routers:
- **use_case**: For processing financial scenarios and extracting standards information
- **transaction**: For analyzing financial transactions and detailed transaction analysis
- **enhancement**: For generating standards enhancement proposals

### Project Structure

```
api/
├── __init__.py              # Package initialization
├── app.py                   # Main FastAPI application
├── run.py                   # Script to run the API with Uvicorn
├── doc.md                   # API documentation
├── routers/                 # API route definitions
│   ├── __init__.py
│   ├── enhancement.py       # Standards enhancement endpoints
│   ├── transaction.py       # Transaction analysis endpoints
│   └── use_case.py          # Use case processing endpoints
├── schemas/                 # Pydantic data models
│   └── ...
└── services/                # Business logic implementation
    └── ...
```

### Design Principles

This modular design ensures clean separation of concerns and makes the codebase more maintainable and extendable. Key design principles include:

1. **Separation of Concerns**: Each module has a specific responsibility
2. **RESTful API Design**: Following REST principles for API endpoints
3. **Error Handling**: Consistent error handling across all endpoints
4. **Validation**: Input validation using Pydantic schemas
