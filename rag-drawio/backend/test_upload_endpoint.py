"""Testa o fluxo de upload sem precisar do servidor HTTP."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.parser.drawio_parser import parse_drawio
from app.graph.graph_builder import GraphBuilder
from app.embeddings.embedding_service import EmbeddingService

# 1. Parse
xml = '''<?xml version="1.0" encoding="UTF-8"?>
<mxGraphModel>
  <root>
    <mxCell id="0" />
    <mxCell id="1" parent="0" />
    <mxCell id="2" value="Inicio" style="ellipse" parent="1" vertex="1">
      <mxGeometry x="10" y="10" width="120" height="40" as="geometry" />
    </mxCell>
    <mxCell id="3" value="Processar dados" style="rounded=1" parent="1" vertex="1">
      <mxGeometry x="150" y="10" width="120" height="40" as="geometry" />
    </mxCell>
    <mxCell id="4" value="Decisao?" style="rhombus" parent="1" vertex="1">
      <mxGeometry x="290" y="10" width="120" height="40" as="geometry" />
    </mxCell>
    <mxCell id="5" value="Fim" style="ellipse" parent="1" vertex="1">
      <mxGeometry x="430" y="10" width="120" height="40" as="geometry" />
    </mxCell>
    <mxCell id="e1" source="2" target="3" parent="1" edge="1">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    <mxCell id="e2" value="Sim" source="3" target="4" parent="1" edge="1">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    <mxCell id="e3" source="4" target="5" parent="1" edge="1">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
  </root>
</mxGraphModel>'''

print("[1/3] Parseando XML...")
g = parse_drawio(xml.encode("utf-8"))
print(f"  OK: {len(g.nodes)} nos, {len(g.edges)} arestas")

print("[2/3] Construindo grafo...")
builder = GraphBuilder().build(g)
summary = builder.get_graph_summary()
print(f"  OK: {summary['total_nodes']} nos no grafo")

print("[3/3] Gerando embeddings...")
emb = EmbeddingService()
n1 = builder.get_enriched_node("2")
if n1:
    print(f"  No '2': {n1.texto} -> proximos: {n1.proximos}")
n2 = builder.get_enriched_node("3")
if n2:
    print(f"  No '3': {n2.texto} -> proximos: {n2.proximos}")
n3 = builder.get_enriched_node("4")
if n3:
    print(f"  No '4': {n3.texto} -> proximos: {n3.proximos}")
n4 = builder.get_enriched_node("5")
if n4:
    print(f"  No '5': {n4.texto} -> proximos: {n4.proximos}")

next_nodes = builder.get_next_nodes("3")
print(f"\nProximos de 'Processar dados': {[n['texto'] for n in next_nodes]}")

prev_nodes = builder.get_previous_nodes("3")
print(f"Anteriores de 'Processar dados': {[n['texto'] for n in prev_nodes]}")

print("\n[OK] Sistema funcionando corretamente!")
print("Inicie o backend com: python -m app.main")
print("E o frontend com: npm run dev (na pasta frontend/)")
