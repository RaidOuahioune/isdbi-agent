from neo4j import GraphDatabase
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# === CONFIG ===
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASS = "yourStrongPassword123"
VECTOR_INDEX_NAME = "standardClauseVectorIndex"  # <-- changed

# === Initialize embedding model ===
EMBED_MODEL_NAME = "BAAI/bge-large-en-v1.5"
embed_model = HuggingFaceEmbedding(model_name=EMBED_MODEL_NAME)

def query_standard_clauses(query_text, top_k=5):
    print(f"🔍 Embedding query for standards: '{query_text}'")
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
