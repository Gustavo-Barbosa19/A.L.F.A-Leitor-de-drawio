from app.parser.drawio_parser import parse_drawio

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

g = parse_drawio(xml.encode("utf-8"))
print(f"Nos: {len(g.nodes)}")
print(f"Arestas: {len(g.edges)}")
for n in g.nodes:
    print(f"  - [{n.tipo}] {n.id}: {n.texto}")
for e in g.edges:
    print(f"  -> {e.source} -> {e.target} ({e.label})")
