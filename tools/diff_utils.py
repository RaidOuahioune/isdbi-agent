import difflib
import re
from typing import Dict, Any
from ui.word_diff import generate_complete_diff

def analyze_text_differences(text1: str, text2: str) -> Dict[str, Any]:
    """
    Performs detailed analysis of differences between two texts.
    Args:
        text1: First text (AI proposed text)
        text2: Second text (Committee edited text)
    Returns:
        Dict containing difference analysis, including:
        - similarity_ratio: float representing how similar the texts are (0.0 to 1.0)
        - diff_lines: list of lines showing differences with +/- markers
        - word_changes: summary of words added/removed/changed
        - is_identical: boolean indicating if texts are identical
        - complete_diff: output from generate_complete_diff
        - stats, change_summary, phrase_substitutions
    """
    similarity = difflib.SequenceMatcher(None, text1, text2).ratio()
    diff_lines = list(difflib.unified_diff(
        text1.splitlines(),
        text2.splitlines(),
        lineterm='',
        n=2
    ))
    text1_words = text1.split()
    text2_words = text2.split()
    s = difflib.SequenceMatcher(None, text1_words, text2_words)
    added_words = []
    removed_words = []
    changed_pairs = []
    for tag, i1, i2, j1, j2 in s.get_opcodes():
        if tag == 'replace':
            changed_pairs.append((' '.join(text1_words[i1:i2]), ' '.join(text2_words[j1:j2])))
        elif tag == 'delete':
            removed_words.append(' '.join(text1_words[i1:i2]))
        elif tag == 'insert':
            added_words.append(' '.join(text2_words[j1:j2]))
    char_level_diffs = []
    if similarity > 0.95:
        for i, (old, new) in enumerate(changed_pairs):
            if len(old) < 50 and len(new) < 50:
                s_chars = difflib.SequenceMatcher(None, old, new)
                char_diff = []
                for tag, i1, i2, j1, j2 in s_chars.get_opcodes():
                    if tag == 'equal':
                        char_diff.append(old[i1:i2])
                    elif tag == 'replace':
                        char_diff.append(f"[{old[i1:i2]} → {new[j1:j2]}]")
                    elif tag == 'delete':
                        char_diff.append(f"[-{old[i1:i2]}]")
                    elif tag == 'insert':
                        char_diff.append(f"[+{new[j1:j2]}]")
                char_level_diffs.append(''.join(char_diff))
    complete_diff = generate_complete_diff(text1, text2)
    words_added = sum(len(re.findall(r'\w+', new)) for new in added_words)
    words_added += sum(len(new.split()) for _, new in changed_pairs)
    words_deleted = sum(len(re.findall(r'\w+', old)) for old in removed_words)
    words_deleted += sum(len(old.split()) for old, _ in changed_pairs)
    words_unchanged = 0
    for tag, i1, i2, j1, j2 in s.get_opcodes():
        if tag == 'equal':
            words_unchanged += (i2 - i1)
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
        percent_changed = (words_added + words_deleted) / max(1, words_unchanged + words_deleted) * 100
        if percent_changed < 10:
            change_summary.append("Minor edits")
        elif percent_changed < 30:
            change_summary.append("Moderate changes")
        else:
            change_summary.append("Major changes")
    phrase_substitutions = []
    for old, new in changed_pairs:
        if len(old.split()) > 3 and len(new.split()) > 3:
            old_clean = re.sub(r'[^\w\s]', '', old.lower())
            new_clean = re.sub(r'[^\w\s]', '', new.lower())
            if difflib.SequenceMatcher(None, old_clean, new_clean).ratio() > 0.5:
                phrase_substitutions.append((old, new))
    return {
        "similarity_ratio": similarity,
        "is_identical": similarity == 1.0,
        "diff_lines": diff_lines,
        "word_changes": {
            "added": added_words,
            "removed": removed_words,
            "changed": changed_pairs
        },
        "char_level_diffs": char_level_diffs,
        "complete_diff": complete_diff,
        "stats": {
            "words_added": words_added,
            "words_deleted": words_deleted,
            "words_unchanged": words_unchanged,
            "total_words_original": words_unchanged + words_deleted,
            "total_words_proposed": words_unchanged + words_added,
            "percent_changed": (words_added + words_deleted) / max(1, words_unchanged + words_deleted) * 100
        },
        "change_summary": ", ".join(change_summary),
        "phrase_substitutions": phrase_substitutions
    }

