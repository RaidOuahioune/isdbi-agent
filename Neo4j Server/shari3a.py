from neo4j import GraphDatabase
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# Setup
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASS = "yourStrongPassword123"

EMBED_MODEL_NAME = "BAAI/bge-large-en-v1.5"
embed_model = HuggingFaceEmbedding(model_name=EMBED_MODEL_NAME)

def query_quran_verses(query_text, top_k=3):
    print(f"🔍 Embedding query for Quran verses: '{query_text}'")
    query_vector = embed_model.get_text_embedding(query_text)

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
    results = []

    with driver.session() as session:
        cypher = """
        CALL db.index.vector.queryNodes($index_name, $top_k, $query_vector)
        YIELD node, score
        RETURN node.unique_id AS id, node.content AS text, score
        ORDER BY score DESC
        """
        records = session.run(
            cypher,
            index_name="quran_verse_embeddings",
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


def query_hadiths(query_text, top_k=3):
    print(f"🔍 Embedding query for Hadith: '{query_text}'")
    query_vector = embed_model.get_text_embedding(query_text)

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
    results = []

    with driver.session() as session:
        cypher = """
        CALL db.index.vector.queryNodes($index_name, $top_k, $query_vector)
        YIELD node, score
        RETURN node.unique_id AS id, node.content AS text, score
        ORDER BY score DESC
        """
        records = session.run(
            cypher,
            index_name="hadith_embeddings",
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

def query_documents(query_text, top_k=3):
    print(f"🔍 Embedding query for document chunks: '{query_text}'")
    query_vector = embed_model.get_text_embedding(query_text)

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
    results = []

    with driver.session() as session:
        cypher = """
        CALL db.index.vector.queryNodes($index_name, $top_k, $query_vector)
        YIELD node, score
        RETURN node.id AS id, node.text AS text, score
        ORDER BY score DESC
        """
        records = session.run(
            cypher,
            index_name="document_chunk_embeddings",
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



def search_all_sources_by_text(query_text, top_k=3):
    all_results = []

    # Quran
    quran_results = query_quran_verses(query_text, top_k=top_k)
    for r in quran_results:
        r["source_type"] = "QuranVerse"
        all_results.append(r)

    # Hadith
    hadith_results = query_hadiths(query_text, top_k=top_k)
    for r in hadith_results:
        r["source_type"] = "Hadith"
        all_results.append(r)

    # Documents
    doc_results = query_documents(query_text, top_k=top_k)
    for r in doc_results:
        r["source_type"] = "DocumentChunk"
        all_results.append(r)

    # Sort by score descending
    all_results = sorted(all_results, key=lambda x: x["score"], reverse=True)

    return all_results
