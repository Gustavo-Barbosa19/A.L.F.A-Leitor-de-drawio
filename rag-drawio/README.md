# IA RAG - Leitor de Draw.io

Sistema de IA especializado em leitura e consulta de fluxogramas **draw.io (.drawio)** usando RAG (Retrieval-Augmented Generation) com Graph RAG.

## Stack

| Camada | Tecnologia |
|---|---|
| Frontend | React + TypeScript + TailwindCSS |
| Backend | Python + FastAPI |
| Vector DB | Qdrant |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Graph | networkx |
| Parser XML | xml.etree.ElementTree |
| LLM | OpenAI API (gpt-4o-mini) |

## Estrutura do Projeto

```
rag-drawio/
├── backend/
│   ├── app/
│   │   ├── main.py                 # Entrypoint FastAPI
│   │   ├── api/routes.py           # Endpoints REST
│   │   ├── parser/drawio_parser.py # Parser de arquivos .drawio
│   │   ├── graph/graph_builder.py  # Grafo navegavel com networkx
│   │   ├── embeddings/             # Servico de embeddings
│   │   ├── vector_store/           # Integracao com Qdrant
│   │   ├── rag/
│   │   │   ├── graph_rag.py        # Graph RAG + LLM
│   │   │   └── guardrails.py       # Sistema anti-alucinacao
│   │   └── models/schemas.py       # Pydantic schemas
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.tsx                 # Componente principal
│   │   ├── components/
│   │   │   ├── ChatArea.tsx        # Area de chat estilo ChatGPT
│   │   │   ├── UploadZone.tsx      # Upload drag and drop
│   │   │   ├── Sidebar.tsx         # Sidebar com grafo e arquivos
│   │   │   └── FlowVisualizer.tsx  # Visualizacao do fluxograma
│   │   ├── api/client.ts           # Cliente HTTP
│   │   └── types/index.ts          # Tipos TypeScript
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
└── .env.example
```

## Funcionalidades

### Core
- **Upload** de arquivos .drawio via drag and drop
- **Parser** completo do XML draw.io (nos, conexoes, decisoes)
- **Graph RAG**: busca semantica + navegacao estrutural no grafo
- **Anti-alucinacao**: respostas estritamente baseadas no fluxograma
- **Chunking inteligente** baseado em nos e subfluxos
- **Qdrant** para armazenamento vetorial

### API
- `POST /api/upload` - Upload de fluxograma
- `POST /api/ask` - Pergunta sobre o fluxograma
- `GET /api/graph` - Dados do grafo
- `GET /api/nodes` - Todos os nos enriquecidos
- `GET /api/health` - Status do servidor

### Resposta da IA
```json
{
  "pergunta": "O que vem depois de fotografar as conexoes?",
  "resposta": "No encontrado: Fotografar conexoes\nProximo(s) passo(s): Salvar conexoes identificadas",
  "fonte": {
    "node_id": "123",
    "texto_original": "Fotografar conexoes",
    "proximo": "Salvar conexoes identificadas"
  }
}
```

## Como Executar

### Com Docker (recomendado)

```bash
# Clone e entre no diretorio
cd rag-drawio

# Copie o .env e configure
cp .env.example .env
# Edite .env com sua OPENAI_API_KEY (opcional)

# Suba os servicos
docker-compose up -d

# Acesse:
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### Sem Docker (desenvolvimento)

**Backend:**
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Inicie o Qdrant (necessario Docker para o banco)
docker run -d -p 6333:6333 qdrant/qdrant

# Inicie o backend
python -m app.main
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Arquitetura RAG

1. **Upload** -> Parse do XML draw.io -> Construcao do grafo (networkx)
2. **Embeddings** -> Gerados para cada no/chunk -> Salvos no Qdrant
3. **Pergunta** -> Busca semantica no Qdrant + busca direta no grafo
4. **Validacao** -> Navegacao nas conexoes reais do grafo
5. **Resposta** -> Construida exclusivamente com dados encontrados
6. **Opcional** -> Se OPENAI_API_KEY configurada, usa LLM como fallback

## Anti-Alucinacao

O sistema possui multiplas camadas de guardrails:

- **Busca direta no grafo**: localiza o no exato mencionado na pergunta
- **Busca semantica**: encontra o no mais relevante via embeddings
- **Navegacao estrutural**: valida que as conexoes existem no grafo
- **Resposta segura**: construida apenas com `texto`, `proximos` e `anteriores` reais
- **LLM com contexto**: se usado, recebe o grafo completo e instrucao para nao inventar

Se a informacao nao existe no fluxograma, a resposta e:
> "Nao encontrei essa informacao no fluxograma."

## Exemplos de Uso

```bash
# Health check
curl http://localhost:8000/api/health

# Upload
curl -X POST -F "file=@meu_fluxo.drawio" http://localhost:8000/api/upload

# Perguntar
curl -X POST -H "Content-Type: application/json" \
  -d '{"pergunta": "Qual o primeiro passo do fluxo?"}' \
  http://localhost:8000/api/ask

# Ver grafo
curl http://localhost:8000/api/graph

# Ver nos
curl http://localhost:8000/api/nodes
```

## Preparado para

- Multiplos fluxogramas simultaneos
- Versionamento de arquivos
- Comparacao entre fluxos
- Exportacao JSON
- Cache de embeddings
- Autenticacao via API Key
