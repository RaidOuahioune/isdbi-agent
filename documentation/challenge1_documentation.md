# Use Case Processor: Financial Standards Journaling System

## Overview

The Use Case Processor Agent is a specialized component in our Islamic Finance Multi-Agent System designed to handle the first challenge category: "Use Case Scenarios". This agent's primary responsibility is to accurately process financial scenarios involving Islamic financial products and provide compliant accounting guidance based on AAOIFI Financial Accounting Standards (FAS).

## Agent Architecture

The Use Case Processor Agent sits within a larger multi-agent architecture that includes:

1. **Orchestrator Agent** - Routes user queries to appropriate specialized agents
2. **Standards Extractor Agent** - Extracts relevant information from AAOIFI standards
3. **Use Case Processor Agent** - Analyzes financial scenarios and provides accounting guidance
4. **Compliance Validator Agent** - Validates the compliance of proposed solutions

## Workflow Process

When a financial use case scenario is submitted, the system follows this workflow:

```
User → UI → Orchestrator → Use Case Processor (Primary) + Standards Extractor (Supporting)
```

1. **Initial Query Processing**: 
   - The user submits a financial scenario (e.g., Ijarah MBT accounting case)
   - The Orchestrator Agent identifies this as a use case scenario and activates the appropriate agents

2. **Standards Analysis**:
   - The Standards Extractor Agent retrieves relevant standards information
   - For example, with Ijarah MBT, FAS 28 is identified as the primary applicable standard
   - Specific requirements are extracted (e.g., recognition of right-of-use assets, treatment of deferred costs)

3. **Scenario Processing**:
   - The Use Case Processor analyzes the scenario details
   - It identifies the financial product type (e.g., Ijarah MBT - lease with ownership transfer)
   - It determines which standards apply to the specific use case

4. **Accounting Guidance Generation**:
   - The agent performs required calculations based on the scenario data
   - It prepares appropriate journal entries with correct amounts
   - It provides detailed explanations for each calculation
   - It references specific sections of the applicable standards

5. **Validation and Response Consolidation**:
   - The proposed solution is validated against standard requirements and Shariah principles
   - The Orchestrator consolidates all outputs into a coherent response

## Technical Implementation

The Use Case Processor Agent is implemented as a class that extends the base `Agent` class:

```python
class UseCaseProcessorAgent(Agent):
    """Agent responsible for processing financial use cases and providing accounting guidance."""

    def __init__(self):
        super().__init__(system_prompt=USE_CASE_PROCESSOR_SYSTEM_PROMPT)

    def process_use_case(self, scenario: str, standards_info: Optional[Dict] = None):
        # Process the scenario and provide guidance
        # ...
```

Key technical aspects:

1. **Context Gathering**: The agent retrieves:
   - Explicitly provided standards information 
   - Additional relevant information from the vector database using semantic search

2. **Prompt Engineering**: The agent uses a specialized system prompt that instructs it to:
   - Analyze practical financial scenarios
   - Determine which standards apply
   - Provide step-by-step accounting guidance
   - Generate appropriate journal entries with explanations

3. **Vector Database Integration**: The agent leverages a vector database to retrieve:
   - Relevant standard sections
   - Calculation methodologies
   - Example applications

4. **Structured Output**: The response contains:
   - Identified financial product type
   - Applicable AAOIFI standards
   - Step-by-step calculation methodology
   - Journal entries with explanations
   - References to specific standard sections

## Example: Ijarah MBT Accounting Challenge

For the Ijarah MBT Accounting challenge, the agent processes:

1. **Scenario Analysis**:
   - Identifies an Ijarah MBT arrangement (lease with transfer)
   - Generator cost: $450,000 + $12,000 (import tax) + $30,000 (freight)
   - 2-year term, $5,000 residual value, $3,000 purchase option
   - Yearly rental: $300,000

2. **Standards Application**:
   - Applies FAS 28 (Ijarah) requirements
   - Uses the Underlying Asset Cost Method for initial recognition

3. **Calculation Methodology**:
   - Determines Right-of-Use (ROU) asset value: $492,000 - $3,000 = $489,000
   - Calculates Deferred Ijarah Cost: $600,000 - $489,000 = $111,000
   - Computes Amortizable Amount: $489,000 - $2,000 = $487,000

4. **Journal Entry Generation**:
   ```
   Dr. Right of Use Asset (ROU)    $489,000
   Dr. Deferred Ijarah Cost        $111,000
      Cr. Ijarah Liability         $600,000
   ```

5. **Explanation Provision**:
   - Explains the treatment of terminal value
   - Details the amortization approach
   - References specific FAS 28 sections

## Value Proposition

The Use Case Processor Agent delivers significant value by:

1. **Accuracy**: Ensuring precise application of AAOIFI standards to complex scenarios
2. **Consistency**: Providing standardized accounting treatments across different cases
3. **Educational Value**: Offering detailed explanations that help users understand the standards
4. **Efficiency**: Automating complex calculations that would otherwise be time-consuming
5. **Compliance**: Ensuring adherence to Islamic finance principles and accounting requirements

This agent is a critical component in our solution for making AAOIFI standards more accessible and easier to implement in practical scenarios.