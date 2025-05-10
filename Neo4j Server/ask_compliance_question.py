from query_enhancer import enhance_query

def ask_compliance_question(question, uploader, llm, top_k=6):
    # First enhance the query to better match Islamic text style
    enhanced_question = enhance_query(question, llm)
    print(f"\n--- Original Question ---\n{question}")
    print(f"\n--- Enhanced Question ---\n{enhanced_question}")
    
    # Use the enhanced question for retrieval
    results = uploader.search_all_sources_by_text(enhanced_question, top_k=top_k)

    print("\n--- Retrieved Chunks ---")
    context_blocks = []
    refs = {"Hadith": [], "QuranVerse": [], "DocumentChunk": []}

    for i, result in enumerate(results):
        source = result.get("source_type")
        content = result.get("text_content", "")
        # print(f"\nChunk {i+1} ({source}):\n{content[:300]}...\n")

        # Accumulate context
        context_blocks.append(content)

        # Track references
        if source == "Hadith":
            refs["Hadith"].append(result.get("unique_id"))
        elif source == "QuranVerse":
            refs["QuranVerse"].append(result.get("unique_id"))
        elif source == "DocumentChunk":
            refs["DocumentChunk"].append(f"{result.get('source_document_name')} (Page {result.get('page_number')})")

    # Include both the original and enhanced questions in the prompt
    prompt = "\n".join(context_blocks) + f"\n\nOriginal Question: {question}\nEnhanced Question: {enhanced_question}\n\nAnswer with reference to Islamic jurisprudence and mention any related Hadiths or Quranic verses if present. Make sure to address the original question directly."

    response = llm.complete(prompt=prompt)

    # Attach references
    response_text = response.text.strip()
    response_text += "\n\nReferences:\n"
    if refs["QuranVerse"]:
        response_text += "- Quran Verses: " + ", ".join(refs["QuranVerse"]) + "\n"
    if refs["Hadith"]:
        response_text += "- Hadiths: " + ", ".join(refs["Hadith"]) + "\n"
    if refs["DocumentChunk"]:
        response_text += "- FAS Document Chunks: " + ", ".join(refs["DocumentChunk"]) + "\n"

    return response_text

