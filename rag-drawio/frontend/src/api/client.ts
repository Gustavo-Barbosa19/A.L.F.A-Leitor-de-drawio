import type { UploadResponse, AskResponse, GraphData, HealthResponse, UploadInfo } from '../types';

const API_BASE = import.meta.env.VITE_API_URL || '/api';

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Erro desconhecido' }));
    throw new Error(err.detail || `Erro ${res.status}`);
  }
  return res.json();
}

export async function uploadFile(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE}/upload`, { method: 'POST', body: formData });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Erro ao fazer upload' }));
    throw new Error(err.detail || `Erro ${res.status}`);
  }
  return res.json();
}

export async function askQuestion(pergunta: string, arquivo_id?: string): Promise<AskResponse> {
  return request<AskResponse>('/ask', {
    method: 'POST',
    body: JSON.stringify({ pergunta, arquivo_id }),
  });
}

export async function getGraph(): Promise<GraphData> {
  return request<GraphData>('/graph');
}

export async function getNodes() {
  return request<{ nodes: any[] }>('/nodes');
}

export async function getHealth(): Promise<HealthResponse> {
  return request<HealthResponse>('/health');
}

export async function getUploads(): Promise<{ arquivos: UploadInfo[] }> {
  return request<{ arquivos: UploadInfo[] }>('/uploads');
}

export async function deleteUpload(arquivo_id: string): Promise<void> {
  await fetch(`${API_BASE}/uploads/${arquivo_id}`, { method: 'DELETE' });
}
