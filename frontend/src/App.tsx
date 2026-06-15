import { useState, useEffect, useCallback } from 'react';
import { Menu, X, Bot } from 'lucide-react';
import Sidebar from './components/Sidebar';
import ChatArea from './components/ChatArea';
import UploadZone from './components/UploadZone';
import ThemeToggle from './components/ThemeToggle';
import * as api from './api/client';
import type { Message, UploadInfo, GraphData, HealthResponse } from './types';

function getInitialTheme(): 'dark' | 'light' {
  if (typeof window !== 'undefined') {
    const stored = localStorage.getItem('theme');
    if (stored === 'light' || stored === 'dark') return stored;
  }
  return 'dark';
}

export default function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploads, setUploads] = useState<UploadInfo[]>([]);
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [graphLoading, setGraphLoading] = useState(false);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [hasFile, setHasFile] = useState(false);
  const [showMobileUpload, setShowMobileUpload] = useState(false);
  const [theme, setTheme] = useState<'dark' | 'light'>(getInitialTheme);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = useCallback(() => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
  }, []);

  useEffect(() => {
    fetchHealth();
    fetchUploads();
    fetchGraph();
  }, []);

  const fetchHealth = async () => {
    try {
      const h = await api.getHealth();
      setHealth(h);
    } catch {
      // server offline
    }
  };

  const fetchUploads = async () => {
    try {
      const data = await api.getUploads();
      setUploads(data.arquivos);
      setHasFile(data.arquivos.length > 0);
    } catch {
      // ignore
    }
  };

  const fetchGraph = async () => {
    setGraphLoading(true);
    try {
      const data = await api.getGraph();
      setGraphData(data);
    } catch {
      setGraphData(null);
    } finally {
      setGraphLoading(false);
    }
  };

  const handleUpload = useCallback(async (file: File) => {
    setIsUploading(true);
    try {
      const result = await api.uploadFile(file);
      setHasFile(true);
      await fetchUploads();
      await fetchGraph();
    } finally {
      setIsUploading(false);
    }
  }, []);

  const handleDeleteUpload = useCallback(async (id: string) => {
    try {
      await api.deleteUpload(id);
      await fetchUploads();
      await fetchGraph();
      if (uploads.length <= 1) {
        setHasFile(false);
        setMessages([]);
      }
    } catch {
      // ignore
    }
  }, [uploads]);

  const handleSend = useCallback(async (text: string) => {
    const userMsg: Message = {
      id: Date.now().toString(),
      tipo: 'user',
      texto: text,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const response = await api.askQuestion(text);
      const assistantMsg: Message = {
        id: (Date.now() + 1).toString(),
        tipo: 'assistant',
        texto: response.resposta || 'Nao encontrei essa informacao no fluxograma.',
        fonte: response.fonte,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        tipo: 'assistant',
        texto: err.message || 'Erro ao processar sua pergunta.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  return (
    <div className="h-screen flex overflow-hidden bg-dark-900">
      {/* Sidebar */}
      <aside
        className={`${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        } fixed lg:relative lg:translate-x-0 z-30 w-80 h-full transition-transform duration-300 ease-in-out`}
      >
        <Sidebar
          uploads={uploads}
          graphData={graphData}
          health={health}
          isUploading={isUploading}
          onUpload={handleUpload}
          onDeleteUpload={handleDeleteUpload}
          graphLoading={graphLoading}
        />
      </aside>

      {/* Overlay for mobile */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-20 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="h-14 border-b border-dark-700 flex items-center px-4 gap-3 bg-dark-800/50 backdrop-blur-sm flex-shrink-0">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-1.5 rounded-lg hover:bg-dark-700 transition-colors lg:hidden"
          >
            {sidebarOpen ? <X className="w-5 h-5 text-dark-200" /> : <Menu className="w-5 h-5 text-dark-200" />}
          </button>

          <Bot className="w-5 h-5 text-blue-400 hidden sm:block" />
          <h1 className="text-sm font-medium text-gray-200 hidden sm:block">
            IA RAG - Leitor de Draw.io
          </h1>

          <div className="flex-1" />

          <ThemeToggle theme={theme} onToggle={toggleTheme} />

          {/* Mobile upload button */}
          <button
            onClick={() => setShowMobileUpload(!showMobileUpload)}
            className="sm:hidden px-3 py-1.5 text-xs bg-dark-700 hover:bg-dark-600 rounded-lg transition-colors text-dark-200"
          >
            {showMobileUpload ? 'Fechar' : 'Upload'}
          </button>
        </header>

        {/* Mobile upload area */}
        {showMobileUpload && (
          <div className="sm:hidden p-4 border-b border-dark-700 bg-dark-800/50">
            <UploadZone onUpload={handleUpload} isLoading={isUploading} />
          </div>
        )}

        {/* Chat */}
        <div className="flex-1 overflow-hidden">
          <ChatArea
            messages={messages}
            onSend={handleSend}
            isLoading={isLoading}
            hasFile={hasFile}
          />
        </div>
      </main>
    </div>
  );
}
