# Standards Enhancement Feature Documentation

## Overview

The Standards Enhancement feature is a specialized multi-agent system designed to help improve AAOIFI Financial Accounting Standards (FAS) by identifying areas for enhancement, proposing specific changes, and validating those changes against Shariah principles.

The system uses three specialized AI agents working together in a coordinated workflow:

1. **Reviewer Agent**: Analyzes standards and identifies potential gaps, ambiguities, or areas for improvement
2. **Proposer Agent**: Generates specific text changes to address the identified issues
3. **Validator Agent**: Validates the proposed changes against Shariah principles and standards consistency

## System Requirements

To run the Standards Enhancement feature, you need:

- Python 3.9+ 
- Required packages (install via `pip install -r requirements.txt`):
  - langchain and langchain-core
  - langchain-google-genai
  - llama-index-core
  - llama-index-embeddings-huggingface
  - transformers
  - langgraph
  - python-dotenv

The system also requires access to:
- The vector database containing AAOIFI standards stored in `vector_db_storage/`
- API keys for the LLM (set in `.env` file)

## Setup Instructions

1. **Clone the repository** (if not already done)
   ```bash
   git clone <repository-url>
   cd isdbi-agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API keys**
   
   Create a `.env` file in the project root with your Google Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

4. **Verify the vector database**
   
   Ensure the `vector_db_storage/` directory contains the embedded AAOIFI standards.

## Running the Standards Enhancement Feature

There are three ways to run the Standards Enhancement feature:

### 1. Using the dedicated demo script

```bash
python3 standards_enhancement_demo.py [--test-case INDEX | --custom | --all]
```

Options:
- `--test-case INDEX`: Run a specific test case by index (0, 1, or 2)
- `--custom`: Run with custom input parameters
- `--all`: Run all test cases sequentially
- No arguments: Run in interactive mode

### 2. Using the main application with enhancement command

```bash
python3 main.py
```

Then use the `/enhance` command followed by the standard ID:

```
You: /enhance 10
```

This will prompt you to select from predefined trigger scenarios or enter a custom one.

### 3. Using the main application with natural language queries

```bash
python3 main.py
```

Then enter an enhancement request in natural language:

```
You: Enhance FAS 10 to address challenges with intangible digital assets like software development.
```

## Test Cases

The system includes three predefined test cases for standards enhancement:

1. **Digital Assets in Istisna'a (FAS 10)**
   - Scenario: A financial institution wants to structure an Istisna'a contract for AI software development
   - Challenge: Applying FAS 10's concepts of "well-defined subject matter" to evolving digital assets

2. **Tokenized Mudarabah Investments (FAS 4)**
   - Scenario: Fintech platforms offering tokenized Mudarabah funds on blockchain networks
   - Challenge: Handling digital representations of investment units and real-time trading

3. **Green Sukuk Environmental Impact (FAS 32)**
   - Scenario: Islamic institutions issuing 'Green Sukuk' for sustainable projects
   - Challenge: Accounting for and reporting environmental impact metrics alongside financial returns

## Expected Output

For each enhancement process, the system produces:

1. **Review Findings**: Analysis of the standard's current state and identified issues
2. **Proposed Enhancements**: Specific textual changes with clear rationale
3. **Visual Diff**: A text-based diff showing what changed between original and proposed text
4. **Validation Results**: Assessment of Shariah compliance, consistency, and implementation practicality

## Extending the System

To add new test cases:

1. Edit `enhancement.py` and add new scenarios to the `ENHANCEMENT_TEST_CASES` list:
   ```python
   {
       "name": "Your New Test Case",
       "standard_id": "4",  # Choose from 4, 7, 10, 28, 32
       "trigger_scenario": """Detailed description of the scenario that requires 
                            standards enhancement..."""
   }
   ```

To extend the Shariah principles knowledge base:

1. Edit `shariah_principles.py` to add new principles or modify existing ones
2. For new standards, add a new list like `FAS_X_PRINCIPLES` and update the `STANDARD_PRINCIPLES` dictionary

## Troubleshooting

Common issues:

1. **Module not found errors**: Ensure all dependencies are installed via `pip install -r requirements.txt`

2. **API key errors**: Check that your `.env` file contains the correct API key

3. **Vector database issues**: If the retriever fails, check that the vector database was properly built and exists in `vector_db_storage/`

4. **Low-quality results**: Try refining the trigger scenario with more specific language and details about the Islamic finance context

## Architecture

The enhancement feature follows this workflow:

1. **User input** → Input is processed to extract standard ID and trigger scenario
2. **Reviewer Agent** → Analyzes standard and identifies enhancement areas
3. **Proposer Agent** → Generates specific text changes with rationale
4. **Validator Agent** → Validates changes against Shariah principles
5. **Result formatting** → Combines all outputs into a structured report with diff visualization

The agents communicate through a state-based graph architecture managed by LangGraph. Each agent's output becomes input for the next agent, creating a coordinated workflow.

## Examples

### Example Output

```
# Standards Enhancement Results for FAS 10

