import { useState, useRef, useCallback } from 'react';
import { Upload, FileText, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';

interface UploadZoneProps {
  onUpload: (file: File) => Promise<void>;
  isLoading: boolean;
}

export default function UploadZone({ onUpload, isLoading }: UploadZoneProps) {
  const [dragActive, setDragActive] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [statusMessage, setStatusMessage] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);
  const dragCounter = useRef(0);

  const handleFile = useCallback(async (file: File) => {
    if (!file.name.endsWith('.drawio') && !file.name.endsWith('.xml')) {
      setUploadStatus('error');
      setStatusMessage('Formato inválido. Use arquivos .drawio ou .xml.');
      return;
    }
    try {
      await onUpload(file);
      setUploadStatus('success');
      setStatusMessage(`"${file.name}" carregado com sucesso!`);
    } catch (err: any) {
      setUploadStatus('error');
      setStatusMessage(err.message || 'Erro ao processar arquivo.');
    }
    setTimeout(() => {
      setUploadStatus('idle');
      setStatusMessage('');
    }, 4000);
  }, [onUpload]);

  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    dragCounter.current++;
    if (e.dataTransfer.items && e.dataTransfer.items.length > 0) {
      setDragActive(true);
    }
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    dragCounter.current--;
    if (dragCounter.current === 0) {
      setDragActive(false);
    }
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    dragCounter.current = 0;
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFile(files[0]);
    }
  }, [handleFile]);

  return (
    <div className="space-y-3">
      <div
        className={`upload-zone cursor-pointer ${dragActive ? 'active' : ''} ${
          isLoading ? 'opacity-50 pointer-events-none' : ''
        }`}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".drawio,.xml"
          className="hidden"
          onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
        />

        {isLoading ? (
          <div className="flex flex-col items-center gap-3 py-4">
            <Loader2 className="w-10 h-10 text-blue-400 animate-spin" />
            <p className="text-dark-200 text-sm">Processando fluxograma...</p>
          </div>
        ) : uploadStatus === 'success' ? (
          <div className="flex flex-col items-center gap-3 py-4">
            <CheckCircle className="w-10 h-10 text-green-400" />
            <p className="text-green-400 text-sm font-medium">{statusMessage}</p>
          </div>
        ) : uploadStatus === 'error' ? (
          <div className="flex flex-col items-center gap-3 py-4">
            <AlertCircle className="w-10 h-10 text-red-400" />
            <p className="text-red-400 text-sm">{statusMessage}</p>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-3 py-4">
            <div className="p-3 bg-dark-600 rounded-full">
              <Upload className="w-6 h-6 text-blue-400" />
            </div>
            <div className="text-center">
              <p className="text-gray-200 font-medium">
                Arraste seu arquivo .drawio aqui
              </p>
              <p className="text-dark-300 text-sm mt-1">ou clique para selecionar</p>
            </div>
            <div className="flex items-center gap-2 text-xs text-dark-300">
              <FileText className="w-3 h-3" />
              <span>Suporta .drawio e .xml</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
