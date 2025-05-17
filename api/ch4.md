# ISDBI Agent API Documentation - Chapter 4

This document describes the API endpoints for the Product Design and Compliance Verification features of the ISDBI Agent API.

## 1. Financial Product Design

### Endpoint

```
POST /product-design
```

Design a Shariah-compliant financial product based on specified requirements.

This endpoint processes product requirements and returns a comprehensive financial product concept with Islamic contract structures, AAOIFI standards considerations, and Shariah compliance checkpoints.

### Request Format

```json
{
  "product_objective": "string",
  "risk_appetite": "string",
  "investment_tenor": "string",
  "target_audience": "string", 
  "asset_focus": "string (optional)",
  "desired_features": ["string"],
  "specific_exclusions": ["string"],
  "additional_notes": "string (optional)"
}
```

#### Field Descriptions

- `product_objective`: The objective of the financial product
- `risk_appetite`: The risk appetite level (e.g., "Low", "Medium", "High")
- `investment_tenor`: The investment tenor (e.g., "Short-term (up to 1 year)", "Medium-term (1-5 years)", "Long-term (5+ years)")
- `target_audience`: The target audience for the product (e.g., "Retail investors", "Corporate clients", "SMEs")
- `asset_focus`: The asset focus for the product (optional)
- `desired_features`: List of desired features
- `specific_exclusions`: List of specific exclusions
- `additional_notes`: Additional requirements or notes (optional)

### Response Format

```json
{
  "suggested_product_concept_name": "string",
  "recommended_islamic_contracts": ["string"],
  "original_requirements": {
    "product_objective": "string",
    "risk_appetite": "string",
    "investment_tenor": "string",
    "target_audience": "string",
    "asset_focus": "string",
    "desired_features": ["string"],
    "specific_exclusions": ["string"],
    "additional_notes": "string"
  },
  "rationale_for_contract_selection": "string",
  "proposed_product_structure_overview": "string",
  "key_aaoifi_fas_considerations": {
    "standard_id": "string"
  },
  "shariah_compliance_checkpoints": ["string"],
  "potential_areas_of_concern": ["string"],
  "potential_risks_and_mitigation_notes": "string",
  "next_steps_for_detailed_design": ["string"]
}
```

#### Field Descriptions

- `suggested_product_concept_name`: Name for the proposed product
- `recommended_islamic_contracts`: List of recommended Islamic contract structures
- `original_requirements`: The initial requirements provided in the request
- `rationale_for_contract_selection`: Explanation for why these contracts were selected
- `proposed_product_structure_overview`: Detailed description of the product structure
- `key_aaoifi_fas_considerations`: Mapping of AAOIFI FAS standards to their relevant considerations
- `shariah_compliance_checkpoints`: List of key compliance points to check
- `potential_areas_of_concern`: List of potential Shariah compliance issues
- `potential_risks_and_mitigation_notes`: Notes on mitigating identified risks
- `next_steps_for_detailed_design`: Recommended next steps for implementing the product

## 2. Compliance Verification

### Endpoint

```
POST /compliance/verify
```

Verify compliance of a financial report with AAOIFI standards.

This endpoint processes a document's content and verifies its compliance with AAOIFI standards, returning a detailed compliance report with structured verification results.

### Request Format

```json
{
  "document_content": "string",
  "document_name": "string"
}
```

#### Field Descriptions

- `document_content`: The full text content of the financial report to verify
- `document_name`: The name of the document (defaults to "Uploaded Document" if not provided)

### Response Format

```json
{
  "document_name": "string",
  "timestamp": "string",
  "compliance_report": "string", 
  "structured_report": [
    {
      "standard": "string",
      "requirement": "string",
      "status": "string",
      "status_code": "string",
      "comments": "string"
    }
  ],
  "document": "string"
}
```

#### Field Descriptions

- `document_name`: The name of the document that was verified
- `timestamp`: ISO format timestamp when the verification was performed
- `compliance_report`: Detailed textual analysis of compliance
- `structured_report`: Array of compliance checkpoints in structured format:
  - `standard`: The AAOIFI standard identifier (e.g., "FAS 4", "FAS 28")
  - `requirement`: Description of the compliance requirement
  - `status`: Human-readable status (e.g., "Compliant", "Partial", "Missing")
  - `status_code`: Machine-readable status code ("compliant", "partial", "missing")
  - `comments`: Detailed comments or suggestions about this requirement
- `document`: The original document content that was analyzed
