import difflib
from typing import List, Tuple
import re
import html

def tokenize_text(text: str) -> List[str]:
    """
    Tokenize text into words and whitespace for more precise diff.
    
    Args:
        text: The input text to tokenize
        
    Returns:
        List of tokens (words and whitespace)
    """
    # Normalize line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # Split text into tokens (words, whitespace, and punctuation)
    tokens = []
    for line in text.split('\n'):
        if tokens:  # Add newline token if not the first line
            tokens.append('\n')
        
        # This regex keeps words, whitespace, and punctuation as separate tokens
        line_tokens = re.findall(r'(\s+|\w+|[^\s\w]+)', line)
        tokens.extend(line_tokens)
    
    return tokens

def generate_word_diff(text1: str, text2: str) -> Tuple[str, List[Tuple[str, str, str]]]:
    """
    Generate a word-by-word diff between two text strings.
    
    Args:
        text1: Original text
        text2: Modified text
        
    Returns:
        Tuple containing:
        - HTML string with highlighted differences
        - List of operations (tag, old text, new text) for detailed analysis
    """
    if not text1 and not text2:
        return "", []
    
    if not text1:
        return f'<span class="addition">{html.escape(text2)}</span>', [('add', '', text2)]
    
    if not text2:
        return f'<span class="deletion">{html.escape(text1)}</span>', [('del', text1, '')]
    
    # Tokenize both texts
    tokens1 = tokenize_text(text1)
    tokens2 = tokenize_text(text2)
    
    # Generate sequence matcher
    matcher = difflib.SequenceMatcher(None, tokens1, tokens2)
    
    # Get operations
    operations = []
    html_diff = []
    
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        # Get the relevant text segments
        text1_segment = ''.join(tokens1[i1:i2])
        text2_segment = ''.join(tokens2[j1:j2])
        
        # Store operation details
        operations.append((tag, text1_segment, text2_segment))
        
        # Add HTML formatting based on the operation type
        if tag == 'equal':
            html_diff.append(html.escape(text1_segment))
        elif tag == 'delete':
            html_diff.append(f'<span class="deletion">{html.escape(text1_segment)}</span>')
        elif tag == 'insert':
            html_diff.append(f'<span class="addition">{html.escape(text2_segment)}</span>')
        elif tag == 'replace':
            html_diff.append(f'<span class="deletion">{html.escape(text1_segment)}</span>')
            html_diff.append(f'<span class="addition">{html.escape(text2_segment)}</span>')
    
    return ''.join(html_diff), operations

def generate_inline_word_diff(text1: str, text2: str) -> str:
    """
    Generate an inline word-by-word diff that shows deletions and additions in-place.
    
    Args:
        text1: Original text
        text2: Modified text
        
    Returns:
        HTML string with inline highlighted differences
    """
    if not text1 and not text2:
        return ""
    
    if not text1:
        return f'<span class="addition">{html.escape(text2)}</span>'
    
    if not text2:
        return f'<span class="deletion">{html.escape(text1)}</span>'
    
    # Tokenize both texts
    tokens1 = tokenize_text(text1)
    tokens2 = tokenize_text(text2)
    
    # Generate sequence matcher
    matcher = difflib.SequenceMatcher(None, tokens1, tokens2)
    
    # Generate inline diff
    html_diff = []
    
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        # Get the relevant text segments
        text1_segment = ''.join(tokens1[i1:i2])
        text2_segment = ''.join(tokens2[j1:j2])
        
        # Add HTML formatting based on the operation type
        if tag == 'equal':
            html_diff.append(html.escape(text1_segment))
        elif tag == 'delete':
            html_diff.append(f'<span class="deletion">{html.escape(text1_segment)}</span>')
        elif tag == 'insert':
            html_diff.append(f'<span class="addition">{html.escape(text2_segment)}</span>')
        elif tag == 'replace':
            # For replacements, try to do a character-level diff for short segments
            if len(text1_segment) < 100 and len(text2_segment) < 100:
                char_matcher = difflib.SequenceMatcher(None, text1_segment, text2_segment)
                for c_tag, c_i1, c_i2, c_j1, c_j2 in char_matcher.get_opcodes():
                    if c_tag == 'equal':
                        html_diff.append(html.escape(text1_segment[c_i1:c_i2]))
                    elif c_tag == 'delete':
                        html_diff.append(f'<span class="deletion">{html.escape(text1_segment[c_i1:c_i2])}</span>')
                    elif c_tag == 'insert':
                        html_diff.append(f'<span class="addition">{html.escape(text2_segment[c_j1:c_j2])}</span>')
                    elif c_tag == 'replace':
                        html_diff.append(f'<span class="deletion">{html.escape(text1_segment[c_i1:c_i2])}</span>')
                        html_diff.append(f'<span class="addition">{html.escape(text2_segment[c_j1:c_j2])}</span>')
            else:
                html_diff.append(f'<span class="deletion">{html.escape(text1_segment)}</span>')
                html_diff.append(f'<span class="addition">{html.escape(text2_segment)}</span>')
    
    return ''.join(html_diff)

