# Hermes LLM no GitHub Codespaces

Este repositório contém a configuração para rodar o modelo **Hermes 2** (NousResearch) com interface web no GitHub Codespaces.

## Pré-requisitos

- GitHub Codespaces ativo (endereço: `https://symmetrical-space-parakeet-5g74pq7q99vjhv4rq-9119.app.github.dev`)
- Codespaces com pelo menos **4 cores** e **8GB RAM** (recomendado: 8GB+)
- Docker habilitado no Codespaces (verifique com `docker --version`)

## Modelo

O modelo padrão configurado é o **Hermes 2 Mistral 7B**, que é o mais leve e rápido para rodar em CPUs/GPUs de Codespaces.

Se você quiser um modelo maior:
- `hermes2-mistral:13b` - Melhor qualidade, mais lento
- `hermes2-pro:7b` - Versão Pro, melhor para tool use

## Instalação Rápida

### Opção 1: Docker (Recomendada)

1. Abra o terminal no Codespaces
2. Navegue até este repositório
3. Torne o script executável:
   ```bash
   chmod +x setup-hermes.sh
   ```
4. Execute o setup:
   ```bash
   ./setup-hermes.sh
   ```

5. Aguarde o download do modelo (5-15 minutos dependendo da conexão)

### Opção 2: Sem Docker (CPU only)

Se Docker não estiver disponível, use o setup alternativo:

```bash
chmod +x setup-hermes-cpu.sh
./setup-hermes-cpu.sh
```

Este script usa `llama-cpp-python` com quantização 4-bit para rodar diretamente em Python.

## Acessando pelo Navegador

### Método 1: Port Forwarding Automático (Recomendado)

Após o setup, o Open WebUI estará na porta **8080**.

1. Na barra inferior do Codespaces, clique na aba **PORTS**
2. Procure pela porta **8080**
3. Clique no ícone de **olho** (tornar público)
4. Clique no ícone de **globo** para abrir no navegador
5. Acesse a URL fornecida

### Método 2: URL Direta (Codespaces)

Use este padrão de URL:

```
https://<seu-codespace>-8080.app.github.dev
```

No seu caso:
```
https://symmetrical-space-parakeet-5g74pq7q99vjhv4rq-9119-8080.app.github.dev
```

**Nota:** A porta `-9119` no seu endereço atual é a porta do editor de arquivos. Você precisará da porta `-8080` para a interface web.

## Uso da Interface Web

1. Na tela de login do Open WebUI, clique em **"Sign Up"** para criar uma conta local
2. Após login, clique no ícone de **engrenagem** (Admin Panel)
3. Em **Connections**, verifique se o Ollama está conectado
4. Em **Models**, você verá o modelo `hermes2-mistral:7b` disponível
5. Selecione o modelo e comece a conversar!

## Comandos Úteis

### Ver logs dos containers
```bash
docker compose logs -f
```

### Parar os serviços
```bash
docker compose down
```

### Reiniciar
```bash
docker compose up -d
```

### Baixar outro modelo
```bash
docker exec -it hermes-ollama ollama pull hermes2-mistral:13b
```

### Listar modelos instalados
```bash
docker exec -it hermes-ollama ollama list
```

### Testar API diretamente
```bash
curl http://localhost:11434/api/generate -d '{
  "model": "hermes2-mistral:7b",
  "prompt": "Why is the sky blue?"
}'
```

## Solução de Problemas

### Codespaces não tem Docker

Use a Opção 2 (setup sem Docker) ou:
```bash
# Instalar Ollama manualmente
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve &
ollama pull hermes2-mistral:7b
```

Depois acesse `https://<codespace>-11434.app.github.dev` para a API, ou configure um proxy reverso.

### Porta 8080 não aparece nos Ports

Execute manualmente:
```bash
docker compose up -d
# Ou sem Docker:
python3 webui-hermes.py --port 8080
```

Depois clique em "Ports" > "Add Port" > digite 8080 > Add.

### Modelo muito lento

- Verifique se há GPU disponível: `nvidia-smi`
- Use modelo menor: `hermes2-mistral:7b` (ao invés de 13b)
- Considere desligar outras aplicações no Codespaces

### Erro de memória

O Codespaces pode ter limite de RAM. Se ocorrer erro de OOM:
```bash
# Verificar uso
free -h

# Parar containers
docker compose down
```

## Estrutura do Projeto

```
├── docker-compose.yml      # Orquestração dos serviços
├── .env.example            # Variáveis de ambiente
├── setup-hermes.sh         # Script de setup com Docker
├── setup-hermes-cpu.sh     # Script de setup sem Docker (CPU)
├── webui-hermes.py         # Interface web alternativa (Gradio)
└── README.md               # Este arquivo
```

## Recursos

- [Hermes Models (NousResearch)](https://huggingface.co/NousResearch)
- [Ollama](https://ollama.com/)
- [Open WebUI](https://github.com/open-webui/open-webui)
