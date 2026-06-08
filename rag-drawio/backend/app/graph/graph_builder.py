import networkx as nx
from typing import List, Optional, Dict, Any
from ..models.schemas import DrawioGraph, DrawioNode, DrawioEdge, NodeEnriched


class GraphBuilder:
    def __init__(self):
        self.graph: nx.DiGraph = nx.DiGraph()
        self.node_map: Dict[str, DrawioNode] = {}

    def build(self, drawio_graph: DrawioGraph) -> "GraphBuilder":
        self.graph.clear()
        self.node_map.clear()

        node: DrawioNode
        for node in drawio_graph.nodes:
            self.node_map[node.id] = node
            self.graph.add_node(
                node.id,
                texto=node.texto,
                tipo=node.tipo,
                parent=node.parent,
            )

        edge: DrawioEdge
        for edge in drawio_graph.edges:
            if edge.source in self.node_map and edge.target in self.node_map:
                attrs = {}
                if edge.label:
                    attrs["label"] = edge.label
                if edge.style:
                    attrs["style"] = edge.style
                self.graph.add_edge(edge.source, edge.target, **attrs)

        return self

    def get_enriched_node(self, node_id: str) -> Optional[NodeEnriched]:
        if node_id not in self.graph:
            return None
        node_data = self.node_map.get(node_id)
        if not node_data:
            return None

        proximos = list(self.graph.successors(node_id))
        anteriores = list(self.graph.predecessors(node_id))
        caminhos = self._get_all_paths_to_end(node_id)

        return NodeEnriched(
            id=node_id,
            texto=node_data.texto,
            tipo=node_data.tipo,
            proximos=proximos,
            anteriores=anteriores,
            caminhos_possiveis=[p[-1] if p else "" for p in caminhos[:5]] if caminhos else [],
        )

    def get_next_nodes(self, node_id: str) -> List[Dict[str, Any]]:
        if node_id not in self.graph:
            return []
        result = []
        for succ in self.graph.successors(node_id):
            edge_data = self.graph.get_edge_data(node_id, succ)
            node_info = self.node_map.get(succ)
            result.append({
                "id": succ,
                "texto": node_info.texto if node_info else "",
                "tipo": node_info.tipo if node_info else "processo",
                "label": edge_data.get("label", "") if edge_data else "",
            })
        return result

    def get_previous_nodes(self, node_id: str) -> List[Dict[str, Any]]:
        if node_id not in self.graph:
            return []
        result = []
        for pred in self.graph.predecessors(node_id):
            node_info = self.node_map.get(pred)
            result.append({
                "id": pred,
                "texto": node_info.texto if node_info else "",
                "tipo": node_info.tipo if node_info else "processo",
            })
        return result

    def get_all_nodes_enriched(self) -> List[NodeEnriched]:
        return [
            self.get_enriched_node(nid)
            for nid in self.graph.nodes
            if self.get_enriched_node(nid) is not None
        ]

    def get_subgraph_text(self, node_id: str, depth: int = 2) -> str:
        if node_id not in self.graph:
            return ""
        visited = set()
        texts = []
        self._dfs_text(node_id, depth, visited, texts)
        return " -> ".join(texts)

    def _dfs_text(self, node_id: str, depth: int, visited: set, texts: list):
        if depth <= 0 or node_id in visited:
            return
        visited.add(node_id)
        node_info = self.node_map.get(node_id)
        if node_info:
            texts.append(f"[{node_info.tipo}] {node_info.texto}")
        for succ in self.graph.successors(node_id):
            self._dfs_text(succ, depth - 1, visited, texts)

    def _get_all_paths_to_end(self, node_id: str, max_depth: int = 10):
        paths = []
        end_nodes = [n for n in self.graph.nodes if self.graph.out_degree(n) == 0]

        for end in end_nodes:
            try:
                all_paths = list(nx.all_simple_paths(self.graph, node_id, end, cutoff=max_depth))
                paths.extend(all_paths)
            except (nx.NetworkXNoPath, nx.NodeNotFound):
                continue

        return paths

    def find_node_by_text_similarity(self, search_text: str) -> Optional[str]:
        search_lower = search_text.lower().strip()
        best_match = None
        best_score = 0

        for nid, node_data in self.node_map.items():
            node_text = node_data.texto.lower()
            if search_lower in node_text:
                score = len(search_lower) / max(len(node_text), 1)
                if score > best_score:
                    best_score = score
                    best_match = nid

            # Word overlap
            search_words = set(search_lower.split())
            node_words = set(node_text.split())
            if search_words and node_words:
                overlap = len(search_words & node_words)
                if overlap > best_score:
                    best_score = overlap
                    best_match = nid

        return best_match

    def get_graph_summary(self) -> Dict[str, Any]:
        return {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "tipos": self._count_types(),
            "nodes": [
                {"id": nid, "texto": self.node_map[nid].texto, "tipo": self.node_map[nid].tipo}
                for nid in self.graph.nodes
                if nid in self.node_map
            ],
        }

    def _count_types(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for nid in self.graph.nodes:
            node_data = self.node_map.get(nid)
            if node_data:
                tipo = node_data.tipo
                counts[tipo] = counts.get(tipo, 0) + 1
        return counts
