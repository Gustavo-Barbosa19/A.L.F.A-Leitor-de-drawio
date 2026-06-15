#!/bin/bash
# Exemplos de requests para a API
# Execute: chmod +x examples_requests.sh && ./examples_requests.sh

BASE_URL="http://localhost:8000/api"

echo "=========================================="
echo "  IA RAG - Exemplos de Requests"
echo "=========================================="
echo ""

# 1. Health Check
echo "[1] Health Check"
curl -s "$BASE_URL/health" | python -m json.tool
echo ""

# 2. Upload de arquivo drawio
echo "[2] Upload de fluxograma"
curl -s -X POST -F "file=@exemplo_fluxo.drawio" "$BASE_URL/upload" | python -m json.tool
echo ""

# 3. Perguntar sobre o fluxograma
echo "[3] Perguntar sobre o fluxo"
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"pergunta": "Qual o primeiro passo do fluxograma?"}' \
  "$BASE_URL/ask" | python -m json.tool
echo ""

# 4. Perguntar sobre etapa especifica
echo "[4] Perguntar sobre etapa especifica"
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"pergunta": "O que vem depois de fotografar as conexoes?"}' \
  "$BASE_URL/ask" | python -m json.tool
echo ""

# 5. Ver grafo completo
echo "[5] Ver dados do grafo"
curl -s "$BASE_URL/graph" | python -m json.tool
echo ""

# 6. Ver nos enriquecidos
echo "[6] Ver nos enriquecidos"
curl -s "$BASE_URL/nodes" | python -m json.tool
echo ""

# 7. Listar uploads
echo "[7] Listar uploads"
curl -s "$BASE_URL/uploads" | python -m json.tool
echo ""

echo "=========================================="
echo "  Testes concluidos!"
echo "=========================================="
