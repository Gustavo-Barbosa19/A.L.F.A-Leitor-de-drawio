import os
import json
from typing import Optional, Dict, Any

from ..embeddings.embedding_service import EmbeddingService
from ..vector_store.qdrant_store import QdrantStore
from ..graph.graph_builder import GraphBuilder
from ..rag.guardrails import GuardrailsValidator
from ..models.schemas import AskResponse


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


class GraphRAG:
    """
    Graph RAG System:
    1. Busca semantica no Qdrant para localizar no relevante
    2. Validacao estrutural no grafo networkx
    3. Navegacao pelas conexoes reais
    4. Geracao de resposta baseada SOMENTE nos dados encontrados
    """

    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_store: QdrantStore,
        graph_builder: Optional[GraphBuilder] = None,
    ):
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.graph_builder = graph_builder
        self.guardrails = GuardrailsValidator(graph_builder)

    def set_graph_builder(self, graph_builder: GraphBuilder):
        self.graph_builder = graph_builder
        self.guardrails.graph_builder = graph_builder

    def ask(self, pergunta: str) -> AskResponse:
        if not self.graph_builder or self.graph_builder.graph.number_of_nodes() == 0:
            return AskResponse(
                pergunta=pergunta,
                resposta="Nenhum fluxograma carregado. Envie um arquivo .drawio primeiro.",
                fonte=None,
            )

        pergunta_lower = pergunta.lower().strip()

        # Step 1: Try direct node matching in the graph
        match_by_text = self._match_by_direct_search(pergunta_lower)
        if match_by_text:
            node_id, node_data = match_by_text
            enriched = self.graph_builder.get_enriched_node(node_id)
            if enriched:
                next_nodes = self.graph_builder.get_next_nodes(node_id)
                prev_nodes = self.graph_builder.get_previous_nodes(node_id)
                resposta = self.guardrails.build_safe_response(
                    node_data.texto, next_nodes, prev_nodes
                )
                return AskResponse(
                    pergunta=pergunta,
                    resposta=resposta,
                    fonte={
                        "node_id": node_id,
                        "texto_original": node_data.texto,
                        "proximo": next_nodes[0]["texto"] if next_nodes else None,
                    },
                )

        # Step 2: Semantic search via embeddings
        sem_result = self._search_semantic(pergunta)
        if sem_result:
            node_id, node_data, score = sem_result
            enriched = self.graph_builder.get_enriched_node(node_id)
            if enriched:
                next_nodes = self.graph_builder.get_next_nodes(node_id)
                prev_nodes = self.graph_builder.get_previous_nodes(node_id)
                resposta = self.guardrails.build_safe_response(
                    node_data.texto, next_nodes, prev_nodes
                )
                return AskResponse(
                    pergunta=pergunta,
                    resposta=resposta,
                    fonte={
                        "node_id": node_id,
                        "texto_original": node_data.texto,
                        "proximo": next_nodes[0]["texto"] if next_nodes else None,
                        "score": score,
                    },
                )

        # Step 3: Try LLM-based extraction
        if OPENAI_API_KEY:
            llm_result = self._ask_llm(pergunta)
            if llm_result:
                return llm_result

        # Fallback: no results found
        return AskResponse(
            pergunta=pergunta,
            resposta="Nao encontrei essa informacao no fluxograma.",
            fonte=None,
        )

    def _match_by_direct_search(self, pergunta_lower: str):
        match = self.graph_builder.find_node_by_text_similarity(pergunta_lower)
        if match:
            node_data = self.graph_builder.node_map.get(match)
            if node_data:
                return match, node_data
        return None

    def _search_semantic(self, pergunta: str):
        embedding = self.embedding_service.embed(pergunta)
        results = self.vector_store.search(embedding, top_k=3)

        for r in results:
            nid = r.get("node_id")
            if nid and nid in self.graph_builder.graph and nid in self.graph_builder.node_map:
                node_data = self.graph_builder.node_map.get(nid)
                if node_data and r.get("score", 0) > 0.3:
                    return nid, node_data, r.get("score", 0)
        return None

    def _ask_llm(self, pergunta: str) -> Optional[AskResponse]:
        try:
            from openai import OpenAI

            graph_data = self.graph_builder.get_graph_summary()
            context = json.dumps(graph_data, ensure_ascii=False, indent=2)

            client = OpenAI(api_key=OPENAI_API_KEY)

            system_prompt = (
                "Voce e um assistente especializado em analisar fluxogramas draw.io. "
                "Sua funcao e responder perguntas com BASE EXCLUSIVA no conteudo do fluxograma fornecido. "
                "NAO invente informacoes. NAO complete lacunas. "
                "Se a informacao nao existir no fluxograma, responda exatamente: "
                "\"Nao encontrei essa informacao no fluxograma.\" "
                "Responda em portugues brasileiro de forma clara e concisa."
            )

            user_prompt = (
                f"Fluxograma atual:\n{context}\n\n"
                f"Pergunta do usuario: {pergunta}\n\n"
                "Responda com base SOMENTE nos dados do fluxograma acima."
            )

            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.1,
                max_tokens=500,
            )

            resposta = response.choices[0].message.content.strip()

            return AskResponse(
                pergunta=pergunta,
                resposta=resposta,
                fonte={"fonte": "llm_com_grafo"},
            )

        except Exception as e:
            print(f"Erro ao consultar LLM: {e}")
            return None
