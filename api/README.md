# ISDBI Agent API Documentation

This document provides detailed information about the API endpoints available in the ISDBI Agent system.

## Overview

The ISDBI Agent API exposes various financial analysis agents as RESTful endpoints. These agents can process scenarios, extract standards information, analyze transactions, and more.

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
  "status": "ok",
  "version": "1.0.0"
}
```

### Use Case Processing

```
POST /api/use-case/process
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
POST /api/standards/extract
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
POST /api/transaction/analyze
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

### Transaction Rationale

```
POST /api/transaction/rationale
```

Generate a detailed rationale for a transaction analysis.

**Request**
```json
{
  "transaction_details": "Details of the transaction to analyze",
  "analysis_results": "Previous analysis results if available"
}
```

**Response**
```json
{
  "rationale": "Detailed rationale for the transaction compliance assessment",
  "references": "Reference to relevant standards or principles"
}
```

### Cross-Standard Analysis

```
POST /api/cross-standard/analyze
```

Analyze how different standards apply to a particular scenario.

**Request**
```json
{
  "scenario": "The scenario to analyze across standards",
  "standards": ["FAS1", "FAS2", "IFRS9"]
}
```

**Response**
```json
{
  "analysis": "Comparative analysis across the specified standards",
  "recommendations": "Recommended approaches for compliance"
}
```

### Knowledge Integration

```
POST /api/knowledge/integrate
```

Integrate new knowledge into the system.

**Request**
```json
{
  "knowledge_text": "Text containing new knowledge to integrate",
  "category": "standards",
  "source": "Source of the knowledge"
}
```

**Response**
```json
{
  "status": "success",
  "integrated_id": "ID of the integrated knowledge"
}
```

### Expert Evaluation

```
POST /api/evaluation/expert
```

Get an evaluation from a specific type of expert.

**Request**
```json
{
  "content": "Content to evaluate",
  "expert_type": "shariah",
  "evaluation_criteria": ["accuracy", "compliance"]
}
```

**Response**
```json
{
  "evaluation": "Expert evaluation of the content",
  "score": 0.85,
  "recommendations": "Recommendations for improvement"
}
```

## Error Handling

All endpoints return standard HTTP status codes:

- 200: Success
- 400: Bad Request - The request was malformed or invalid
- 404: Not Found - The requested resource was not found
- 500: Internal Server Error - An unexpected error occurred on the server

Error responses include details about the error:

```json
{
  "error": "Error message",
  "details": {
    "field": "Additional error details"
  }
}
```

## Versioning

The current API version is v1. All endpoints are prefixed with `/api` and no explicit version number is required in the URL.

## Rate Limiting

Currently, there is no rate limiting implemented. This is planned for future development.

## Running the API

You can run the API using Docker:

```bash
docker-compose -f docker-compose.api.yml up
```

Or directly using Python:

```bash
cd /path/to/isdbi-agent
python -m api.run
```
