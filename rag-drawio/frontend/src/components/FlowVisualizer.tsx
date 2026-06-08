import { useState } from 'react';
import { ChevronDown, ChevronRight, GitBranch, Circle, Square, Diamond } from 'lucide-react';
import type { GraphData } from '../types';

interface FlowVisualizerProps {
  graphData: GraphData | null;
  isLoading: boolean;
}

function TipoIcon({ tipo }: { tipo: string }) {
  switch (tipo) {
    case 'decisao':
      return <Diamond className="w-3.5 h-3.5 text-yellow-400" />;
    case 'inicio':
      return <Circle className="w-3.5 h-3.5 text-green-400" />;
    case 'fim':
      return <Square className="w-3.5 h-3.5 text-red-400" />;
    default:
      return <GitBranch className="w-3.5 h-3.5 text-blue-400" />;
  }
}

export default function FlowVisualizer({ graphData, isLoading }: FlowVisualizerProps) {
  const [expanded, setExpanded] = useState(true);

  if (isLoading) {
    return (
      <div className="bg-dark-800 rounded-xl border border-dark-700 p-4 animate-pulse">
        <div className="h-4 bg-dark-600 rounded w-1/3 mb-3" />
        <div className="space-y-2">
          <div className="h-3 bg-dark-600 rounded w-full" />
          <div className="h-3 bg-dark-600 rounded w-2/3" />
        </div>
      </div>
    );
  }

  if (!graphData || graphData.nodes.length === 0) return null;

  return (
    <div className="bg-dark-800 rounded-xl border border-dark-700 overflow-hidden">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between px-4 py-3 hover:bg-dark-700/50 transition-colors"
      >
        <div className="flex items-center gap-2">
          <GitBranch className="w-4 h-4 text-blue-400" />
          <span className="text-sm font-medium text-gray-200">Fluxograma</span>
          <span className="text-xs text-dark-400">
            {graphData.total_nodes} nós · {graphData.total_edges} conexões
          </span>
        </div>
        {expanded ? <ChevronDown className="w-4 h-4 text-dark-300" /> : <ChevronRight className="w-4 h-4 text-dark-300" />}
      </button>

      {expanded && (
        <div className="px-4 pb-3 space-y-1 max-h-64 overflow-y-auto">
          {graphData.nodes.map((node) => (
            <div
              key={node.id}
              className="flex items-center gap-2 px-2 py-1.5 rounded-lg hover:bg-dark-700/50 text-sm"
            >
              {node.tipo === 'decisao' ? (
                <div className="w-4 h-4 rotate-45 border border-yellow-500/50 flex items-center justify-center flex-shrink-0">
                  <span className="rotate-45 text-[8px] text-yellow-400">?</span>
                </div>
              ) : node.tipo === 'inicio' ? (
                <div className="w-3 h-3 rounded-full bg-green-500/30 border border-green-500/50 flex-shrink-0" />
              ) : node.tipo === 'fim' ? (
                <div className="w-3 h-3 bg-red-500/30 border border-red-500/50 flex-shrink-0" />
              ) : (
                <div className="w-3 h-3 rounded-sm bg-blue-500/30 border border-blue-500/50 flex-shrink-0" />
              )}
              <span className="text-dark-200 truncate flex-1">{node.texto}</span>
              <span className="text-[10px] text-dark-400 uppercase">{node.tipo}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
