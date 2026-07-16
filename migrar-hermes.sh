#!/usr/bin/env bash
# ============================================================================
# migrar-hermes.sh — Instala o Hermes Agent limpo e restaura seu backup
# ============================================================================
# COMO USAR no OUTRO Codespaces:
#   1) Coloque este arquivo E o hermes-backup.tar.gz na mesma pasta
#      (ex: a home ~/  ou  /workspaces/<repo>/ )
#   2) Rode:   bash migrar-hermes.sh
#   3) Espere terminar e rode:   hermes
#
# O script:
#   - verifica curl/git
#   - instala o Hermes limpo pelo instalador oficial (baixa Python/Node/deps)
#   - restaura config.yaml, auth.json (chaves), .env, skills, memories
#   - NÃO copia o venv antigo (que é o que costuma quebrar a migração)
# ============================================================================
set -euo pipefail

# Evita vazamento de ambiente que atrapalha o instalador
unset PYTHONPATH 2>/dev/null || true
unset PYTHONHOME 2>/dev/null || true

C_G='\033[0;32m'; C_Y='\033[0;33m'; C_R='\033[0;31m'; C_B='\033[1m'; C_N='\033[0m'
say()  { echo -e "${C_G}==>${C_N} ${C_B}$*${C_N}"; }
warn() { echo -e "${C_Y}!! ${C_N} $*"; }
die()  { echo -e "${C_R}ERRO:${C_N} $*"; exit 1; }

# --- localizar o tarball ao lado do script -------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP="${1:-$SCRIPT_DIR/hermes-backup.tar.gz}"
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"

say "Verificando pré-requisitos (curl, git)..."
command -v curl >/dev/null 2>&1 || die "curl não encontrado. Instale com: sudo apt-get update && sudo apt-get install -y curl"
command -v git  >/dev/null 2>&1 || die "git não encontrado. Instale com: sudo apt-get update && sudo apt-get install -y git"

[ -f "$BACKUP" ] || die "Backup não encontrado: $BACKUP
Coloque o hermes-backup.tar.gz na mesma pasta deste script, ou rode:
  bash migrar-hermes.sh /caminho/para/hermes-backup.tar.gz"

say "Backup encontrado: $BACKUP ($(du -h "$BACKUP" | cut -f1))"

# --- 1) Instalar o Hermes limpo ------------------------------------------
if command -v hermes >/dev/null 2>&1 || [ -x "$HERMES_HOME/hermes-agent/venv/bin/hermes" ]; then
    warn "Hermes já parece instalado — pulando a instalação, só vou restaurar o backup."
else
    say "Instalando o Hermes Agent (baixa Python/Node/deps — pode levar alguns minutos)..."
    curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup --non-interactive \
        || curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup \
        || die "Falha ao instalar o Hermes. Rode manualmente:
  curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
depois rode este script de novo (ele vai só restaurar o backup)."
fi

# --- 2) Restaurar o backup por cima --------------------------------------
say "Restaurando config, chaves e personalização em $HERMES_HOME ..."
mkdir -p "$HERMES_HOME"

# backup de segurança de um config existente, se houver
if [ -f "$HERMES_HOME/config.yaml" ]; then
    cp "$HERMES_HOME/config.yaml" "$HERMES_HOME/config.yaml.pre-migracao.$(date +%Y%m%d_%H%M%S)" 2>/dev/null || true
fi

tar -xzf "$BACKUP" -C "$HERMES_HOME"

# permissões seguras nos arquivos sensíveis
chmod 600 "$HERMES_HOME/auth.json" "$HERMES_HOME/.env" 2>/dev/null || true
chmod 700 "$HERMES_HOME" 2>/dev/null || true

say "Restaurado:"
for f in config.yaml auth.json .env SOUL.md memories/MEMORY.md memories/USER.md; do
    [ -e "$HERMES_HOME/$f" ] && echo "   ✓ $f"
done
[ -d "$HERMES_HOME/skills" ] && echo "   ✓ skills/ ($(find "$HERMES_HOME/skills" -name SKILL.md | wc -l) skills)"

# --- 3) Verificação final -------------------------------------------------
say "Verificando instalação..."
HERMES_BIN="$(command -v hermes || echo "$HERMES_HOME/hermes-agent/venv/bin/hermes")"
if [ -x "$HERMES_BIN" ] || command -v hermes >/dev/null 2>&1; then
    echo
    say "PRONTO! ✅  Feche e reabra o terminal (ou rode:  source ~/.bashrc)"
    echo -e "   Depois é só rodar:  ${C_B}hermes${C_N}"
    echo
    "$HERMES_BIN" --version 2>/dev/null || hermes --version 2>/dev/null || true
else
    die "Hermes instalado mas o comando não ficou no PATH.
Tente:  export PATH=\"\$HOME/.local/bin:\$PATH\"  e rode:  hermes"
fi
