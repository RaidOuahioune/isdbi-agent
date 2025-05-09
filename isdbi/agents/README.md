# AAOIFI Standards Enhancement System

An AI-powered system for reviewing, proposing, and validating enhancements to Islamic Finance standards using a multi-agent architecture.

## Overview

The Standards Enhancement feature is a specialized multi-agent system designed to help improve AAOIFI Financial Accounting Standards (FAS) by identifying areas for enhancement, proposing specific changes, and validating those changes against Shariah principles.

The system uses three specialized AI agents working together in a coordinated workflow:

1. **Reviewer Agent**: Analyzes standards and identifies potential gaps, ambiguities, or areas for improvement
2. **Proposer Agent**: Generates specific text changes to address the identified issues
3. **Validator Agent**: Validates the proposed changes against Shariah principles and standards consistency

## Features

- Comprehensive analysis of Islamic Finance standards
- AI-generated enhancement proposals with rationale
- Validation against Shariah principles
- Visual diff comparisons of original and proposed text changes
- Export options for results (Markdown and HTML)
- Historical database of past enhancements
- Streamlit web interface with progress monitoring

## Installation

### Requirements

- Python 3.9+
- Access to Google's Gemini API (API key required)

### Setup

1. **Clone the repository**

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

## Usage

There are three ways to use the Standards Enhancement feature:

### 1. Web Interface (Streamlit)

The easiest way to use the system is via the Streamlit web interface:

```bash
cd ui
streamlit run app.py
```

This will open a web browser with the interactive interface where you can:
- Select from predefined test cases
- Create custom enhancement scenarios
- View the results with interactive visualizations
- Export results as Markdown or HTML
- Browse past enhancements

### 2. Command Line Demo

For a simpler command-line demonstration:

```bash
python standards_enhancement_demo.py
```

Options:
- `--test-case INDEX`: Run a specific test case by index (0, 1, 2, etc.)
- `--custom`: Run with custom input parameters
- `--all`: Run all test cases sequentially

### 3. Programmatic Usage

You can also use the enhancement system programmatically in your own Python code:

```python
from enhancement import run_standards_enhancement

# Run an enhancement process
results = run_standards_enhancement(
    standard_id="10",  # FAS 10 (Istisna'a)
    trigger_scenario="Your trigger scenario here...",
    progress_callback=None  # Optional callback for progress updates
)

# Display or process the results
print(results['review'])
print(results['proposal'])
print(results['validation'])
```

## Test Cases

The system includes several predefined test cases for standards enhancement:

1. **Digital Assets in Istisna'a (FAS 10)**
   - Scenario: A financial institution wants to structure an Istisna'a contract for AI software development
   - Challenge: Applying FAS 10's concepts of "well-defined subject matter" to evolving digital assets

2. **Tokenized Mudarabah Investments (FAS 4)**
   - Scenario: Fintech platforms offering tokenized Mudarabah funds on blockchain networks
   - Challenge: Handling digital representations of investment units and real-time trading

3. **Green Sukuk Environmental Impact (FAS 32)**
   - Scenario: Islamic institutions issuing 'Green Sukuk' for sustainable projects
   - Challenge: Accounting for and reporting environmental impact metrics alongside financial returns

4. **Digital Banking Services in Ijarah (FAS 28)**
   - Scenario: Islamic banks offering digital banking services through cloud infrastructure
   - Challenge: Classifying and measuring digital service agreements with mixed components

5. **Cryptocurrency Zakat Calculation (FAS 7)**
   - Scenario: Calculating Zakat on volatile cryptocurrency assets
   - Challenge: Addressing value fluctuations specific to digital assets

## Project Structure

- `agents.py`: Specialized agents for reviewing, proposing, and validating
- `enhancement.py`: Main enhancement workflow
- `visualize.py`: Text comparison and visualization utilities
- `shariah_principles.py`: Knowledge base of Shariah principles
- `agent_graph.py`: Agent coordination and workflow
- `ui/app.py`: Streamlit web interface
- `ui/progress_monitor.py`: Real-time progress monitoring
- `standards_enhancement_demo.py`: Command-line demo
- `past_enhancements/`: Database of saved enhancements

## Contributing

We welcome contributions to enhance this system! Some areas for potential improvement:

1. **Cross-standard Analysis**: Evaluate consistency across multiple standards
2. **Impact Assessment**: Evaluate potential impact of changes on financial reporting
3. **User Feedback Loop**: Allow user feedback to improve proposals
4. **Enhanced Visualization**: More advanced visualization of proposed changes
5. **Integration with Knowledge Bases**: Incorporate more Islamic finance resources

## License

[Specify your license here]

## Acknowledgments

- AAOIFI for their comprehensive Islamic Finance standards
- LangChain and LangGraph for agent coordination
- Google Gemini for AI capabilities 