export interface DrawioNode {
  id: string;
  texto: string;
  tipo: string;
  proximos?: string[];
  anteriores?: string[];
  caminhos_possiveis?: string[];
}

export interface DrawioEdge {
  source: string;
  target: string;
  label?: string;
}

export interface GraphData {
  total_nodes: number;
  total_edges: number;
  tipos: Record<string, number>;
  nodes: {
    id: string;
    texto: string;
    tipo: string;
  }[];
}

export interface UploadResponse {
  arquivo_id: string;
  nome: string;
  total_nodes: number;
  total_edges: number;
  mensagem: string;
}

export interface AskResponse {
  pergunta: string;
  resposta: string;
  fonte: {
    node_id?: string;
    texto_original?: string;
    proximo?: string;
    score?: number;
  } | null;
}

export interface HealthResponse {
  status: string;
  versao: string;
  qdrant_connected: boolean;
  arquivos_carregados: number;
}

export interface UploadInfo {
  id: string;
  nome: string;
  total_nodes: number;
  total_edges: number;
}

export interface Message {
  id: string;
  tipo: 'user' | 'assistant';
  texto: string;
  fonte?: AskResponse['fonte'];
  timestamp: Date;
}
