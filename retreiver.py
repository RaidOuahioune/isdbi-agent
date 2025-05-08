from llama_index.core import StorageContext, load_index_from_storage
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
storage_path = "./vector_db_storage/"

storage_context = StorageContext.from_defaults(persist_dir=storage_path)

# Load the index from storage


embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")  # Adjust device as needed

index = load_index_from_storage(storage_context,embed_model=embed_model)

retriever = VectorIndexRetriever(
    index=index,
    similarity_top_k=20,  # Number of most relevant chunks to retrieve
)