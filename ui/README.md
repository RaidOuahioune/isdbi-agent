# AAOIFI Standards Enhancement UI

This directory contains the UI components for the AAOIFI Standards Enhancement System. The application visualizes the output of an AI-powered system that analyzes and proposes enhancements to Islamic Finance standards.

## Available Applications

### 1. Main Application (`app.py`)

The full-featured application that integrates with the enhancement system. Use this when you want to:
- Run actual enhancement processes with the AI agents
- Save and view past enhancements
- Export results in different formats

```bash
streamlit run ui/app.py
```

### 2. Simple Demo Application (`app_simple.py`)

A lightweight demo version that simulates the enhancement process using pre-generated output files. Use this when you want to:
- Demonstrate the UI without running the actual AI agents
- Test the parsing functionality with different output formats
- Show the application to users without deploying the full system

```bash
streamlit run ui/app_simple.py
```

## Key Components

### Output Parser (`output_parser.py`)

A robust parser for processing enhancement results with the following features:

- **Section Extraction**: Extracts the main sections from output (trigger scenario, review findings, proposed enhancements, validation results)
- **Original/Proposed Text Extraction**: Identifies the original text and proposed enhancements from the proposal section
- **Fallback Mechanisms**: Multiple parsing strategies to handle various output formats
- **Diff Generation**: Creates visually appealing diffs between original and proposed text

Usage example:
```python
from output_parser import OutputParser

# Parse sections from markdown output
with open("output_file.txt", "r") as f:
    output_text = f.read()
    
results = OutputParser.parse_markdown_sections(output_text)

# Extract original and proposed text
original, proposed = OutputParser.extract_original_and_proposed(results["proposal"])

# Generate a diff
diff_text = OutputParser.format_text_diff(original, proposed)

# Format diff as HTML
html_diff = OutputParser.format_diff_html(diff_text)
```

### Category Configuration (`category_config.py`)

Defines the categories and test cases for the enhancement system:

- Categories for different types of standards
- Test cases with example scenarios
- Helper functions for filtering test cases by category

### Progress Monitor (`progress_monitor.py`)

Provides real-time progress updates during the enhancement process:

- Visual progress indicators
- Phase-based updates
- Detailed step tracking

## Integration with Enhancement System

The UI integrates with the main enhancement system through:

1. The `run_standards_enhancement` function from `enhancement.py`
2. The `run_enhancement_with_monitoring` function for progress tracking
3. The `OutputParser` class for processing results

## Customization

### Adding New Categories

To add a new category, update `category_config.py`:

```python
# Add to ENHANCEMENT_CATEGORIES
ENHANCEMENT_CATEGORIES["category4"] = "New Category Name"

# Add test cases
ENHANCEMENT_TEST_CASES.append({
    "name": "New Test Case",
    "standard_id": "XX",
    "category": "category4",
    "output_file": "category4_agent_output.txt",
    "trigger_scenario": """Description of the scenario..."""
})
```

### Extending the Parser

To handle new output formats, extend the `OutputParser` class in `output_parser.py`:

```python
@staticmethod
def parse_custom_format(output_text):
    """Parse a custom output format"""
    # Implement custom parsing logic
    return parsed_sections
``` 