# Compliance Verification Agent Documentation

## Overview
The Compliance Verification Agent is a specialized component of the ISDBI system designed to analyze financial reports and documents for compliance with AAOIFI (Accounting and Auditing Organization for Islamic Financial Institutions) standards. It leverages advanced NLP capabilities to detect violations and provide detailed compliance reports.

## Architecture

### Core Components

1. **ComplianceVerifierAgent**
   - Location: `components/agents/compliance_verfiier.py`
   - Main class responsible for verification logic
   - Inherits from base Agent class
   - Uses custom system prompts for compliance checking

2. **DocumentProcessor**
   - Location: `utils/document_processor.py`
   - Handles document parsing and text extraction
   - Supports PDF and plain text files
   - Uses python-magic for file type detection

3. **Evaluation System**
   - Location: `components/evaluation/`
   - Provides scoring and assessment of verification results
   - Multiple expert agents evaluate different aspects
   - Generates detailed evaluation reports

### Directory Structure
```
isdbi-agent/
├── components/
│   ├── agents/
│   │   ├── compliance_verfiier.py
│   │   └── base_agent.py
│   └── evaluation/
│       ├── __init__.py
│       ├── evaluation_manager.py
│       └── expert_agents.py
├── utils/
│   ├── document_processor.py
│   ├── compliance_tests.py
│   └── verify_compliance.py
└── use_cases/
    └── compliance/
        └── usecase_1.txt
```

## Usage

### Command Line Interface

1. **Verify Single Document**
```bash
python main.py --verify path/to/document.pdf
```

Optional flags:
- `--verify-verbose`: Show detailed processing output

2. **Run Compliance Tests**
```bash
python main.py --compliance-tests
```

Optional flags:
- `--compliance-verbose`: Show detailed test output
- `--compliance-output {json,csv}`: Specify results format

### Python API

1. **Direct Verification**
```python
from components.agents.compliance_verfiier import ComplianceVerifierAgent
from utils.document_processor import DocumentProcessor

# Initialize components
verifier = ComplianceVerifierAgent()
processor = DocumentProcessor()

# Process document
doc_content = processor.process_document("path/to/document.pdf")

# Verify compliance
result = verifier.verify_compliance(doc_content["content"])
print(result["compliance_report"])
```

2. **Using Test Framework**
```python
from utils.compliance_tests import run_compliance_tests

# Run tests with custom options
results = run_compliance_tests(
    verbose=True,
    output_format="json"
)
```

## Input/Output Formats

### Input Documents
- Supported formats:
  - PDF (`.pdf`)
  - Plain text (`.txt`)
- Document structure:
  - Financial reports
  - Balance sheets
  - Income statements
  - Notes to financial statements

### Output Format

1. **Compliance Report**
```python
{
    "document": str,  # Original document content
    "compliance_report": str,  # Detailed compliance analysis
}
```

2. **Evaluation Results**
```python
{
    "test_case": str,  # Test case identifier
    "evaluation": {
        "overall_score": float,  # 0-10 scale
        "expert_evaluations": {
            "shariah_compliance": dict,
            "financial_accuracy": dict,
            "standards_compliance": dict,
            "logical_reasoning": dict,
            "practical_application": dict
        }
    }
}
```

## Testing

### Test Cases
- Located in `use_cases/compliance/`
- Format:
  - Report content in markdown
  - Ground truth violations after `- VIOLATIONS:` marker
- Each file tests specific compliance scenarios

### Running Tests
1. Using CLI:
```bash
python main.py --compliance-tests --compliance-output json
```

2. Using Python:
```python
from utils.compliance_tests import run_compliance_tests
results = run_compliance_tests(output_format="json")
```

### Results
- Saved in `results/` directory
- Formats:
  - JSON: Detailed evaluation data
  - CSV: Simplified scoring matrix

## Dependencies
- Python 3.8+
- Required packages:
  - `python-magic`: File type detection
  - `unstructured`: PDF processing
  - `langchain`: LLM integration
  - Additional dependencies in `requirements.txt`

## Best Practices

1. **Document Processing**
   - Use clean, well-formatted financial reports
   - Ensure documents follow standard accounting formats
   - Include all relevant notes and disclosures

2. **Compliance Testing**
   - Regular testing with standard test cases
   - Validate results against ground truth
   - Monitor evaluation scores for consistency

3. **Error Handling**
   - Check file format compatibility
   - Validate document structure
   - Handle processing exceptions gracefully

## Common Issues & Solutions

1. **File Type Errors**
   - Issue: Unsupported file format
   - Solution: Convert to PDF or plain text

2. **Processing Failures**
   - Issue: PDF extraction errors
   - Solution: Check PDF formatting and try text extraction

3. **Low Compliance Scores**
   - Issue: Missing key information in reports
   - Solution: Ensure all required disclosures are present

## Future Enhancements
1. Support for additional file formats
2. Enhanced violation detection accuracy
3. Real-time compliance monitoring
4. Integration with document management systems
5. Custom compliance rule configuration

## Support
For issues and questions:
1. Check existing documentation
2. Review test cases for examples
3. Contact system administrators for assistance