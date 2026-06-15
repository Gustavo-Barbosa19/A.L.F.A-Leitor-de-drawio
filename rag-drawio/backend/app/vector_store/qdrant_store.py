import os
import uuid
from typing import List, Optional, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue


QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "drawio_flows")


class QdrantStore:
    def __init__(self):
        self.client = None
        self.collection_name = QDRANT_COLLECTION
        self._connected = False

    def _connect(self):
        if self._connected and self.client is not None:
            return
        try:
            kwargs = {"host": QDRANT_HOST, "port": QDRANT_PORT, "timeout": 5}
            if QDRANT_API_KEY:
                kwargs["api_key"] = QDRANT_API_KEY
                kwargs["https"] = True
            self.client = QdrantClient(**kwargs)
            self.client.get_collections()
            self._connected = True
        except Exception as e:
            self._connected = False
            print(f"Qdrant nao disponivel: {e}")

    def _ensure_collection(self, vector_size: int = 384):
        self._connect()
        if not self._connected or self.client is None:
            return
        try:
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)
            if not exists:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
                )
        except Exception as e:
            print(f"Erro ao garantir colecao Qdrant: {e}")

    def recreate_collection(self, vector_size: int = 384):
        self._connect()
        if not self._connected:
            return
        try:
            self.client.delete_collection(collection_name=self.collection_name)
        except Exception:
            pass
        try:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )
        except Exception as e:
            print(f"Erro ao recriar colecao: {e}")

    def upsert_node(self, node_id: str, texto: str, embedding: List[float], metadata: Dict[str, Any]):
        self._connect()
        if not self._connected:
            return
        point = PointStruct(
            id=str(uuid.uuid5(uuid.NAMESPACE_DNS, node_id)),
            vector=embedding,
            payload={"node_id": node_id, "texto": texto, **metadata},
        )
        try:
            self.client.upsert(collection_name=self.collection_name, points=[point])
        except Exception as e:
            print(f"Erro ao upsertar no Qdrant: {e}")

    def upsert_batch(self, points: List[PointStruct]):
        self._connect()
        if not self._connected or not points:
            return
        try:
            self.client.upsert(collection_name=self.collection_name, points=points)
        except Exception as e:
            print(f"Erro ao upsertar batch no Qdrant: {e}")

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict]:
        self._connect()
        if not self._connected:
            return []
        try:
            hits = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k,
            )
            return [
                {
                    "node_id": hit.payload.get("node_id"),
                    "texto": hit.payload.get("texto"),
                    "tipo": hit.payload.get("tipo"),
                    "score": hit.score,
                    "payload": hit.payload,
                }
                for hit in hits
            ]
        except Exception as e:
            print(f"Erro ao buscar no Qdrant: {e}")
            return []

    def search_with_filter(self, query_embedding: List[float], tipo: Optional[str] = None, top_k: int = 5) -> List[Dict]:
        self._connect()
        if not self._connected:
            return []
        try:
            query_filter = None
            if tipo:
                query_filter = Filter(must=[FieldCondition(key="tipo", match=MatchValue(value=tipo))])
            hits = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=query_filter,
                limit=top_k,
            )
            return [
                {
                    "node_id": hit.payload.get("node_id"),
                    "texto": hit.payload.get("texto"),
                    "tipo": hit.payload.get("tipo"),
                    "score": hit.score,
                    "payload": hit.payload,
                }
                for hit in hits
            ]
        except Exception as e:
            print(f"Erro ao buscar no Qdrant: {e}")
            return []

    def get_all_nodes(self) -> List[Dict]:
        self._connect()
        if not self._connected:
            return []
        try:
            records = self.client.scroll(collection_name=self.collection_name, limit=10000)[0]
            return [
                {
                    "node_id": rec.payload.get("node_id"),
                    "texto": rec.payload.get("texto"),
                    "tipo": rec.payload.get("tipo"),
                    "payload": rec.payload,
                }
                for rec in records
            ]
        except Exception as e:
            print(f"Erro ao listar nos do Qdrant: {e}")
            return []

    def delete_collection_data(self):
        self._connect()
        if not self._connected:
            return
        try:
            self.client.delete_collection(collection_name=self.collection_name)
        except Exception as e:
            print(f"Erro ao deletar colecao: {e}")

    def count_points(self) -> int:
        self._connect()
        if not self._connected:
            return 0
        try:
            result = self.client.count(collection_name=self.collection_name)
            return result.count
        except Exception:
            return 0

    def health_check(self) -> bool:
        self._connect()
        if not self._connected:
            return False
        try:
            self.client.get_collections()
            return True
        except Exception:
            return False
