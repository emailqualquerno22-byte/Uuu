# Kilo Agent Stack — Frontier-Class Autonomous AI Agent

A production-ready AI agent stack that can compete with frontier models like Claude Opus 5.5 / Mythos 5.

## Features

- **Multi-provider support**: Anthropic (Claude), OpenAI, Ollama (local models)
- **Full tool registry**: filesystem, web fetch, shell execution, grep, MCP integration
- **Agent loop**: tool calling, reflection, error recovery, progressive disclosure
- **Memory**: session-level with fact persistence and compression
- **MCP integration**: Model Context Protocol servers for filesystem and web
- **Works without API keys**: falls back to Ollama local models

## Quick Start

```bash
# Activate the virtual environment
source .venv/bin/activate

# Install dependencies (already done)
pip install -r requirements.txt

# Copy environment file and add API keys (optional)
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY or OPENAI_API_KEY

# Run the agent with a task
python agents/harness.py "create a file with the current date and read it back"

# Or use verbose mode
python -v agents/harness.py "list all files in the project"
```

## Project Structure

```
/workspace/app/
├── .env.example          # Environment variables template
├── requirements.txt      # Python dependencies
├── package.json          # Node dependencies
├── README.md             # This file
├── .venv/                # Python virtual environment
├── node_modules/         # Node dependencies
├── mcp_servers/
│   ├── config.json       # MCP server configurations
│   └── filesystem_server.py  # MCP filesystem server
├── agents/
│   ├── harness.py        # Main agent loop and CLI
│   ├── tools.py          # Tool registry (filesystem, web, shell, etc.)
│   ├── memory.py         # Memory management with persistence
│   ├── mcp_client.py     # MCP client integration
│   ├── mcp_servers/
│   │   ├── filesystem_server.py  # MCP filesystem server
│   │   └── fetch_server.py       # MCP web fetch server
│   └── test_write.py     # Test file (remove me)
└── tests/                # Test suite
```

## Architecture

The agent stack is built in layers:

1. **Model Layer**: Claude Opus 5.5 / OpenAI GPT-4o / Ollama Qwen2.5 (local)
2. **Harness Layer**: Agent loop with tool calling, memory, reflection
3. **Tool Layer**: Filesystem, web, shell, grep, MCP servers
4. **Memory Layer**: Session memory with fact persistence
5. **MCP Layer**: Model Context Protocol servers for tool extension

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | No | Anthropic API key for Claude models |
| `OPENAI_API_KEY` | No | OpenAI API key for GPT models |
| `OLLAMA_HOST` | No | Ollama host URL (default: http://localhost:11434) |

### MCP Servers

The project includes two MCP servers:
- **filesystem**: read/write files, list directories, create/remove
- **fetch**: web URL fetching with HTML stripping

Both are configured in `mcp_servers/config.json`.

## Testing

```bash
# Run tests
pytest tests/ -v

# Or run the agent directly
python agents/harness.py "test task"
```

## Requirements

- Python 3.10+
- Node.js 18+ (for Claude Agent SDK)
- Ollama installed (for local model fallback) — already installed in this environment
- 8GB+ RAM recommended
- 15GB+ disk space

## License

MIT