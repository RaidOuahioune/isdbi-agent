def enhance_query(question, llm):
    """
    Use the LLM to enhance the user's query to better match the style of Islamic texts.
    This helps bridge the vocabulary gap between modern questions and classical Islamic sources.
    
    Args:
        question (str): The original user query
        llm: The language model to use for enhancement
    
    Returns:
        str: An enhanced version of the query with Islamic terminology
    """
    
    prompt = f"""
You are a specialized Islamic query enhancer. Your task is to reformulate questions to better match the 
language and terminology used in Islamic texts like the Quran and Hadith.

Guidelines:
- Preserve the original meaning and intent of the question
- Add relevant Islamic terminology and concepts that might be in the sources
- Use classical expressions and phrases common in Islamic jurisprudence
- Include key Arabic terms where appropriate (with English translations)
- Make sure the enhanced query will help retrieve relevant passages from Islamic sources
- Keep the enhanced query concise (maximum 2-3 sentences)

Original question: {question}

Enhanced question for retrieval (make sure it's still focused on the main question):
"""

    response = llm.complete(prompt=prompt)
    enhanced_query = response.text.strip()
    
    # Fall back to original query if something goes wrong
    if not enhanced_query or len(enhanced_query) < len(question)/2:
        return question
        
    return enhanced_query
