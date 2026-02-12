#!/bin/bash
# =============================================================================
# Setup - Instala a automação de Daily Summary
# Uso: bash setup.sh
# =============================================================================
set -euo pipefail

USER_HOME="$HOME"
BASE_DIR="$USER_HOME/daily-summaries"
PLIST_NAME="com.user.daily-summary.plist"
PLIST_SRC="$BASE_DIR/$PLIST_NAME"
PLIST_DST="$USER_HOME/Library/LaunchAgents/$PLIST_NAME"

echo "=== Daily Summary - Setup ==="
echo ""

# 1. Verificar glab
if ! command -v glab &>/dev/null; then
  echo "[ERRO] glab não encontrado. Instale com: brew install glab"
  exit 1
fi

echo "[OK] glab encontrado: $(which glab)"

# 2. Verificar autenticação glab
if ! glab auth status &>/dev/null 2>&1; then
  echo "[WARN] glab não autenticado. Execute: glab auth login"
fi

# 3. Detectar username do GitLab
GL_USER=$(glab auth status 2>&1 | grep -oP 'Logged in to .+ as \K\S+' || echo "")
if [ -z "$GL_USER" ]; then
  read -p "Não foi possível detectar seu username. Digite seu GitLab username: " GL_USER
fi
echo "[OK] GitLab username: $GL_USER"

# 4. Criar estrutura
mkdir -p "$BASE_DIR/logs"
echo "[OK] Diretório criado: $BASE_DIR"

# 5. Configurar username no script
if grep -q 'GITLAB_USERNAME:-' "$BASE_DIR/generate-daily.sh"; then
  echo "[OK] Script principal já configurado."
fi

# 6. Ajustar plist com HOME real
sed -i '' "s|PLACEHOLDER_HOME|$USER_HOME|g" "$PLIST_SRC"
echo "[OK] LaunchAgent configurado com HOME=$USER_HOME"

# 7. Tornar script executável
chmod +x "$BASE_DIR/generate-daily.sh"
echo "[OK] Script marcado como executável"

# 8. Instalar LaunchAgent
if [ -f "$PLIST_DST" ]; then
  launchctl bootout "gui/$(id -u)" "$PLIST_DST" 2>/dev/null || true
fi
cp "$PLIST_SRC" "$PLIST_DST"
launchctl bootstrap "gui/$(id -u)" "$PLIST_DST"
echo "[OK] LaunchAgent instalado e ativado"

echo ""
echo "=== Setup concluído! ==="
echo ""
echo "Resumos serão gerados em: $BASE_DIR/<yyyy-MM-dd>/summary.md"
echo "Logs em:                  $BASE_DIR/logs/"
echo ""
echo "Comandos úteis:"
echo "  Testar agora:       bash $BASE_DIR/generate-daily.sh"
echo "  Testar data:        bash $BASE_DIR/generate-daily.sh 2025-02-10"
echo "  Pausar automação:   launchctl bootout gui/$(id -u) $PLIST_DST"
echo "  Retomar automação:  launchctl bootstrap gui/$(id -u) $PLIST_DST"
echo "  Ver logs:           tail -f $BASE_DIR/logs/stdout.log"
echo "  Ver status:         launchctl print gui/$(id -u)/com.user.daily-summary"
