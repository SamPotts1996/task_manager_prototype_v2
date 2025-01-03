import logging
import chromadb
from chromadb.config import Settings
from typing import List, Dict

logger = logging.getLogger(__name__)

class VectorStorage:
    """
    A wrapper around Chroma for storing and retrieving embeddings and associated content.
    We assume we have a separate embedding model from Llama, so we do not do Llama embeddings here.
    We call a 'MiniLMInterface' externally and pass the result in if needed.
    """
    def __init__(
        self,
        embedding_interface=None,
        collection_name: str = "agent_memory",
        persist_directory: str = "chroma_db"
    ):
        """
        If 'embedding_interface' is not None, we can do on-the-fly embeddings inside VectorStorage.
        Otherwise, we expect the user to pass embeddings directly.
        """
        self.embedding_interface = embedding_interface
        self.client = chromadb.Client(
            Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=persist_directory
            )
        )
        logger.debug("[VectorStorage] Initializing collection...")
        self.collection = self.client.get_or_create_collection(collection_name)
        logger.debug(f"[VectorStorage] Collection '{collection_name}' ready.")

    def store(self, doc_id: str, text: str, metadata: Dict = None):
        """
        Store a piece of text. If we have an embedding interface, we will embed here;
        otherwise we expect the caller to embed externally.
        """
        if metadata is None:
            metadata = {}

        try:
            if self.embedding_interface:
                # Generate embedding via MiniLM
                embedding = self.embedding_interface.get_embedding(text)
            else:
                logger.warning("[VectorStorage] No embedding interface; storing doc with empty embedding.")
                embedding = []

            logger.debug(f"[VectorStorage] Storing doc_id={doc_id}, len_embedding={len(embedding)}")
            self.collection.add(
                documents=[text],
                embeddings=[embedding],
                metadatas=[metadata],
                ids=[doc_id]
            )
            logger.debug("[VectorStorage] Document stored with embedding.")
        except Exception as e:
            logger.error(f"[VectorStorage] Error storing in vector DB: {e}", exc_info=True)

    def query_similar(self, query_text: str, k: int = 3) -> List[Dict]:
        """
        Query the DB for the top-k similar documents to 'query_text'.
        We'll embed the query with our interface if available.
        """
        if not self.embedding_interface:
            logger.warning("[VectorStorage] No embedding interface; cannot do similarity search. Returning empty.")
            return []

        try:
            query_emb = self.embedding_interface.get_embedding(query_text)
            results = self.collection.query(
                query_embeddings=[query_emb],
                n_results=k
            )
            # results is a dict with "documents", "ids", "metadatas", "embeddings" (optionally)
            docs = []
            for i in range(len(results["documents"][0])):
                docs.append({
                    "id": results["ids"][0][i],
                    "document": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i]
                })
            return docs
        except Exception as e:
            logger.error(f"[VectorStorage] Error querying vector DB: {e}", exc_info=True)
            return []
