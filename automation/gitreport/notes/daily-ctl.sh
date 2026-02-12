#!/bin/bash
# =============================================================================
# daily-ctl - Controle da automação de Daily Summary
# Uso: daily-ctl [start|stop|status|run|run-date|logs|test-notes]
# =============================================================================

PLIST_DST="$HOME/Library/LaunchAgents/com.user.daily-summary.plist"
SCRIPT="$HOME/daily-summaries/generate-daily.sh"
LOG_DIR="$HOME/daily-summaries/logs"
SERVICE_LABEL="com.user.daily-summary"

case "${1:-help}" in
  start)
    echo "Ativando automação..."
    launchctl bootstrap "gui/$(id -u)" "$PLIST_DST" 2>/dev/null && \
      echo "[OK] Automação ativada. Executa seg-sex às 09:25." || \
      echo "[WARN] Já está ativa ou erro ao ativar."
    ;;

  stop)
    echo "Desativando automação..."
    launchctl bootout "gui/$(id -u)/$SERVICE_LABEL" 2>/dev/null && \
      echo "[OK] Automação desativada. Use 'daily-ctl start' para reativar." || \
      echo "[WARN] Já está desativada ou erro ao desativar."
    ;;

  status)
    echo "=== Status da Automação ==="
    if launchctl print "gui/$(id -u)/$SERVICE_LABEL" &>/dev/null; then
      echo "Estado: ATIVO ✅"
      echo ""
      launchctl print "gui/$(id -u)/$SERVICE_LABEL" 2>/dev/null | grep -E "(state|last exit|run count)" || true
    else
      echo "Estado: INATIVO ⏸️"
    fi
    echo ""
    echo "Últimos resumos gerados:"
    ls -1dt "$HOME/daily-summaries"/2* 2>/dev/null | head -5 | while read dir; do
      date_dir=$(basename "$dir")
      if [ -f "$dir/summary.md" ]; then
        echo "  ✅ $date_dir"
      else
        echo "  ❌ $date_dir (sem summary.md)"
      fi
    done
    if ! ls -d "$HOME/daily-summaries"/2* &>/dev/null; then
      echo "  Nenhum resumo encontrado."
    fi
    ;;

  run)
    echo "Executando agora (dia anterior)..."
    bash "$SCRIPT"
    ;;

  run-date)
    if [ -z "${2:-}" ]; then
      echo "Uso: daily-ctl run-date <yyyy-MM-dd>"
      echo "Exemplo: daily-ctl run-date 2025-02-10"
      exit 1
    fi
    echo "Executando para data: $2"
    bash "$SCRIPT" "$2"
    ;;

  test-notes)
    echo "Testando integração com Apple Notes..."
    osascript <<'EOF'
tell application "Notes"
    tell account "iCloud"
        if not (exists folder "Daily Summaries") then
            make new folder with properties {name:"Daily Summaries"}
        end if
        make new note at folder "Daily Summaries" with properties {name:"Teste - Daily Summary", body:"<h1>Teste</h1><p>Se você está lendo isso, a integração com Apple Notes está funcionando! 🎉</p><p>Pode deletar esta nota.</p>"}
    end tell
end tell
EOF
    if [ $? -eq 0 ]; then
      echo "[OK] Nota de teste criada! Verifique no Apple Notes → Daily Summaries."
      echo "     Delete a nota de teste quando confirmar que funcionou."
    else
      echo "[ERRO] Falha ao criar nota."
      echo ""
      echo "Possíveis causas:"
      echo "  1. Terminal sem permissão de automação para Notes"
      echo "     → Vá em: Ajustes do Sistema → Privacidade → Automação"
      echo "     → Ative Terminal (ou iTerm) → Notes"
      echo ""
      echo "  2. A conta '$NOTES_ACCOUNT' não existe"
      echo "     → Abra Notes.app e verifique o nome exato da conta"
      echo "     → Ajuste NOTES_ACCOUNT em generate-daily.sh"
    fi
    ;;

  logs)
    echo "=== Stdout (últimas 50 linhas) ==="
    tail -50 "$LOG_DIR/stdout.log" 2>/dev/null || echo "Sem logs."
    echo ""
    echo "=== Stderr (últimas 20 linhas) ==="
    tail -20 "$LOG_DIR/stderr.log" 2>/dev/null || echo "Sem erros."
    ;;

  help|*)
    cat <<'HELP'
daily-ctl - Controle da automação de Daily Summary

Uso: daily-ctl <comando>

Comandos:
  start        Ativa a automação (seg-sex 09:25)
  stop         Desativa temporariamente
  status       Mostra estado e últimos resumos
  run          Executa agora para o dia anterior
  run-date     Executa para uma data (yyyy-MM-dd)
  test-notes   Testa integração com Apple Notes
  logs         Mostra logs recentes
  help         Mostra esta ajuda

Exemplos:
  daily-ctl stop              # Pausar a automação
  daily-ctl start             # Retomar
  daily-ctl run-date 2025-02-10  # Gerar para data específica
  daily-ctl test-notes        # Verificar se Apple Notes funciona
HELP
    ;;
esac
