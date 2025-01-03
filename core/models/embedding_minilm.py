import logging
import os
from llama_cpp import Llama
from typing import List

logger = logging.getLogger(__name__)

class MiniLMInterface:
    """
    A specialized embedding interface that uses a smaller .gguf model
    (all-MiniLM-L6-v2.F32.gguf) for semantic embeddings.

    This class will produce embeddings of dimension ~384 (the typical dimension
    for that MiniLM variant). This ensures we store vectors that match Chroma's
    384 dimension.
    """
    def __init__(self, model_path: str, n_ctx: int = 512, n_threads: int = 4, n_batch: int = 128):
        self.model_path = model_path
        self.n_ctx = n_ctx
        self.n_threads = n_threads
        self.n_batch = n_batch
        self._init_embed_model()

    def _init_embed_model(self):
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"MiniLM model not found at {self.model_path}")

        logger.info(f"[MiniLMInterface] Loading embedding model from {self.model_path} with n_ctx={self.n_ctx}")
        # llama.cpp can run "embedding=True" for certain specialized smaller models
        self.emb_llm = Llama(
            model_path=self.model_path,
            n_ctx=self.n_ctx,
            n_threads=self.n_threads,
            n_batch=self.n_batch,
            embedding=True,  # Important: We enable embedding mode here
        )

    def get_embedding(self, text: str) -> List[float]:
        """
        Generate an embedding for the given text using the miniLM .gguf model.
        Typically, the dimension is 384 if the model is truly a miniLM-l6-v2 variant.
        """
        try:
            # The llama-cpp embedding call returns a list of floats
            emb_result = self.emb_llm.embed(text)
            logger.debug(f"[MiniLMInterface] Embedding for '{text[:30]}...' => dim={len(emb_result)}")
            return emb_result  # This should be ~384 floats
        except Exception as e:
            logger.exception(f"[MiniLMInterface] Error generating embedding: {e}")
            return []
