import logging
from typing import List, Union
from llama_cpp import Llama

logger = logging.getLogger(__name__)

class LlamaInterface:
    def __init__(self, model_path: str, n_ctx: int = 2048):
        self.model_path = model_path
        self.n_ctx = n_ctx
        self._init_models()

    def _init_models(self):
        logger.info(f"[LlamaInterface] Loading model from {self.model_path} with n_ctx={self.n_ctx}")
        self.llm = Llama(
            model_path=self.model_path,
            n_ctx=self.n_ctx,
            n_threads=8,
            n_batch=512
        )
        self.embedding_model = Llama(
            model_path=self.model_path,
            n_ctx=self.n_ctx,
            n_threads=8,
            embedding=True
        )

    def generate(self, prompt: str, max_tokens: int = 200) -> str:
        try:
            response = self.llm(
                prompt,
                max_tokens=max_tokens,
                temperature=0.1,
                top_p=0.95,
                top_k=40,
                repeat_penalty=1.1,
                stop=["Human:", "Assistant:"]
            )
            text_out = response["choices"][0]["text"].strip()
            logger.info(f"[LlamaInterface] Generated text: {text_out}")
            return text_out
        except Exception as e:
            logger.exception(f"[LlamaInterface] Error in LLM generation: {e}")
            return ""

    def get_embedding(self, text: str) -> List[float]:
        try:
            raw_embed = self.embedding_model.embed(text)
            emb = self._really_flatten_embedding(raw_embed)
            logger.debug(f"[LlamaInterface] Generated embedding of length {len(emb)}.")
            return emb
        except Exception as e:
            logger.exception(f"[LlamaInterface] Error getting embedding: {e}")
            return []

    def _really_flatten_embedding(self, emb: Union[float, List]) -> List[float]:
        """
        Flatten any nested list elements into one 1D list of floats.
        """
        flattened = []
        stack = [emb]  # iterative approach to flatten

        while stack:
            current = stack.pop()
            if isinstance(current, list):
                stack.extend(current)
            else:
                # must be numeric or castable to float
                flattened.append(float(current))

        flattened.reverse()  # because we used pop from the end
        return flattened