def generate_sentence_diff(text1: str, text2: str) -> str:
    """
    Generate a sentence-by-sentence diff for longer text.
    
    Args:
        text1: Original text
        text2: Modified text
        
    Returns:
        HTML string with sentence-level diff
    """
    # Split texts into sentences
    sentences1 = re.split(r'(?<=[.!?])\s+', text1)
    sentences2 = re.split(r'(?<=[.!?])\s+', text2)
    
    # Use SequenceMatcher to find similarities
    matcher = difflib.SequenceMatcher(None, sentences1, sentences2)
    
    # Generate HTML diff
    html_diff = []
    
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            for sentence in sentences1[i1:i2]:
                html_diff.append(html.escape(sentence) + ' ')
        elif tag == 'delete':
            for sentence in sentences1[i1:i2]:
                html_diff.append(f'<span class="deletion">{html.escape(sentence)}</span> ')
        elif tag == 'insert':
            for sentence in sentences2[j1:j2]:
                html_diff.append(f'<span class="addition">{html.escape(sentence)}</span> ')
        elif tag == 'replace':
            for sentence in sentences1[i1:i2]:
                html_diff.append(f'<span class="deletion">{html.escape(sentence)}</span> ')
            for sentence in sentences2[j1:j2]:
                html_diff.append(f'<span class="addition">{html.escape(sentence)}</span> ')
    
    return ''.join(html_diff)

def generate_complete_diff(original_text: str, proposed_text: str) -> dict:
    """
    Generate comprehensive diff analysis between original and proposed text.
    
    Args:
        original_text: The original standard text
        proposed_text: The proposed enhancement text
        
    Returns:
        Dictionary with different diff formats and analysis
    """
    # Clean the input texts
    original_text = original_text.strip() if original_text else ""
    proposed_text = proposed_text.strip() if proposed_text else ""
    
    # Generate different diff formats
    word_diff_html, operations = generate_word_diff(original_text, proposed_text)
    inline_diff_html = generate_inline_word_diff(original_text, proposed_text)
    sentence_diff_html = generate_sentence_diff(original_text, proposed_text)
    
    # Calculate some stats
    words_added = sum(len(re.findall(r'\w+', new)) for tag, old, new in operations if tag in ['insert', 'replace'])
    words_deleted = sum(len(re.findall(r'\w+', old)) for tag, old, new in operations if tag in ['delete', 'replace'])
    words_unchanged = sum(len(re.findall(r'\w+', old)) for tag, old, new in operations if tag == 'equal')
    
    # Analyze the type of changes
    change_summary = []
    if words_added > 0 and words_deleted == 0:
        change_summary.append("Text additions only")
    elif words_deleted > 0 and words_added == 0:
        change_summary.append("Text removals only")
    elif words_added > 0 and words_deleted > 0:
        change_summary.append("Text replacements")
    
    if words_unchanged == 0:
        change_summary.append("Complete rewrite")
    elif words_unchanged > 0 and (words_added > 0 or words_deleted > 0):
        percent_changed = (words_added + words_deleted) / (words_unchanged + words_deleted) * 100
        if percent_changed < 10:
            change_summary.append("Minor edits")
        elif percent_changed < 30:
            change_summary.append("Moderate changes")
        else:
            change_summary.append("Major changes")
    
    # Return comprehensive results
    return {
        "word_diff_html": word_diff_html,
        "inline_diff_html": inline_diff_html,
        "sentence_diff_html": sentence_diff_html,
        "stats": {
            "words_added": words_added,
            "words_deleted": words_deleted,
            "words_unchanged": words_unchanged,
            "total_words_original": words_unchanged + words_deleted,
            "total_words_proposed": words_unchanged + words_added,
            "percent_changed": (words_added + words_deleted) / max(1, words_unchanged + words_deleted) * 100
        },
        "change_summary": ", ".join(change_summary)
    } 