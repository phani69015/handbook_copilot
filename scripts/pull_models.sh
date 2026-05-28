#!/bin/bash
# Pull required Ollama models on first start.
# Run this after the Ollama container is healthy.
#
# Usage: ./scripts/pull_models.sh

set -e

OLLAMA_HOST="${OLLAMA_BASE_URL:-http://localhost:11434}"
LLM_MODEL="${OLLAMA_LLM_MODEL:-llama3.1:8b}"
EMBED_MODEL="${OLLAMA_EMBED_MODEL:-nomic-embed-text}"

echo "============================================"
echo "Pulling Ollama models..."
echo "  Host:        $OLLAMA_HOST"
echo "  LLM Model:   $LLM_MODEL"
echo "  Embed Model: $EMBED_MODEL"
echo "============================================"

# Wait for Ollama to be ready
echo "Waiting for Ollama to be ready..."
until curl -s "$OLLAMA_HOST/api/tags" > /dev/null 2>&1; do
    echo "  Ollama not ready, retrying in 5s..."
    sleep 5
done
echo "Ollama is ready!"

# Pull embedding model first (smaller, faster)
echo ""
echo "Pulling embedding model: $EMBED_MODEL"
curl -s "$OLLAMA_HOST/api/pull" -d "{\"name\": \"$EMBED_MODEL\"}" | while read -r line; do
    status=$(echo "$line" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('status',''))" 2>/dev/null || echo "")
    if [ -n "$status" ]; then
        echo "  $status"
    fi
done

# Pull LLM model
echo ""
echo "Pulling LLM model: $LLM_MODEL"
curl -s "$OLLAMA_HOST/api/pull" -d "{\"name\": \"$LLM_MODEL\"}" | while read -r line; do
    status=$(echo "$line" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('status',''))" 2>/dev/null || echo "")
    if [ -n "$status" ]; then
        echo "  $status"
    fi
done

echo ""
echo "============================================"
echo "All models pulled successfully!"
echo "============================================"
