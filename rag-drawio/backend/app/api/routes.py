import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from ..models.schemas import (
    AskRequest,
    AskResponse,
    UploadResponse,
    HealthResponse,
)
from ..parser.drawio_parser import parse_drawio
from ..graph.graph_builder import GraphBuilder
from ..embeddings.embedding_service import EmbeddingService
from ..vector_store.qdrant_store import QdrantStore
from ..rag.graph_rag import GraphRAG


router = APIRouter()

embedding_service = EmbeddingService()
vector_store = QdrantStore()
graph_builder = GraphBuilder()
rag_system = GraphRAG(embedding_service, vector_store, graph_builder)

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

uploaded_files = {}


@router.get("/health", response_model=HealthResponse)
async def health():
    qdrant_ok = False
    try:
        qdrant_ok = vector_store.health_check()
    except Exception:
        qdrant_ok = False

    return HealthResponse(
        status="ok",
        versao="1.0.0",
        qdrant_connected=qdrant_ok,
        arquivos_carregados=len(uploaded_files),
    )


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Nome de arquivo invalido.")

    if not (file.filename.endswith(".drawio") or file.filename.endswith(".xml")):
        raise HTTPException(
            status_code=400,
            detail="Formato invalido. Envie arquivos .drawio ou .xml.",
        )

    arquivo_id = str(uuid.uuid4())
    safe_name = f"{arquivo_id}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, safe_name)

    content = await file.read()

    with open(file_path, "wb") as f:
        f.write(content)

    try:
        drawio_graph = parse_drawio(content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar arquivo: {str(e)}")

    if not drawio_graph.nodes:
        raise HTTPException(
            status_code=400,
            detail="Nenhum no encontrado no fluxograma. Verifique se o arquivo contem elementos validos.",
        )

    # Build graph
    graph_builder.build(drawio_graph)

    # Generate embeddings and store in Qdrant
    try:
        nodes_data = [
            {"id": n.id, "texto": n.texto, "tipo": n.tipo}
            for n in drawio_graph.nodes
        ]
        edges_data = [
            {"source": e.source, "target": e.target, "label": e.label}
            for e in drawio_graph.edges
        ]

        chunks = EmbeddingService.generate_chunks_from_graph({
            "nodes": nodes_data,
            "edges": edges_data,
        })

        from qdrant_client.http.models import PointStruct

        points = []
        for i, chunk in enumerate(chunks):
            texto = chunk.get("texto", "")
            if not texto:
                continue
            embedding = embedding_service.embed(texto)
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{arquivo_id}_{i}"))
            points.append(
                PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={
                        "arquivo_id": arquivo_id,
                        "node_id": chunk.get("node_id"),
                        "texto": texto,
                        "tipo": chunk.get("tipo", "unknown"),
                        "tipo_chunk": chunk.get("tipo_chunk", "node"),
                        "source": chunk.get("source"),
                        "target": chunk.get("target"),
                    },
                )
            )

        if points:
            vector_store.upsert_batch(points)
    except Exception as e:
        print(f"Warning: Erro ao salvar embeddings: {e}")

    # Store metadata
    uploaded_files[arquivo_id] = {
        "nome": file.filename,
        "path": file_path,
        "total_nodes": len(drawio_graph.nodes),
        "total_edges": len(drawio_graph.edges),
    }

    return UploadResponse(
        arquivo_id=arquivo_id,
        nome=file.filename,
        total_nodes=len(drawio_graph.nodes),
        total_edges=len(drawio_graph.edges),
        mensagem=f"Fluxograma processado com sucesso: {len(drawio_graph.nodes)} nos e {len(drawio_graph.edges)} conexoes encontrados.",
    )


@router.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest):
    if not request.pergunta or not request.pergunta.strip():
        raise HTTPException(status_code=400, detail="Pergunta nao pode estar vazia.")

    if not graph_builder or graph_builder.graph.number_of_nodes() == 0:
        return AskResponse(
            pergunta=request.pergunta,
            resposta="Nenhum fluxograma carregado. Envie um arquivo .drawio primeiro.",
            fonte=None,
        )

    resposta = rag_system.ask(request.pergunta)
    return resposta


@router.get("/graph")
async def get_graph():
    if not graph_builder or graph_builder.graph.number_of_nodes() == 0:
        return JSONResponse(
            content={"nodes": [], "edges": [], "message": "Nenhum grafo carregado."}
        )

    return graph_builder.get_graph_summary()


@router.get("/nodes")
async def get_nodes():
    if not graph_builder:
        return JSONResponse(content={"nodes": []})

    enriched = graph_builder.get_all_nodes_enriched()
    return {
        "nodes": [
            {
                "id": n.id,
                "texto": n.texto,
                "tipo": n.tipo,
                "proximos": n.proximos,
                "anteriores": n.anteriores,
                "caminhos_possiveis": n.caminhos_possiveis,
            }
            for n in enriched
        ]
    }


@router.get("/uploads")
async def list_uploads():
    return {
        "arquivos": [
            {
                "id": aid,
                "nome": info["nome"],
                "total_nodes": info["total_nodes"],
                "total_edges": info["total_edges"],
            }
            for aid, info in uploaded_files.items()
        ]
    }


@router.delete("/uploads/{arquivo_id}")
async def delete_upload(arquivo_id: str):
    if arquivo_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="Arquivo nao encontrado.")

    file_path = uploaded_files[arquivo_id].get("path")
    if file_path and os.path.exists(file_path):
        os.remove(file_path)

    del uploaded_files[arquivo_id]

    return {"mensagem": "Arquivo removido com sucesso."}
