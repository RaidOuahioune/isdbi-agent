import textwrap

from llama_index.embeddings.huggingface import HuggingFaceEmbedding # New import

# === Existing Query Function ===
from neo4j import GraphDatabase

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASS = "yourStrongPassword123"
VECTOR_INDEX_NAME = "lawClauseVectorIndex"
# It's a larger model, so initialization might take a moment.
EMBEDDING_MODEL_NAME = "BAAI/bge-large-en-v1.5"

embed_model = HuggingFaceEmbedding(model_name=EMBEDDING_MODEL_NAME)
def query_law_clauses(query_text, top_k=2):
    print(f"🔍 Embedding query: '{query_text}'")
    query_vector = embed_model.get_text_embedding(query_text)

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
    results = []

    with driver.session() as session:
        cypher = f"""
        CALL db.index.vector.queryNodes($index_name, $top_k, $query_vector)
        YIELD node, score
        RETURN node.id AS id, node.text AS text, score
        ORDER BY score DESC
        """
        records = session.run(
            cypher,
            index_name=VECTOR_INDEX_NAME,
            top_k=top_k,
            query_vector=query_vector
        )
        for record in records:
            results.append({
                "id": record["id"],
                "score": round(record["score"], 4),
                "text": record["text"]
            })

    return results

# === Updated Compliance Function ===
def ask_compliance_question_law(question, llm, top_k=5):
    # Step 1: Retrieve top-k law clauses using external query function
    context_nodes = query_law_clauses(question, top_k=top_k)


    if not context_nodes:
        return "❗ No relevant legal clauses were found to answer this question."

    # Step 2: Format retrieved clauses for prompt
    context_text = "\n\n".join(
        f"[{node['id']} - score {node['score']}]\n{textwrap.fill(node['text'], 100)}"
        for node in context_nodes
    )

    # Step 3: Build LLM prompt
    prompt = f"""You are a legal compliance assistant knowledgeable in algerian law.
The user asked: "{question}"

Based on the following law clauses, answer clearly and cite them if relevant:

--- START OF LAW CLAUSES ---
{context_text}
--- END OF LAW CLAUSES ---

🧠 Answer:"""

    # Step 4: Use Gemini to answer
    response = llm.complete(prompt)
    return response.text.strip()
