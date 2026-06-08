import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2, AlertCircle } from 'lucide-react';
import type { Message } from '../types';

interface ChatAreaProps {
  messages: Message[];
  onSend: (message: string) => Promise<void>;
  isLoading: boolean;
  hasFile: boolean;
}

export default function ChatArea({ messages, onSend, isLoading, hasFile }: ChatAreaProps) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading || !hasFile) return;
    const text = input.trim();
    setInput('');
    await onSend(text);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-dark-300">
            <Bot className="w-12 h-12 mb-4 text-dark-400" />
            <p className="text-lg font-medium text-dark-200">
              {hasFile ? 'Faça uma pergunta sobre o fluxograma' : 'Envie um arquivo .drawio para começar'}
            </p>
            <p className="text-sm mt-2">
              {hasFile
                ? 'Pergunte sobre etapas, conexões ou decisões do fluxo.'
                : 'Use a área de upload ao lado ou no botão superior.'}
            </p>
          </div>
        ) : (
          messages.map((msg) => (
            <div
              key={msg.id}
              className={`message-enter flex gap-3 ${
                msg.tipo === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              {msg.tipo === 'assistant' && (
                <div className="w-8 h-8 rounded-full bg-blue-600/20 flex items-center justify-center flex-shrink-0 mt-1">
                  <Bot className="w-4 h-4 text-blue-400" />
                </div>
              )}

              <div
                className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                  msg.tipo === 'user'
                    ? 'bg-blue-600 text-white rounded-br-md'
                    : 'bg-dark-700 text-gray-200 rounded-bl-md border border-dark-600'
                }`}
              >
                <p className="text-sm whitespace-pre-wrap leading-relaxed">{msg.texto}</p>
                {msg.fonte && msg.tipo === 'assistant' && (
                  <div className="mt-2 pt-2 border-t border-dark-600 text-xs text-dark-300">
                    {msg.fonte.node_id && <span className="mr-3">Nó: {msg.fonte.node_id}</span>}
                    {msg.fonte.score && <span>Score: {(msg.fonte.score * 100).toFixed(0)}%</span>}
                  </div>
                )}
                <span className="text-[10px] text-dark-400 block mt-1">
                  {msg.timestamp.toLocaleTimeString()}
                </span>
              </div>

              {msg.tipo === 'user' && (
                <div className="w-8 h-8 rounded-full bg-dark-600 flex items-center justify-center flex-shrink-0 mt-1">
                  <User className="w-4 h-4 text-gray-300" />
                </div>
              )}
            </div>
          ))
        )}

        {isLoading && (
          <div className="message-enter flex gap-3">
            <div className="w-8 h-8 rounded-full bg-blue-600/20 flex items-center justify-center flex-shrink-0">
              <Loader2 className="w-4 h-4 text-blue-400 animate-spin" />
            </div>
            <div className="bg-dark-700 rounded-2xl rounded-bl-md px-4 py-3 border border-dark-600">
              <div className="flex gap-1.5">
                <span className="w-2 h-2 bg-dark-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <span className="w-2 h-2 bg-dark-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <span className="w-2 h-2 bg-dark-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="border-t border-dark-700 px-4 py-3">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={hasFile ? 'Pergunte sobre o fluxograma...' : 'Envie um arquivo primeiro...'}
            disabled={!hasFile || isLoading}
            rows={1}
            className="input-field resize-none"
            style={{ minHeight: '44px', maxHeight: '120px' }}
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading || !hasFile}
            className="btn-primary px-3 flex items-center justify-center"
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </form>
        {!hasFile && (
          <p className="text-xs text-dark-400 mt-2 flex items-center gap-1">
            <AlertCircle className="w-3 h-3" />
            Envie um fluxograma para começar a perguntar
          </p>
        )}
      </div>
    </div>
  );
}
