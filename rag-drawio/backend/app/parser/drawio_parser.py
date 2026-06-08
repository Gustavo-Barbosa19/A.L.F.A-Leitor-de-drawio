import xml.etree.ElementTree as ET
import re
import zipfile
import io
from typing import List, Optional
from ..models.schemas import DrawioNode, DrawioEdge, DrawioGraph


NODE_TYPE_KEYWORDS = {
    "decisao": ["decisão", "decisa", "?", "if ", "else", "se ", "senão", "senao"],
    "inicio": ["início", "inicio", "começo", "comeco", "start", "begin"],
    "fim": ["fim", "end", "final", "termina"],
    "processo": [],
}


def _detect_node_type(texto: str, style: Optional[str] = None) -> str:
    texto_lower = texto.lower().strip()

    if style and "rhombus" in style:
        return "decisao"

    for tipo, keywords in NODE_TYPE_KEYWORDS.items():
        if any(kw in texto_lower for kw in keywords):
            return tipo

    if style:
        if "ellipse" in style or "oval" in style:
            if any(kw in texto_lower for kw in NODE_TYPE_KEYWORDS["inicio"]):
                return "inicio"
            return "fim"
        if "hexagon" in style:
            return "processo"

    return "processo"


def _extract_label_from_style(style: str) -> Optional[str]:
    match = re.search(r'label[=;]([^;]*)', style)
    if match:
        return match.group(1).strip()
    return None


def _parse_mxfile(xml_content: str) -> DrawioGraph:
    root = ET.fromstring(xml_content)
    ns = {"mx": "http://schemas.microsoft.com/office/drawing/2010/main"}

    nodes = {}
    edges = []
    cell_parents = {}

    all_cells = root.findall(".//mxCell") or root.findall(".//{http://schemas.microsoft.com/office/drawing/2010/main}cell")

    if not all_cells:
        all_cells = root.findall(".//*")

    # First pass: collect all mxCell elements
    mx_cells = []
    for el in root.iter():
        tag = el.tag
        if tag.endswith("}cell") or tag == "cell" or tag == "mxCell":
            mx_cells.append(el)
        elif el.get("id") and (el.get("value") is not None or el.get("source") is not None or el.get("target") is not None):
            mx_cells.append(el)

    # Second pass: process cells
    for cell in mx_cells:
        cell_id = cell.get("id")
        if not cell_id:
            continue

        parent = cell.get("parent")
        if parent:
            cell_parents[cell_id] = parent

        value = cell.get("value", "")

        source = cell.get("source")
        target = cell.get("target")
        style = cell.get("style")

        if source and target:
            label = value.strip() if value else None
            if not label and style:
                label = _extract_label_from_style(style)
            edges.append(DrawioEdge(source=source, target=target, label=label, style=style))
            continue

        if value or (style and "text" not in style and ";" not in (style or "").replace("html", "").replace("rounded", "")):
            texto = value.strip() if value else ""
            if texto:
                tipo = _detect_node_type(texto, style)
                node = DrawioNode(id=cell_id, texto=texto, tipo=tipo, parent=parent, style=style)
                nodes[cell_id] = node

    # If we got very few nodes with the above logic, fallback: collect all cells with <div> or text content
    if len(nodes) < 2:
        for cell in mx_cells:
            cell_id = cell.get("id")
            if not cell_id or cell_id in nodes:
                continue

            source = cell.get("source")
            target = cell.get("target")
            if source and target:
                continue

            value = cell.get("value", "")
            if value and value.strip():
                texto = value.strip()
                estilo = cell.get("style", "")
                cell_parent = cell.get("parent")
                tipo = _detect_node_type(texto, estilo)
                node = DrawioNode(id=cell_id, texto=texto, tipo=tipo, parent=cell_parent, style=estilo)
                nodes[cell_id] = node

    # Handle child-parent relationships: if a parent has text and children, merge
    for child_id, parent_id in cell_parents.items():
        if parent_id in nodes and child_id in nodes:
            child_text = nodes[child_id].texto
            if child_text and len(child_text) > len(nodes[parent_id].texto or ""):
                nodes[parent_id].texto += " - " + child_text

    # Filter out geometry-only cells with no meaningful text
    nodes_filtered = {k: v for k, v in nodes.items() if v.texto and len(v.texto.strip()) > 0}

    return DrawioGraph(
        nodes=list(nodes_filtered.values()),
        edges=edges,
    )


def parse_drawio(content: bytes) -> DrawioGraph:
    xml_content = None

    try:
        with zipfile.ZipFile(io.BytesIO(content)) as z:
            compressed_files = [f for f in z.namelist() if f.endswith(".drawio")]
            if compressed_files:
                xml_content = z.read(compressed_files[0]).decode("utf-8")
            else:
                # Try reading any XML file inside the zip
                xml_files = [f for f in z.namelist()]
                for f in xml_files:
                    data = z.read(f)
                    try:
                        text = data.decode("utf-8")
                        if "mxGraphModel" in text or "mxCell" in text:
                            xml_content = text
                            break
                    except:
                        continue
    except (zipfile.BadZipFile, zipfile.LargeZipFile):
        pass

    if xml_content is None:
        try:
            decoded = content.decode("utf-8")
            if "mxGraphModel" in decoded or "mxCell" in decoded:
                xml_content = decoded
        except UnicodeDecodeError:
            text = content.decode("latin-1")
            if "mxGraphModel" in text or "mxCell" in text:
                xml_content = text

    if xml_content is None:
        raise ValueError("Não foi possível interpretar o arquivo draw.io.")

    graph = _parse_mxfile(xml_content)

    # Deduplicate edges
    seen_edges = set()
    unique_edges = []
    for edge in graph.edges:
        key = (edge.source, edge.target)
        if key not in seen_edges:
            seen_edges.add(key)
            unique_edges.append(edge)

    graph.edges = unique_edges

    return graph
