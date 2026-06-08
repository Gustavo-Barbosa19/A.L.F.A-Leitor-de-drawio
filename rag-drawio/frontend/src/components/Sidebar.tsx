import { useState } from 'react';
import { Upload, FileText, Trash2, Database, Layers, BarChart3, Loader2 } from 'lucide-react';
import UploadZone from './UploadZone';
import FlowVisualizer from './FlowVisualizer';
import type { UploadInfo, GraphData, HealthResponse } from '../types';

interface SidebarProps {
  uploads: UploadInfo[];
  graphData: GraphData | null;
  health: HealthResponse | null;
  isUploading: boolean;
  onUpload: (file: File) => Promise<void>;
  onDeleteUpload: (id: string) => Promise<void>;
  graphLoading: boolean;
}

export default function Sidebar({
  uploads,
  graphData,
  health,
  isUploading,
  onUpload,
  onDeleteUpload,
  graphLoading,
}: SidebarProps) {
  const [showUpload, setShowUpload] = useState(false);

  return (
    <div className="h-full flex flex-col bg-dark-800 border-r border-dark-700">
      <div className="p-4 border-b border-dark-700">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <Layers className="w-5 h-5 text-blue-400" />
            <h2 className="font-semibold text-gray-200">Draw.io RAG</h2>
          </div>
          <button
            onClick={() => setShowUpload(!showUpload)}
            className="p-1.5 rounded-lg hover:bg-dark-600 transition-colors"
            title="Upload de fluxograma"
          >
            <Upload className="w-4 h-4 text-dark-300" />
          </button>
        </div>

        {showUpload && (
          <div className="mb-3 animate-fade-in">
            <UploadZone onUpload={onUpload} isLoading={isUploading} />
          </div>
        )}

        {!showUpload && (
          <div
            onClick={() => setShowUpload(true)}
            className="upload-zone cursor-pointer py-3"
          >
            <div className="flex items-center justify-center gap-2 text-sm text-dark-300">
              <Upload className="w-4 h-4" />
              <span>Clique para enviar .drawio</span>
            </div>
          </div>
        )}
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <FlowVisualizer graphData={graphData} isLoading={graphLoading} />

        {uploads.length > 0 && (
          <div className="bg-dark-800 rounded-xl border border-dark-700 overflow-hidden">
            <div className="flex items-center gap-2 px-4 py-3 border-b border-dark-700">
              <FileText className="w-4 h-4 text-blue-400" />
              <span className="text-sm font-medium text-gray-200">Arquivos</span>
              <span className="text-xs text-dark-400 ml-auto">{uploads.length}</span>
            </div>
            <div className="divide-y divide-dark-700">
              {uploads.map((up) => (
                <div key={up.id} className="flex items-center gap-2 px-4 py-2.5 hover:bg-dark-700/50 group">
                  <FileText className="w-3.5 h-3.5 text-dark-400" />
                  <div className="flex-1 min-w-0">
                    <p className="text-xs text-gray-300 truncate">{up.nome}</p>
                    <p className="text-[10px] text-dark-400">
                      {up.total_nodes} nós · {up.total_edges} conexões
                    </p>
                  </div>
                  <button
                    onClick={() => onDeleteUpload(up.id)}
                    className="p-1 rounded hover:bg-dark-600 opacity-0 group-hover:opacity-100 transition-all"
                    title="Remover"
                  >
                    <Trash2 className="w-3 h-3 text-red-400" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {health && (
          <div className="bg-dark-800 rounded-xl border border-dark-700 p-4">
            <div className="flex items-center gap-2 mb-2">
              <BarChart3 className="w-4 h-4 text-blue-400" />
              <span className="text-sm font-medium text-gray-200">Servidor</span>
            </div>
            <div className="space-y-1.5 text-xs">
              <div className="flex justify-between">
                <span className="text-dark-400">Status</span>
                <span className={health.status === 'ok' ? 'text-green-400' : 'text-red-400'}>
                  {health.status === 'ok' ? 'Online' : 'Offline'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-dark-400">Qdrant</span>
                <span className={health.qdrant_connected ? 'text-green-400' : 'text-red-400'}>
                  {health.qdrant_connected ? 'Conectado' : 'Desconectado'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-dark-400">Arquivos</span>
                <span className="text-gray-300">{health.arquivos_carregados}</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
