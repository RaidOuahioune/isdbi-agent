"""
Utility functions for the Islamic Finance standards system.

This module contains common utility functions that may be used across multiple components.
"""

def format_journal_entry(entry):
    """Format a journal entry dictionary into a readable string."""
    return f"Dr. {entry['debit_account']} ${entry['amount']}\n" \
           f"Cr. {entry['credit_account']} ${entry['amount']}"

def extract_standard_id(text):
    """Extract standard ID from text mention."""
    import re
    match = re.search(r"FAS\s+(\d+)", text)
    if match:
        return match.group(1)
    return None

def chunk_text(text, chunk_size=1000, overlap=200):
    """Split text into chunks of specified size with overlap."""
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunks.append(text[i:i + chunk_size])
        if i + chunk_size >= len(text):
            break
    return chunks