## Trigger Scenario
A financial institution wants to structure an Istisna'a contract for the development of a large-scale AI software platform...

## Review Findings
The review of FAS 10 identified the following areas that need enhancement:

1. Definition of "Subject Matter" - The current definition focuses on physical goods...

## Proposed Enhancements
Original text:
The subject matter of the Istisna'a must be precisely specified in terms of its kind, type, quantity, and quality...

Proposed text:
The subject matter of the Istisna'a must be precisely specified in terms of its kind, type, quantity, and quality, with consideration for the nature of the asset...

Rationale:
This enhancement clarifies how the principle of "precise specification" applies differently to intangible assets...

## Visual Diff of Changes
```diff
--- Original
+++ Proposed
@@ -1 +1,3 @@
-The subject matter of the Istisna'a must be precisely specified in terms of its kind, type, quantity, and quality...
+The subject matter of the Istisna'a must be precisely specified in terms of its kind, type, quantity, and quality, with consideration for the nature of the asset. For tangible assets, full specifications must be provided. For intangible assets like software development, the subject matter may be defined through comprehensive functional requirements, milestones, and acceptance criteria...
```

## Validation Results
Shariah Compliance Assessment:
APPROVED - The proposed changes maintain compliance with the principle of minimizing Gharar...
```

## Implementation Details

### Multi-Agent Architecture

The Standards Enhancement feature is built on a multi-agent architecture with three specialized agents:

1. **Reviewer Agent** (`ReviewerAgent` in `agents.py`)
   - Analyzes standards content retrieved from the vector database
   - Identifies potential gaps, ambiguities, or inconsistencies
   - Extracts relevant sections for enhancement

2. **Proposer Agent** (`ProposerAgent` in `agents.py`)
   - Receives analysis from the Reviewer Agent
   - Generates specific textual enhancements
   - Provides rationale for each proposed change

3. **Validator Agent** (`ValidatorAgent` in `agents.py`)
   - Validates proposed changes against Shariah principles
   - Checks for internal consistency
   - Ensures practical implementability
   - Provides clear approval/rejection with reasoning

### Key Files

- `agents.py`: Contains all agent definitions including the three enhancement agents
- `enhancement.py`: Main workflow for the enhancement process
- `standards_enhancement_demo.py`: CLI interface for running enhancement demos
- `shariah_principles.py`: Knowledge base of Shariah principles for validation
- `visualize.py`: Utilities for visualizing differences between original and enhanced text
- `agent_graph.py`: Defines the agent interaction workflow

### Workflow Steps

1. **Input Processing**: Extract standard ID and trigger scenario
2. **Review Phase**: Reviewer Agent extracts and analyzes standard content
3. **Proposal Phase**: Proposer Agent generates specific text changes
4. **Validation Phase**: Validator Agent checks against Shariah principles
5. **Output Formatting**: Results are formatted with visual diffs

## Use Cases

The Standards Enhancement feature is designed for:

1. **Standards Committees**: To help identify and address gaps in existing standards
2. **Islamic Financial Institutions**: To propose enhancements based on practical challenges
3. **Researchers and Educators**: To explore how standards might evolve to address emerging issues
4. **Regulators**: To evaluate potential improvements to regulatory frameworks

## Future Enhancements

Potential improvements to the Standards Enhancement feature:

1. **Cross-standard Analysis**: Evaluate consistency and alignment across multiple standards
2. **Historical Context**: Add awareness of the historical development of standards
3. **Global Comparison**: Compare AAOIFI standards with other global standards (IFRS, etc.)
4. **Impact Assessment**: Evaluate potential impact of changes on financial reporting
5. **Collaborative Editing**: Allow multiple users to contribute to the enhancement process 