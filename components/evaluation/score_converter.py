"""
Utility to convert between different scoring scales for the evaluation system.
"""

def convert_10_to_4_scale(score_10: float) -> int:
    """
    Convert a score on a 1-10 scale to the discrete 1-4 scale.
    
    Args:
        score_10: Score on 1-10 scale
        
    Returns:
        Equivalent score on 1-4 scale
    """
    if score_10 < 3.5:
        return 1  # Poor
    elif score_10 < 6.0:
        return 2  # Fair
    elif score_10 < 8.5:
        return 3  # Good
    else:
        return 4  # Excellent
        
def convert_4_to_10_scale(score_4: int) -> float:
    """
    Convert a score on the discrete 1-4 scale to the 1-10 scale.
    
    Args:
        score_4: Score on 1-4 scale
        
    Returns:
        Equivalent score on 1-10 scale
    """
    conversion = {
        1: 2.5,   # Poor -> 2.5/10
        2: 5.0,   # Fair -> 5.0/10
        3: 7.5,   # Good -> 7.5/10
        4: 9.5,   # Excellent -> 9.5/10
    }
    return conversion.get(score_4, 5.0)  # Default to middle score if invalid

def get_discrete_score_label(score: int) -> str:
    """
    Get the text label for a discrete score.
    
    Args:
        score: Score on 1-4 scale
        
    Returns:
        Text label for the score
    """
    labels = {
        1: "Poor",
        2: "Fair",
        3: "Good",
        4: "Excellent"
    }
    return labels.get(score, "Unknown")
