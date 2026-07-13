#!/bin/bash
set -e

echo "=========================================="
echo "  Hermes LLM - Setup para GitHub Codespaces"
echo "=========================================="
echo ""

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar se Docker está disponível
if ! command -v docker &> /dev/null; then
    echo -e "${RED}ERRO: Docker não encontrado.${NC}"
    echo "Verifique se o Codespaces tem Docker habilitado."
    exit 1
fi

echo -e "${GREEN}[1/4] Docker detectado.${NC}"

# Verificar se docker-compose está disponível
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}ERRO: docker-compose não encontrado.${NC}"
    exit 1
fi

echo -e "${GREEN}[2/4] docker-compose detectado.${NC}"

# Subir serviços
echo -e "${YELLOW}[3/4] Subindo Ollama + Open WebUI...${NC}"
docker compose up -d

# Esperar Ollama ficar pronto
echo -e "${YELLOW}Aguardando Ollama inicializar...${NC}"
sleep 5

# Verificar se Ollama está respondendo
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo -e "${YELLOW}Aguardando Ollama ficar totalmente pronto...${NC}"
    sleep 10
fi

# Baixar o modelo Hermes
echo -e "${YELLOW}[4/4] Baixando modelo Hermes 2 Mistral (7B)...${NC}"
echo "Isso pode demorar alguns minutos dependendo da conexão..."
docker exec -it hermes-ollama ollama pull hermes2-mistral:7b

echo ""
echo -e "${GREEN}=========================================="
echo "  Setup concluído!"
echo "==========================================${NC}"
echo ""
echo "Acesse a interface web em:"
echo -e "  ${GREEN}https://${CODESPACE_NAME}-8080.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}${NC}"
echo ""
echo "Ou, se port forwarding não estiver automático:"
echo "  1. Clique em 'Ports' na barra inferior do Codespaces"
echo "  2. Encontre a porta 8080"
echo "  3. Clique no ícone de olho para torná-la pública"
echo "  4. Acesse a URL exibida"
echo ""
echo "Para ver os logs:"
echo "  docker compose logs -f"
echo ""
echo "Para parar:"
echo "  docker compose down"
echo ""
