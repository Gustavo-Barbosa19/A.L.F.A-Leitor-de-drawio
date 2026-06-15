import re
from typing import Optional, Tuple


class GuardrailsValidator:
    """
    Sistema anti-alucinacao.
    Valida se a resposta gerada pela IA esta estritamente baseada
    no conteudo extraido do fluxograma.
    """

    def __init__(self, graph_builder=None):
        self.graph_builder = graph_builder

    def validate_response(
        self,
        resposta: str,
        node_ids_involved: list,
    ) -> Tuple[bool, str]:
        """
        Valida se a resposta contem apenas informacoes presentes nos nos.
        Retorna (valido, mensagem_ajustada).
        """
        if not node_ids_involved:
            return False, "Nao foi possivel encontrar informacao no fluxograma."

        textos_validos = set()
        for nid in node_ids_involved:
            if self.graph_builder and nid in self.graph_builder.graph:
                node_data = self.graph_builder.node_map.get(nid)
                if node_data:
                    textos_validos.add(node_data.texto.lower())

        if not textos_validos:
            return False, "Nao foi possivel validar a informacao no fluxograma."

        return True, resposta

    def extract_nodes_from_question(
        self, pergunta: str
    ) -> Optional[list]:
        """
        Tenta extrair mencpes a nos especificos na pergunta.
        """
        if not self.graph_builder:
            return None

        matched_nodes = []
        pergunta_lower = pergunta.lower()

        for nid, node_data in self.graph_builder.node_map.items():
            node_text_lower = node_data.texto.lower()
            if node_text_lower and (
                node_text_lower in pergunta_lower
                or any(
                    word in pergunta_lower
                    for word in node_text_lower.split()
                    if len(word) > 3
                )
            ):
                matched_nodes.append(nid)

        return matched_nodes if matched_nodes else None

    def check_hallucination(
        self, response_text: str, valid_texts: set
    ) -> bool:
        """
        Verifica se a resposta contem afirmacoes alem do que esta nos textos validos.
        Retorna True se detectar alucinacao.
        """
        sentences = re.split(r'[.!?]+', response_text)
        for sentence in sentences:
            sentence = sentence.strip().lower()
            if not sentence or len(sentence) < 10:
                continue
            if sentence.startswith("nao") or sentence.startswith("não"):
                continue
            if not any(valid_word in sentence for valid_word in valid_texts):
                return True
        return False

    def build_safe_response(
        self, node_texto: str, next_nodes: list, prev_nodes: list
    ) -> str:
        """Constrói resposta segura baseada exclusivamente nos dados do grafo."""
        lines = []

        if node_texto:
            lines.append(f"No encontrado: {node_texto}")

        if next_nodes:
            textos = []
            for n in next_nodes[:3]:
                label = f" ({n.get('label', '')})" if n.get("label") else ""
                textos.append(f"{n.get('texto', '')}{label}")
            if textos:
                lines.append("Proximo(s) passo(s): " + ", ".join(textos))
        else:
            lines.append("Este no nao possui proximos passos.")

        if prev_nodes:
            textos = [n.get("texto", "") for n in prev_nodes[:3]]
            lines.append("Passo(s) anterior(es): " + ", ".join(textos))

        return "\n".join(lines)
