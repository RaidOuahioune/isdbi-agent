from neo4j import GraphDatabase
import json
# from sentence_transformers import SentenceTransformer # Replaced by llama_index
from llama_index.embeddings.huggingface import HuggingFaceEmbedding # New import
import numpy as np
import re # For basic slugification
import time # For potential delays if needed

# --- Initialize Embedding Model (LlamaIndex HuggingFaceEmbedding) ---
# This model needs to be downloaded by llama_index the first time it's used.
# It's a larger model, so initialization might take a moment.
EMBEDDING_MODEL_NAME = "BAAI/bge-large-en-v1.5"
EMBEDDING_DIMENSIONS = 1024 # Critical for Neo4j Vector Index

class Neo4jUploader:
    def __init__(self, uri, user, password, embedding_model_name=EMBEDDING_MODEL_NAME):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        print(f"Initializing LlamaIndex HuggingFace embedding model: {embedding_model_name}...")
        try:
            self.embed_model = HuggingFaceEmbedding(model_name=embedding_model_name)
            print("Embedding model initialized successfully.")
        except Exception as e:
            print(f"Error initializing HuggingFaceEmbedding model: {e}")
            print("Please ensure the model name is correct and you have internet access for the first download.")
            print("You might need to install additional dependencies like 'pip install torch sentence-transformers'.")
            self.embed_model = None # Set to None if initialization fails
            raise # Re-raise the exception to stop execution if model is critical

    def close(self):
        if self.driver:
            self.driver.close()
            print("Neo4j connection closed.")

    def _run_query(self, query, parameters=None):
        try:
            with self.driver.session(database="neo4j") as session:
                result = session.run(query, parameters)
                return [record for record in result]
        except Exception as e:
            print(f"Error executing Cypher query: {e}")
            print(f"Query: {query}")
            print(f"Parameters: {parameters}")
            return []

    def generate_embedding(self, text):
        if not self.embed_model:
            print("Error: Embedding model not initialized. Cannot generate embedding.")
            return None
        if not text or not isinstance(text, str):
            # print(f"Warning: Cannot generate embedding for non-string or empty text: {text}")
            return None # Or handle as an error
        try:
            # LlamaIndex's HuggingFaceEmbedding typically returns a list of floats directly
            embedding_vector = self.embed_model.get_text_embedding(text)
            return embedding_vector # Should already be a list of floats
        except Exception as e:
            print(f"Error generating embedding for text '{text[:50]}...': {e}")
            return None

    def _basic_slugify(self, text_parts):
        slug = "-".join(str(part).strip() for part in text_parts if str(part).strip())
        slug = re.sub(r'[^\w\s-]', '', slug).strip().lower()
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug if slug else "unknown"

    # --- upload_quran_verses method (no change needed in its Cypher, only uses self.generate_embedding) ---
    def upload_quran_verses(self, quran_json_data):
        print("Starting Quran verse upload...")
        query_verse = """
        UNWIND keys($chapter_map) AS chapter_key
        UNWIND $chapter_map[chapter_key] AS verse_data
        MERGE (qv:QuranVerse {unique_id: 'Quran:' + verse_data.chapter + ':' + verse_data.verse})
        ON CREATE SET qv.chapter_number = toInteger(verse_data.chapter),
                      qv.verse_number = toInteger(verse_data.verse),
                      qv.text_english = verse_data.text,
                      qv.embedding = $embedding_map['Quran:' + verse_data.chapter + ':' + verse_data.verse]
        ON MATCH SET  qv.text_english = verse_data.text,
                      qv.embedding = $embedding_map['Quran:' + verse_data.chapter + ':' + verse_data.verse]
        RETURN count(qv) AS verses_processed
        """
        embedding_map = {}
        processed_count = 0
        if not quran_json_data:
            print("  No Quran data provided to upload_quran_verses.")
            return

        total_verses_to_embed = sum(len(verses) for verses in quran_json_data.values())
        print(f"  Generating embeddings for approximately {total_verses_to_embed} Quran verses...")

        for chapter_key, verses in quran_json_data.items():
            for verse in verses:
                unique_id = f"Quran:{verse['chapter']}:{verse['verse']}"
                embedding = self.generate_embedding(verse['text'])
                if embedding: # Only add if embedding was successful
                    embedding_map[unique_id] = embedding
                processed_count +=1
                if processed_count % 500 == 0 or processed_count == total_verses_to_embed:
                    print(f"    Generated embeddings for {processed_count}/{total_verses_to_embed} Quran verses...")

        if not embedding_map:
            print("  No embeddings were generated for Quran verses. Aborting upload for Quran.")
            return

        # Filter quran_json_data to only include verses for which embeddings were generated
        filtered_quran_data = {}
        for chapter_key, verses in quran_json_data.items():
            filtered_verses = []
            for verse in verses:
                unique_id = f"Quran:{verse['chapter']}:{verse['verse']}"
                if unique_id in embedding_map:
                    filtered_verses.append(verse)
            if filtered_verses:
                filtered_quran_data[chapter_key] = filtered_verses
        if not filtered_quran_data:
            print("  No Quran verses with successful embeddings to upload.")
            return

        result = self._run_query(query_verse, parameters={"chapter_map": filtered_quran_data, "embedding_map": embedding_map})
        if result:
            print(f"Quran verses and embeddings processed/uploaded: {result[0]['verses_processed']}")
        else:
            print("Quran verse upload might have encountered an issue or no verses were processed.")


    # --- upload_bukhari_hadiths method (no change needed in its Cypher) ---
    def upload_bukhari_hadiths(self, bukhari_json_data):
        print("Starting Sahih Bukhari Hadith upload...")
        query_hadith = """
        UNWIND $volume_list AS volume_data
        UNWIND volume_data.books AS book_data
        UNWIND book_data.hadiths AS hadith_item
        // Using pre-calculated unique_id and ensuring it exists in the embedding_map
        WITH volume_data.name AS volume_name, book_data.name AS book_name, hadith_item,
             $id_to_unique_id_map[hadith_item.info + '|' + hadith_item.text] AS hadith_unique_id
        WHERE hadith_unique_id IS NOT NULL AND $embedding_map[hadith_unique_id] IS NOT NULL
        MERGE (h:Hadith {unique_id: hadith_unique_id})
        ON CREATE SET h.volume_name = volume_name,
                      h.book_name_english = book_name,
                      h.info_text = hadith_item.info,
                      h.narrated_by = hadith_item.by,
                      h.text_english = hadith_item.text,
                      h.embedding = $embedding_map[hadith_unique_id]
        ON MATCH SET  h.text_english = hadith_item.text,
                      h.embedding = $embedding_map[hadith_unique_id]
        RETURN count(h) AS hadiths_processed
        """
        embedding_map = {}
        id_to_unique_id_map = {} # Maps original composite key to the generated unique_id
        hadith_counter = 0
        total_hadiths_to_embed = sum(len(book.get("hadiths", [])) for volume in bukhari_json_data for book in volume.get("books", []))
        print(f"  Generating embeddings for approximately {total_hadiths_to_embed} Hadiths...")

        for volume in bukhari_json_data:
            vol_name = volume.get("name", "UnknownVolume")
            for book in volume.get("books", []):
                book_name = book.get("name", "UnknownBook")
                for hadith_data in book.get("hadiths", []):
                    info_text = hadith_data.get("info", "")
                    hadith_text_content = hadith_data.get("text", "")
                    if not hadith_text_content: # Skip if no text for embedding
                        continue

                    # Create a temporary key from original data to map to the generated unique_id
                    original_data_key = info_text + '|' + hadith_text_content

                    slug_parts = [ vol_name, book_name, info_text, str(hadith_counter)]
                    unique_id_val = "Bukhari:" + self._basic_slugify(slug_parts)
                    id_to_unique_id_map[original_data_key] = unique_id_val

                    embedding = self.generate_embedding(hadith_text_content)
                    if embedding:
                        embedding_map[unique_id_val] = embedding
                    hadith_counter += 1
                    if hadith_counter % 500 == 0 or hadith_counter == total_hadiths_to_embed:
                        print(f"    Generated embeddings for {hadith_counter}/{total_hadiths_to_embed} Hadiths...")

        if not embedding_map:
            print("  No embeddings were generated for Hadiths. Aborting upload for Bukhari.")
            return

        # Filter bukhari_json_data to only include hadiths for which embeddings were generated
        # and reconstruct the list for UNWIND to ensure hadith_item matches what's in id_to_unique_id_map
        filtered_bukhari_data = []
        for volume in bukhari_json_data:
            filtered_volume = {"name": volume.get("name"), "books": []}
            for book in volume.get("books", []):
                filtered_book = {"name": book.get("name"), "hadiths": []}
                for hadith_item in book.get("hadiths", []):
                    original_data_key = hadith_item.get("info", "") + '|' + hadith_item.get("text", "")
                    # Check if this hadith's generated unique_id has an embedding
                    if original_data_key in id_to_unique_id_map and id_to_unique_id_map[original_data_key] in embedding_map:
                        filtered_book["hadiths"].append(hadith_item)
                if filtered_book["hadiths"]:
                    filtered_volume["books"].append(filtered_book)
            if filtered_volume["books"]:
                filtered_bukhari_data.append(filtered_volume)

        if not filtered_bukhari_data:
            print("  No Hadith data with successful embeddings to upload.")
            return

        result = self._run_query(query_hadith, parameters={
            "volume_list": filtered_bukhari_data,
            "embedding_map": embedding_map,
            "id_to_unique_id_map": id_to_unique_id_map
        })
        if result:
            print(f"Sahih Bukhari hadiths and embeddings processed/uploaded: {result[0]['hadiths_processed']}")
        else:
            print("Sahih Bukhari Hadith upload might have encountered an issue or no hadiths were processed.")


    # --- create_general_concepts_with_embeddings method (no change needed in its Cypher) ---
    def create_general_concepts_with_embeddings(self, concepts_list):
        print("Starting general Islamic concept upload...")
        # ... (implementation is the same as before, just ensure self.generate_embedding is called)
        query = """
        UNWIND $concepts AS concept_data
        MERGE (ic:IslamicConcept {name: concept_data.name})
        ON CREATE SET ic.definition_english = concept_data.definition_english,
                      ic.category = concept_data.category,
                      ic.embedding = $embedding_map[concept_data.name]
        ON MATCH SET  ic.definition_english = concept_data.definition_english,
                      ic.category = concept_data.category,
                      ic.embedding = $embedding_map[concept_data.name]
        RETURN count(ic) AS concepts_processed
        """
        embedding_map = {}
        for concept in concepts_list:
            text_to_embed = concept['name']
            if 'definition_english' in concept and concept['definition_english']:
                text_to_embed += ". " + concept['definition_english']
            embedding = self.generate_embedding(text_to_embed)
            if embedding:
                embedding_map[concept['name']] = embedding
        if not embedding_map:
            print("  No embeddings generated for general concepts. Skipping upload.")
            return
        
        # Filter concepts to only include those for which embeddings were generated
        filtered_concepts_list = [c for c in concepts_list if c['name'] in embedding_map]

        result = self._run_query(query, parameters={"concepts": filtered_concepts_list, "embedding_map": embedding_map})
        if result:
            print(f"General Islamic concepts processed/uploaded: {result[0]['concepts_processed']}")

    # --- create_finance_product_concepts_with_embeddings method (no change needed in its Cypher) ---
    def create_finance_product_concepts_with_embeddings(self, products_list):
        print("Starting Islamic finance product concept upload...")
        # ... (implementation is the same as before, just ensure self.generate_embedding is called)
        query = """
        UNWIND $products AS product_data
        MERGE (ifp:IslamicFinanceProduct {name: product_data.name})
        ON CREATE SET ifp.use_case = product_data.use_case,
                      ifp.scenario_summary = product_data.scenario_summary,
                      ifp.implementation_summary = product_data.implementation_summary,
                      ifp.popular_for = product_data.popular_for,
                      ifp.fas_reference = product_data.fas_reference,
                      ifp.embedding = $embedding_map[product_data.name]
        ON MATCH SET  ifp.use_case = product_data.use_case,
                      ifp.scenario_summary = product_data.scenario_summary,
                      ifp.implementation_summary = product_data.implementation_summary,
                      ifp.popular_for = product_data.popular_for,
                      ifp.fas_reference = product_data.fas_reference,
                      ifp.embedding = $embedding_map[product_data.name]
        RETURN count(ifp) AS products_processed
        """
        embedding_map = {}
        for product in products_list:
            text_to_embed = f"Product: {product['name']}. "
            text_to_embed += f"Use Case: {product.get('use_case', '')}. "
            text_to_embed += f"FAS Reference: {product.get('fas_reference', '')}. "
            text_to_embed += f"Scenario: {product.get('scenario_summary', '')}. "
            text_to_embed += f"Implementation: {product.get('implementation_summary', '')}. "
            text_to_embed += f"Popular for: {product.get('popular_for', '')}."
            embedding = self.generate_embedding(text_to_embed)
            if embedding:
                embedding_map[product['name']] = embedding
        if not embedding_map:
            print("  No embeddings generated for finance products. Skipping upload.")
            return

        filtered_products_list = [p for p in products_list if p['name'] in embedding_map]

        result = self._run_query(query, parameters={"products": filtered_products_list, "embedding_map": embedding_map})
        if result:
            print(f"Islamic finance product concepts processed/uploaded: {result[0]['products_processed']}")
    def upload_document_chunks(self, llama_index_nodes):
        """
        Uploads LlamaIndex Node objects (chunks) to Neo4j.
        Assumes nodes might or might not have pre-computed embeddings.
        If node.embedding is None, it will attempt to generate one.
        """
        if not self.embed_model:
            print("Error: Embedding model not initialized. Cannot process document chunks.")
            return
        if not llama_index_nodes:
            print("No document chunks provided to upload.")
            return

        print(f"Starting upload of {len(llama_index_nodes)} document chunks...")
        query_chunk = """
        UNWIND $chunk_batch AS chunk_data
        MERGE (dc:DocumentChunk {chunk_id: chunk_data.chunk_id})
        ON CREATE SET dc.text_content = chunk_data.text_content,
                      dc.source_document_name = chunk_data.source_document_name,
                      dc.page_number = chunk_data.page_number,
                      dc.extra_metadata = chunk_data.extra_metadata,
                      dc.embedding = chunk_data.embedding
        ON MATCH SET  dc.text_content = chunk_data.text_content,
                      dc.source_document_name = chunk_data.source_document_name,
                      dc.page_number = chunk_data.page_number,
                      dc.extra_metadata = chunk_data.extra_metadata,
                      dc.embedding = chunk_data.embedding
        RETURN count(dc) AS chunks_processed
        """

        batch_size = 50
        chunks_data_for_neo4j_batch = []
        total_uploaded_to_db = 0
        freshly_embedded_count = 0

        for i, node in enumerate(llama_index_nodes):
            chunk_id = node.node_id
            text_content = node.get_content()
            metadata = node.metadata or {}
            source_document_name = metadata.get('file_name', 'Unknown Source')
            page_number_str = metadata.get('page_label', None)
            page_number = None
            if page_number_str is not None:
                try: page_number = int(page_number_str)
                except ValueError: page_number = None # Keep as None if not a valid int

            embedding = getattr(node, 'embedding', None) # Safely get embedding
            if not embedding:
                # print(f"  Node {chunk_id} missing embedding. Generating fresh one...")
                embedding = self.generate_embedding(text_content)
                if embedding:
                    freshly_embedded_count += 1
                else:
                    print(f"  Skipping chunk {chunk_id} from {source_document_name} due to embedding generation failure.")
                    continue # Skip this node if embedding failed

            if not embedding: # Double check if embedding is still None
                print(f"  Skipping chunk {chunk_id} (final check) - no embedding.")
                continue

            chunks_data_for_neo4j_batch.append({
                "chunk_id": chunk_id,
                "text_content": text_content,
                "source_document_name": source_document_name,
                "page_number": page_number,
                "extra_metadata": json.dumps(metadata), # Store all metadata
                "embedding": embedding
            })

            if (i + 1) % batch_size == 0 or (i + 1) == len(llama_index_nodes):
                if chunks_data_for_neo4j_batch:
                    print(f"  Uploading batch of {len(chunks_data_for_neo4j_batch)} chunks to Neo4j ({i+1}/{len(llama_index_nodes)} processed)...")
                    result = self._run_query(query_chunk, parameters={"chunk_batch": chunks_data_for_neo4j_batch})
                    if result and result[0]['chunks_processed'] is not None:
                        total_uploaded_to_db += result[0]['chunks_processed']
                    else:
                        print(f"    Batch upload might have encountered an issue for {len(chunks_data_for_neo4j_batch)} chunks.")
                    chunks_data_for_neo4j_batch = [] # Clear batch

        if freshly_embedded_count > 0:
            print(f"  Generated fresh embeddings for {freshly_embedded_count} chunks.")
        print(f"Document chunk upload complete. Total chunks uploaded/updated in DB: {total_uploaded_to_db}")


    # --- link_nodes_by_semantic_similarity method (no change needed) ---
    def link_nodes_by_semantic_similarity(self, node1_label, node2_label, relationship_type, threshold=0.75, id_prop1='unique_id', id_prop2='unique_id'):
        print(f"Attempting to link {node1_label} with {node2_label} using relationship {relationship_type} (threshold: {threshold})...")
        # ... (implementation remains the same as the previous complete code example)
        query1 = f"MATCH (n1:{node1_label}) WHERE n1.embedding IS NOT NULL RETURN n1.{id_prop1} AS id1, n1.embedding AS emb1"
        nodes1_data = self._run_query(query1)

        query2 = f"MATCH (n2:{node2_label}) WHERE n2.embedding IS NOT NULL RETURN n2.{id_prop2} AS id2, n2.embedding AS emb2"
        nodes2_data = self._run_query(query2)

        if not nodes1_data or not nodes2_data:
            print(f"  No nodes found for one or both labels ({node1_label}, {node2_label}) with embeddings. Skipping linking.")
            return

        print(f"  Comparing {len(nodes1_data)} {node1_label}(s) with {len(nodes2_data)} {node2_label}(s)...")

        link_query = f"""
        MATCH (n1:{node1_label} {{{id_prop1}: $id1}})
        MATCH (n2:{node2_label} {{{id_prop2}: $id2}})
        MERGE (n1)-[r:{relationship_type}]->(n2)
        ON CREATE SET r.score = $score, r.method = 'embedding_similarity'
        ON MATCH SET r.score = $score, r.method = 'embedding_similarity_updated'
        """
        links_created_total = 0
        processed_node1_count = 0

        for node1 in nodes1_data:
            processed_node1_count += 1
            if not node1.get('emb1') or not node1.get('id1'): continue # Added .get for safety
            emb1_np = np.array(node1['emb1'])
            if emb1_np.ndim == 0 or emb1_np.size == 0: continue

            links_for_node1 = 0
            for node2 in nodes2_data:
                if not node2.get('emb2') or not node2.get('id2'): continue # Added .get for safety
                if node1_label == node2_label and node1['id1'] == node2['id2']:
                    continue

                emb2_np = np.array(node2['emb2'])
                if emb2_np.ndim == 0 or emb2_np.size == 0: continue

                try:
                    # Ensure embeddings are not zero vectors before normalization
                    norm_emb1 = np.linalg.norm(emb1_np)
                    norm_emb2 = np.linalg.norm(emb2_np)
                    if norm_emb1 == 0 or norm_emb2 == 0:
                        similarity = 0.0
                    else:
                        similarity = np.dot(emb1_np, emb2_np) / (norm_emb1 * norm_emb2)
                    if np.isnan(similarity):
                        similarity = 0.0
                except Exception as e:
                    similarity = 0.0

                if similarity >= threshold:
                    self._run_query(link_query, parameters={"id1": node1['id1'], "id2": node2['id2'], "score": float(similarity)})
                    links_for_node1 += 1
            links_created_total += links_for_node1
            if processed_node1_count % 100 == 0 or links_for_node1 > 0 :
                 print(f"  Processed {processed_node1_count}/{len(nodes1_data)} {node1_label}s. '{node1['id1']}' linked to {links_for_node1} {node2_label}(s). Total links so far: {links_created_total}")

        print(f"Finished linking {node1_label} and {node2_label}. Total links created/updated above threshold: {links_created_total}")

    # Inside the Neo4jUploader class:

    def search_relevant_nodes_by_text(self, search_text, node_label, index_name, top_k=5):
        """
        Searches for nodes of a given label that are semantically similar to the search_text.

        Args:
            search_text (str): The text to search for.
            node_label (str): The Neo4j label of the nodes to search (e.g., "QuranVerse", "Hadith").
            index_name (str): The name of the Neo4j vector index for that node label.
            top_k (int): The number of top similar results to return.

        Returns:
            list: A list of dictionaries, where each dictionary contains the node's properties and the similarity score.
        """
        if not self.embed_model:
            print("Error: Embedding model not initialized. Cannot perform search.")
            return []
        if not search_text:
            print("Error: Search text cannot be empty.")
            return []

        # print(f"Generating embedding for search text: '{search_text[:50]}...'")
        query_embedding = self.generate_embedding(search_text)

        if not query_embedding:
            print("Error: Could not generate embedding for the search text.")
            return []

        # Ensure your Neo4j version supports db.index.vector.queryNodes (5.11+)
        # and that the vector index 'index_name' exists for 'node_label'
        # with the correct dimensions and similarity function.
        cypher_query = f"""
        CALL db.index.vector.queryNodes($index_name, $top_k, $query_embedding)
        YIELD node, score
        // Ensure the node has the expected label, though the index should handle this.
        // WHERE $node_label IN labels(node) // Optional safeguard
        RETURN node, score
        """
        # For older Neo4j without vector index, this would be very inefficient:
        # You'd have to MATCH all nodes, get all embeddings, and compute similarity in Python.

        # print(f"Querying Neo4j vector index '{index_name}' for '{node_label}' nodes similar to '{search_text[:30]}...'")
        results = self._run_query(cypher_query, parameters={
            "index_name": index_name,
            "top_k": top_k,
            "query_embedding": query_embedding
            # "node_label": node_label # Only if using the optional WHERE clause
        })

        formatted_results = []
        if results:
            for record in results:
                node_data = dict(record["node"]) # Convert Neo4j Node object to dictionary
                node_data["similarity_score"] = record["score"]
                formatted_results.append(node_data)
            # print(f"Found {len(formatted_results)} relevant {node_label} nodes.")
        # else:
            # print(f"No relevant {node_label} nodes found for the search text or an error occurred.")

        return formatted_results
    # Inside the Neo4jUploader class:
    # You'll also need the search function for DocumentChunk
    def search_document_chunks_by_text(self, search_text, top_k=5):
        """
        Searches for DocumentChunk nodes semantically similar to the search_text.
        Assumes a vector index named 'document_chunk_embeddings' exists.
        """
        return self.search_relevant_nodes_by_text(
            search_text=search_text,
            node_label="DocumentChunk",
            index_name="document_chunk_embeddings", # Ensure this index is created
            top_k=top_k
        )
    
    def search_all_sources_by_text(self, search_text, top_k=6):
        results = []

        # Search in FAS Document Chunks
        doc_chunks = self.search_relevant_nodes_by_text(
            search_text=search_text,
            node_label="DocumentChunk",
            index_name="document_chunk_embeddings",
            top_k=top_k
        )
        for result in doc_chunks:
            result["source_type"] = "DocumentChunk"
            results.append(result)

        # Search in Hadiths
        hadiths = self.search_relevant_nodes_by_text(
            search_text=search_text,
            node_label="Hadith",
            index_name="hadith_embeddings",
            top_k=top_k
        )
        for result in hadiths:
            result["source_type"] = "Hadith"
            results.append(result)

        # Search in QuranVerses
        quran_verses = self.search_relevant_nodes_by_text(
            search_text=search_text,
            node_label="QuranVerse",
            index_name="quran_verse_embeddings",
            top_k=top_k
        )
        for result in quran_verses:
            result["source_type"] = "QuranVerse"
            results.append(result)

        # Sort all results by similarity score (descending)
        results.sort(key=lambda x: x.get("similarity_score", 0), reverse=True)

        return results
        
    def upload_tafseer_with_quran(self, tafseer_json_data):
        """
        Uploads Tafseer (Quran commentary) data and links it to existing Quran verses.
        Also updates the Quran verse embeddings to include the Tafseer text.
        
        Expected format for tafseer_json_data:
        {
            "1": [  # Chapter number as key
                {
                    "chapter": "1",  # Chapter number
                    "verse": "1",    # Verse number
                    "text": "...",   # Original Quran text
                    "tafseer": "..." # Tafseer commentary text
                },
                ...
            ],
            ...
        }
        """
        print("Starting Tafseer upload and Quran verse updates...")
        
        # Query to create Tafseer nodes and link them to QuranVerses
        query_tafseer = """
        UNWIND keys($chapter_map) AS chapter_key
        UNWIND $chapter_map[chapter_key] AS verse_data
        MATCH (qv:QuranVerse {unique_id: 'Quran:' + verse_data.chapter + ':' + verse_data.verse})
        MERGE (t:Tafseer {unique_id: 'Tafseer:' + verse_data.chapter + ':' + verse_data.verse})
        ON CREATE SET t.chapter_number = toInteger(verse_data.chapter),
                      t.verse_number = toInteger(verse_data.verse),
                      t.text = verse_data.tafseer,
                      t.embedding = $tafseer_embedding_map['Tafseer:' + verse_data.chapter + ':' + verse_data.verse]
        ON MATCH SET  t.text = verse_data.tafseer,
                      t.embedding = $tafseer_embedding_map['Tafseer:' + verse_data.chapter + ':' + verse_data.verse]
        MERGE (qv)-[r:HAS_TAFSEER]->(t)
        // Update QuranVerse with combined embedding
        SET qv.embedding = $combined_embedding_map['Quran:' + verse_data.chapter + ':' + verse_data.verse],
            qv.has_tafseer = true
        RETURN count(t) AS tafseers_processed
        """
        
        if not tafseer_json_data:
            print("  No Tafseer data provided to upload_tafseer_with_quran.")
            return
            
        tafseer_embedding_map = {}
        combined_embedding_map = {}
        processed_count = 0
        
        total_verses_to_embed = sum(len(verses) for verses in tafseer_json_data.values())
        print(f"  Generating embeddings for approximately {total_verses_to_embed} Tafseer entries and combined Quran+Tafseer...")
        
        for chapter_key, verses in tafseer_json_data.items():
            for verse in verses:
                # Skip if missing required data
                if not verse.get('chapter') or not verse.get('verse') or not verse.get('tafseer'):
                    continue
                    
                quran_unique_id = f"Quran:{verse['chapter']}:{verse['verse']}"
                tafseer_unique_id = f"Tafseer:{verse['chapter']}:{verse['verse']}"
                
                # Generate embedding for Tafseer text alone
                tafseer_text = verse.get('tafseer', '')
                tafseer_embedding = self.generate_embedding(tafseer_text)
                
                # Generate embedding for combined Quran verse + Tafseer
                combined_text = f"{verse.get('text', '')} {tafseer_text}"
                combined_embedding = self.generate_embedding(combined_text)
                
                # Store embeddings if successfully generated
                if tafseer_embedding:
                    tafseer_embedding_map[tafseer_unique_id] = tafseer_embedding
                    
                if combined_embedding:
                    combined_embedding_map[quran_unique_id] = combined_embedding
                
                processed_count += 1
                if processed_count % 500 == 0 or processed_count == total_verses_to_embed:
                    print(f"    Generated embeddings for {processed_count}/{total_verses_to_embed} entries...")
        
        if not tafseer_embedding_map or not combined_embedding_map:
            print("  No embeddings were generated for Tafseer data or combined texts. Aborting upload.")
            return
            
        # Filter tafseer_json_data to only include verses for which both embeddings were generated
        filtered_tafseer_data = {}
        for chapter_key, verses in tafseer_json_data.items():
            filtered_verses = []
            for verse in verses:
                quran_unique_id = f"Quran:{verse['chapter']}:{verse['verse']}"
                tafseer_unique_id = f"Tafseer:{verse['chapter']}:{verse['verse']}"
                if (tafseer_unique_id in tafseer_embedding_map and 
                    quran_unique_id in combined_embedding_map):
                    filtered_verses.append(verse)
            if filtered_verses:
                filtered_tafseer_data[chapter_key] = filtered_verses
                
        if not filtered_tafseer_data:
            print("  No Tafseer entries with successful embeddings to upload.")
            return
            
        result = self._run_query(
            query_tafseer, 
            parameters={
                "chapter_map": filtered_tafseer_data, 
                "tafseer_embedding_map": tafseer_embedding_map,
                "combined_embedding_map": combined_embedding_map
            }
        )
        
        if result:
            print(f"Tafseer entries processed/uploaded: {result[0]['tafseers_processed']}")
            print("QuranVerse nodes updated with combined Quran+Tafseer embeddings")
            
            # Create vector index for Tafseer if it doesn't exist
            self.create_vector_index_if_not_exists("Tafseer", "tafseer_embedding", EMBEDDING_DIMENSIONS)
        else:
            print("Tafseer upload might have encountered an issue or no entries were processed.")
            
    def create_vector_index_if_not_exists(self, node_label, index_name_suffix, dimensions):
        """Helper method to create a vector index if it doesn't exist already"""
        index_name = f"{node_label.lower()}_{index_name_suffix}"
        check_index_query = "SHOW INDEXES WHERE name = $index_name"
        result = self._run_query(check_index_query, parameters={"index_name": index_name})
        
        if not result:
            create_index_query = f"""
            CREATE VECTOR INDEX {index_name} IF NOT EXISTS
            FOR (n:{node_label})
            ON n.embedding
            OPTIONS {{indexConfig: {{
                `vector.dimensions`: {dimensions},
                `vector.similarity_function`: 'cosine'
            }}}}
            """
            self._run_query(create_index_query)
            print(f"Created vector index '{index_name}' for {node_label} nodes")


