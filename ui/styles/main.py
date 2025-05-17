"""
Main CSS styles for the Streamlit application.
"""

def load_css():
    """Return the CSS styles for the application."""
    return """
<style>
    .main {
        background-color: #f5f7f9;
    }
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 1rem;
    }
    .stMarkdown h1 {
        color: #1e3a8a;
    }
    .stMarkdown h2 {
        color: #2563eb;
        padding-top: 0.5rem;
    }
    .stMarkdown h3 {
        color: #3b82f6;
    }
    .review-container {
        background-color: #f0f9ff;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #3b82f6;
        margin-bottom: 1rem;
    }
    .proposal-container {
        background-color: #f0fdf4;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #22c55e;
        margin-bottom: 1rem;
    }
    .validation-container {
        background-color: #fff7ed;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #f59e0b;
        margin-bottom: 1rem;
    }
    .diff-container {
        font-family: monospace;
        white-space: pre-wrap;
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        padding: 1rem;
        border-radius: 0.5rem;
        overflow-x: auto;
    }
    .addition {
        background-color: #dcfce7;
        color: #166534;
        display: inline;
        border-radius: 3px;
        padding: 0 2px;
    }
    .deletion {
        background-color: #fee2e2;
        color: #991b1b;
        display: inline;
        border-radius: 3px;
        padding: 0 2px;
    }
    .diff-stats {
        display: flex;
        justify-content: space-between;
        margin-bottom: 1rem;
        background-color: #f1f5f9;
        padding: 0.75rem;
        border-radius: 0.5rem;
    }
    .diff-stat-item {
        text-align: center;
        padding: 0 0.5rem;
    }
    .diff-stat-value {
        font-size: 1.25rem;
        font-weight: bold;
    }
    .diff-stat-label {
        font-size: 0.875rem;
        color: #64748b;
    }
    .diff-header {
        font-weight: bold;
        color: #64748b;
        margin-bottom: 0.5rem;
    }
    .diff-tabs {
        margin-bottom: 1rem;
    }
    .loading-text {
        color: #4b5563;
        font-style: italic;
    }
    .result-container {
        margin-top: 2rem;
        padding: 1rem;
        background-color: white;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    .export-button {
        margin-top: 1rem;
    }
    .past-enhancement {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 5px solid #6366f1;
    }
    .cross-standard-container {
        background-color: #eef2ff;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #818cf8;
        margin-bottom: 1rem;
    }
    .compatibility-table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
        font-family: Arial, sans-serif;
    }
    .compatibility-table th {
        background-color: #f1f5f9;
        padding: 12px 15px;
        text-align: left;
        border: 1px solid #e2e8f0;
    }
    .compatibility-table td {
        padding: 12px 15px;
        border: 1px solid #e2e8f0;
    }
    .impact-high {
        font-weight: bold;
        color: #dc2626;
    }
    .impact-medium {
        font-weight: bold;
        color: #d97706;
    }
    .impact-low {
        font-weight: bold;
        color: #059669;
    }
    .impact-none {
        color: #6b7280;
    }
    .contradiction {
        background-color: #fee2e2;
    }
    .synergy {
        background-color: #d1fae5;
    }
    .both {
        background-color: #fff7ed;
    }
    .none {
        background-color: #f3f4f6;
    }
</style>
"""

def get_enhancement_css():
    """Get CSS styles for enhancement results display."""
    return """
    <style>
        /* Enhancement Area Styling */
        .enhancement-area {
            background-color: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 0.5rem;
            padding: 1rem;
            margin-bottom: 1rem;
        }
        
        /* Proposal Section Styling */
        .proposal-section {
            background-color: #f0fdf4;
            border-left: 4px solid #22c55e;
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 0.5rem;
        }
        
        /* Validation Section Styling */
        .validation-section {
            background-color: #fff7ed;
            border-left: 4px solid #f59e0b;
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 0.5rem;
        }
        
        /* Enhancement Title Styling */
        .enhancement-title {
            font-size: 1.25rem;
            font-weight: bold;
            color: #0f172a;
            margin-bottom: 0.5rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #e2e8f0;
        }
        
        /* Analysis Section Styling */
        .analysis-section {
            background-color: #f0f9ff;
            border-left: 4px solid #3b82f6;
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 0.5rem;
        }
        
        /* Code Block Styling */
        pre {
            background-color: #f8fafc;
            padding: 1rem;
            border-radius: 0.5rem;
            font-family: 'Courier New', monospace;
            overflow-x: auto;
        }
    </style>
    """