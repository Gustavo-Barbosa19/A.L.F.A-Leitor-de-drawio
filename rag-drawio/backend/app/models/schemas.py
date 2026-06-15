from pydantic import BaseModel, Field
from typing import Optional, List, Any


class DrawioNode(BaseModel):
    id: str
    texto: str
    tipo: str = Field(default="processo")
    parent: Optional[str] = None
    style: Optional[str] = None


class DrawioEdge(BaseModel):
    source: str
    target: str
    label: Optional[str] = None
    style: Optional[str] = None


class DrawioGraph(BaseModel):
    nodes: List[DrawioNode] = []
    edges: List[DrawioEdge] = []


class NodeEnriched(BaseModel):
    id: str
    texto: str
    tipo: str
    proximos: List[str] = []
    anteriores: List[str] = []
    fluxo_relacionado: Optional[str] = None
    caminhos_possiveis: List[str] = []


class AskRequest(BaseModel):
    pergunta: str
    arquivo_id: Optional[str] = None


class AskResponse(BaseModel):
    pergunta: str
    resposta: str
    fonte: Optional[dict] = None


class UploadResponse(BaseModel):
    arquivo_id: str
    nome: str
    total_nodes: int
    total_edges: int
    mensagem: str


class HealthResponse(BaseModel):
    status: str
    versao: str
    qdrant_connected: bool
    arquivos_carregados: int