def format_difference_details(diff_analysis: Dict[str, Any]) -> str:
    similarity = diff_analysis["similarity_ratio"]
    if diff_analysis["is_identical"]:
        return "IMPORTANT: The committee text is identical to the AI proposed text (100% match). No changes were made."
    parts = [f"Similarity: {similarity:.2%}"]
    if "stats" in diff_analysis:
        stats = diff_analysis["stats"]
        parts.append("\nChange Statistics:")
        parts.append(f"- Words added: {stats.get('words_added', 0)}")
        parts.append(f"- Words deleted: {stats.get('words_deleted', 0)}")
        parts.append(f"- Words unchanged: {stats.get('words_unchanged', 0)}")
        parts.append(f"- Percent changed: {stats.get('percent_changed', 0):.1f}%")
    if "change_summary" in diff_analysis:
        parts.append(f"\nChange Summary: {diff_analysis['change_summary']}")
    word_changes = diff_analysis["word_changes"]
    if word_changes["added"]:
        parts.append(f"\nWords/phrases added: {', '.join([f'\"{w}\"' for w in word_changes['added'][:5]])}")
        if len(word_changes["added"]) > 5:
            parts.append(f"...and {len(word_changes['added']) - 5} more additions")
    if word_changes["removed"]:
        parts.append(f"\nWords/phrases removed: {', '.join([f'\"{w}\"' for w in word_changes['removed'][:5]])}")
        if len(word_changes["removed"]) > 5:
            parts.append(f"...and {len(word_changes['removed']) - 5} more removals")
    if word_changes["changed"]:
        changes = [f'\"{before}\" → \"{after}\"' for before, after in word_changes["changed"][:5]]
        parts.append(f"\nWords/phrases changed: {'; '.join(changes)}")
        if len(word_changes["changed"]) > 5:
            parts.append(f"...and {len(word_changes['changed']) - 5} more changes")
    if "phrase_substitutions" in diff_analysis and diff_analysis["phrase_substitutions"]:
        parts.append("\nPhrase substitutions (semantic changes):")
        for i, (old, new) in enumerate(diff_analysis["phrase_substitutions"][:3]):
            parts.append(f"{i+1}. \"{old}\" → \"{new}\"")
        if len(diff_analysis["phrase_substitutions"]) > 3:
            parts.append(f"...and {len(diff_analysis['phrase_substitutions']) - 3} more substitutions")
    if diff_analysis["char_level_diffs"]:
        parts.append("\nDetailed character changes:")
        for i, diff in enumerate(diff_analysis["char_level_diffs"][:5]):
            parts.append(f"{i+1}. {diff}")
        if len(diff_analysis["char_level_diffs"]) > 5:
            parts.append(f"...and {len(diff_analysis['char_level_diffs']) - 5} more character-level changes")
    if diff_analysis["diff_lines"]:
        parts.append("\nLine-by-line differences:")
        parts.append("\n".join(diff_analysis["diff_lines"][:10]))
        if len(diff_analysis["diff_lines"]) > 10:
            parts.append(f"... (plus {len(diff_analysis['diff_lines']) - 10} more diff lines)")
    parts.append("\nIMPORTANT: Focus your assessment on these specific differences between the AI proposal and committee edits.")
    parts.append("Pay special attention to subtle changes that might alter the meaning or Shariah compliance of the text.")
    return "\n".join(parts)
