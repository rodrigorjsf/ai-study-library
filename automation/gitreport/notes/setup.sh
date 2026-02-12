#!/bin/bash
# =============================================================================
# Setup - Instala a automação de Daily Summary com Apple Notes
# Uso: bash setup.sh
# =============================================================================
set -euo pipefail

USER_HOME="$HOME"
BASE_DIR="$USER_HOME/daily-summaries"
PLIST_NAME="com.user.daily-summary.plist"
PLIST_SRC="$BASE_DIR/$PLIST_NAME"
PLIST_DST="$USER_HOME/Library/LaunchAgents/$PLIST_NAME"

echo "╔══════════════════════════════════════════════╗"
echo "║     Daily Summary - Setup com Apple Notes    ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# 1. Verificar glab
echo "[1/7] Verificando glab..."
if ! command -v glab &>/dev/null; then
  echo "  [ERRO] glab não encontrado. Instale com: brew install glab"
  exit 1
fi
echo "  [OK] glab: $(which glab)"

# 2. Verificar autenticação glab
echo "[2/7] Verificando autenticação do glab..."
if ! glab auth status &>/dev/null 2>&1; then
  echo "  [WARN] glab não autenticado. Execute: glab auth login"
  echo "  Continuando setup... mas o script vai falhar sem autenticação."
else
  GL_USER=$(glab auth status 2>&1 | grep -oE 'as [^ ]+' | head -1 | sed 's/as //' || echo "")
  echo "  [OK] Logado como: $GL_USER"
fi

# 3. Verificar osascript
echo "[3/7] Verificando osascript..."
if ! command -v osascript &>/dev/null; then
  echo "  [ERRO] osascript não encontrado. Este setup requer macOS."
  exit 1
fi
echo "  [OK] osascript disponível"

# 4. Verificar pandoc (opcional)
echo "[4/7] Verificando pandoc (opcional)..."
if command -v pandoc &>/dev/null; then
  echo "  [OK] pandoc encontrado (melhor conversão markdown → HTML)"
else
  echo "  [INFO] pandoc não encontrado. Será usado conversor embutido."
  echo "         Para melhor resultado: brew install pandoc"
fi

# 5. Criar estrutura
echo "[5/7] Criando diretórios..."
mkdir -p "$BASE_DIR/logs"
echo "  [OK] $BASE_DIR"

# 6. Configurar plist
echo "[6/7] Configurando LaunchAgent..."
sed -i '' "s|PLACEHOLDER_HOME|$USER_HOME|g" "$PLIST_SRC" 2>/dev/null || \
  sed "s|PLACEHOLDER_HOME|$USER_HOME|g" "$PLIST_SRC" > "$PLIST_SRC.tmp" && mv "$PLIST_SRC.tmp" "$PLIST_SRC"

chmod +x "$BASE_DIR/generate-daily.sh"
chmod +x "$BASE_DIR/daily-ctl.sh"

# Instalar LaunchAgent
if launchctl print "gui/$(id -u)/com.user.daily-summary" &>/dev/null; then
  launchctl bootout "gui/$(id -u)/com.user.daily-summary" 2>/dev/null || true
fi
cp "$PLIST_SRC" "$PLIST_DST"
launchctl bootstrap "gui/$(id -u)" "$PLIST_DST"
echo "  [OK] LaunchAgent instalado e ativado"

# 7. Testar Apple Notes
echo "[7/7] Testando integração com Apple Notes..."
echo "  (Pode aparecer um popup pedindo permissão de automação — aceite!)"
echo ""

osascript <<'EOF' 2>/dev/null
tell application "Notes"
    tell account "iCloud"
        if not (exists folder "Daily Summaries") then
            make new folder with properties {name:"Daily Summaries"}
        end if
    end tell
end tell
EOF

if [ $? -eq 0 ]; then
  echo "  [OK] Apple Notes: pasta 'Daily Summaries' criada/verificada"
else
  echo "  [WARN] Não foi possível acessar o Apple Notes."
  echo ""
  echo "  ╔══════════════════════════════════════════════════════════╗"
  echo "  ║  AÇÃO NECESSÁRIA: Permitir automação                    ║"
  echo "  ║                                                          ║"
  echo "  ║  1. Abra: Ajustes do Sistema → Privacidade e Segurança  ║"
  echo "  ║  2. Vá em: Automação                                    ║"
  echo "  ║  3. Encontre: Terminal (ou o app que executou o setup)   ║"
  echo "  ║  4. Ative o toggle para: Notes                          ║"
  echo "  ║                                                          ║"
  echo "  ║  Depois rode: daily-ctl test-notes                      ║"
  echo "  ╚══════════════════════════════════════════════════════════╝"
fi

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║              Setup concluído!                ║"
echo "╚══════════════════════════════════════════════╝"
echo ""
echo "Resumos serão gerados em:"
echo "  📝 Apple Notes → iCloud → Daily Summaries"
echo "  📄 $BASE_DIR/<yyyy-MM-dd>/summary.md"
echo ""
echo "Adicione ao seu ~/.config/fish/config.fish:"
echo ""
echo "  alias daily-ctl='bash $BASE_DIR/daily-ctl.sh'"
echo ""
echo "Comandos úteis:"
echo "  daily-ctl test-notes          # Testar Apple Notes"
echo "  daily-ctl run                 # Executar agora"
echo "  daily-ctl run-date 2025-02-10 # Executar para data específica"
echo "  daily-ctl stop                # Pausar automação"
echo "  daily-ctl start               # Retomar automação"
echo "  daily-ctl status              # Ver estado"
echo "  daily-ctl logs                # Ver logs"
