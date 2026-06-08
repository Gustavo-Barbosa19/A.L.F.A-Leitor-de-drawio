import os
import numpy as np
from typing import List, Optional, Union


class EmbeddingService:
    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or os.getenv(
            "EMBEDDING_MODEL",
            "sentence-transformers/all-MiniLM-L6-v2",
        )
        self.model = None
        self._load_model()

    def _load_model(self):
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
        except ImportError:
            print(
                "WARNING: sentence-transformers nao disponivel. "
                "Usando fallback dummy embedding."
            )
            self.model = None
        except Exception as e:
            print(f"WARNING: Erro ao carregar modelo {self.model_name}: {e}")
            self.model = None

    def embed(self, text: str) -> List[float]:
        if not text or not text.strip():
            text = "[empty]"

        if self.model is not None:
            try:
                embedding = self.model.encode(text, normalize_embeddings=True)
                return embedding.tolist()
            except Exception as e:
                print(f"Erro ao gerar embedding: {e}")
                return self._fallback_embed(text)

        return self._fallback_embed(text)

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        if self.model is not None:
            try:
                embeddings = self.model.encode(
                    texts, normalize_embeddings=True, show_progress_bar=False
                )
                return [emb.tolist() for emb in embeddings]
            except Exception as e:
                print(f"Erro ao gerar embeddings batch: {e}")
                return [self._fallback_embed(t) for t in texts]

        return [self._fallback_embed(t) for t in texts]

    def _fallback_embed(self, text: str) -> List[float]:
        import hashlib
        hash_bytes = hashlib.md5(text.encode()).digest()
        seed = int.from_bytes(hash_bytes[:4], "big")
        rng = np.random.RandomState(seed)
        vec = rng.randn(384)
        vec = vec / np.linalg.norm(vec)
        return vec.tolist()

    def get_dimension(self) -> int:
        test_emb = self.embed("test")
        return len(test_emb)

    @staticmethod
    def generate_chunks_from_graph(graph_data) -> List[dict]:
        chunks = []

        node: dict
        for node in graph_data.get("nodes", []):
            chunk = {
                "texto": node.get("texto", ""),
                "node_id": node.get("id"),
                "tipo": node.get("tipo", "processo"),
                "tipo_chunk": "node",
            }
            chunks.append(chunk)

        edge: dict
        for edge in graph_data.get("edges", []):
            chunk = {
                "texto": edge.get("label", "") or f"Conexao de {edge.get('source')} para {edge.get('target')}",
                "source": edge.get("source"),
                "target": edge.get("target"),
                "tipo_chunk": "edge",
            }
            if chunk["texto"]:
                chunks.append(chunk)

        return chunks
