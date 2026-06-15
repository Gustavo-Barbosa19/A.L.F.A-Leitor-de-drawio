#!/bin/bash
# ============================================
# Script para preparar deploy no Hugging Face
# ============================================
# Uso: bash scripts/deploy-hf.sh <diretorio_destino>
# Exemplo: bash scripts/deploy-hf.sh ../meu-hf-space

set -e

DEST="${1:-./hf-deploy}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=========================================="
echo "  Preparando deploy para Hugging Face"
echo "  Destino: $DEST"
echo "=========================================="

# Create destination
mkdir -p "$DEST"

# Copy all project files
echo "[1/3] Copiando arquivos do projeto..."
rsync -av --exclude='node_modules' \
          --exclude='__pycache__' \
          --exclude='*.pyc' \
          --exclude='.git' \
          --exclude='.env' \
          --exclude='venv' \
          --exclude='hf-deploy' \
          "$PROJECT_DIR/" "$DEST/"

# Copy HF Dockerfile as main Dockerfile
echo "[2/3] Configurando Dockerfile para HF..."
cp "$PROJECT_DIR/Dockerfile.hf" "$DEST/Dockerfile"

# Create HF README metadata
echo "[3/3] Criando README do Space..."
cat > "$DEST/README.md" << 'EOF'
---
title: Leitor de Fluxo Draw.io
emoji: 📊
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# IA RAG - Leitor de Draw.io

Sistema de IA especializado em leitura e consulta de fluxogramas **draw.io (.drawio)** usando RAG com Graph RAG.

## Como usar

1. Faça upload de um arquivo `.drawio`
2. Pergunte sobre o fluxograma em linguagem natural
3. A IA responde exclusivamente com base no conteúdo do fluxograma

## Stack

- **Frontend:** React + TypeScript + TailwindCSS
- **Backend:** Python + FastAPI
- **Vector DB:** Embutido (fallback in-memory)
- **Embeddings:** sentence-transformers (fallback dummy)
- **Graph:** networkx
- **Parser:** XML draw.io
EOF

echo ""
echo "=========================================="
echo "  Deploy preparado em: $DEST"
echo "=========================================="
echo ""
echo "Proximos passos:"
echo "  1. Crie um Space em https://huggingface.co/new-space"
echo "     - SDK: Docker"
echo "  2. Envie os arquivos:"
echo "     cd $DEST"
echo "     git init"
echo "     git add ."
echo "     git commit -m 'Initial deploy'"
echo "     git remote add origin https://huggingface.co/spaces/SEU_USUARIO/SEU_SPACE"
echo "     git push -u origin main"
echo ""
echo "  Ou use a CLI do HF:"
echo "     huggingface-cli upload SEU_USUARIO/SEU_SPACE $DEST"
