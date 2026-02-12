#!/bin/bash
# =============================================================================
# daily-ctl - Controle da automação de Daily Summary
# Uso: daily-ctl [start|stop|status|run|run-date|logs]
# =============================================================================

PLIST_DST="$HOME/Library/LaunchAgents/com.user.daily-summary.plist"
SCRIPT="$HOME/daily-summaries/generate-daily.sh"
LOG_DIR="$HOME/daily-summaries/logs"
SERVICE="gui/$(id -u)/com.user.daily-summary"

case "${1:-help}" in
  start)
    echo "Ativando automação..."
    launchctl bootstrap "gui/$(id -u)" "$PLIST_DST" 2>/dev/null && \
      echo "[OK] Automação ativada. Próxima execução: seg-sex às 09:25." || \
      echo "[WARN] Já está ativa ou erro ao ativar."
    ;;

  stop)
    echo "Desativando automação..."
    launchctl bootout "gui/$(id -u)" "$PLIST_DST" 2>/dev/null && \
      echo "[OK] Automação desativada." || \
      echo "[WARN] Já está desativada ou erro ao desativar."
    ;;

  status)
    echo "=== Status da Automação ==="
    if launchctl print "$SERVICE" &>/dev/null; then
      echo "Estado: ATIVO"
      launchctl print "$SERVICE" 2>/dev/null | grep -E "(state|last exit|run count)" || true
    else
      echo "Estado: INATIVO"
    fi
    echo ""
    echo "Últimos resumos:"
    ls -1dt "$HOME/daily-summaries"/2* 2>/dev/null | head -5 || echo "  Nenhum resumo encontrado."
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

  logs)
    echo "=== Logs (últimas 50 linhas) ==="
    tail -50 "$LOG_DIR/stdout.log" 2>/dev/null || echo "Sem logs stdout."
    echo ""
    echo "=== Erros ==="
    tail -20 "$LOG_DIR/stderr.log" 2>/dev/null || echo "Sem logs stderr."
    ;;

  help|*)
    echo "daily-ctl - Controle da automação de Daily Summary"
    echo ""
    echo "Uso: daily-ctl <comando>"
    echo ""
    echo "Comandos:"
    echo "  start       Ativa a automação (executa seg-sex 09:25)"
    echo "  stop        Desativa a automação temporariamente"
    echo "  status      Mostra se está ativo e últimos resumos"
    echo "  run         Executa agora para o dia anterior"
    echo "  run-date    Executa para uma data específica (yyyy-MM-dd)"
    echo "  logs        Mostra os últimos logs"
    echo "  help        Mostra esta ajuda"
    ;;
esac
