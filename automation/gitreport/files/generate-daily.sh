#!/bin/bash
# =============================================================================
# Daily Summary Generator
# Busca commits do dia anterior (ou sexta, se segunda) via glab,
# gera resumo via cursor-cli + Gemini Flash e salva em markdown.
# =============================================================================
set -euo pipefail

# --- Config ---
GITLAB_USERNAME="${GITLAB_USERNAME:-$(glab auth status 2>&1 | grep -oP 'Logged in to .+ as \K\S+' || echo '')}"
BASE_DIR="$HOME/daily-summaries"
LOCK_FILE="$BASE_DIR/.lock"
LOG_DIR="$BASE_DIR/logs"
CURSOR_PROMPT_FILE="/tmp/daily-summary-prompt.md"

# --- Garantir PATH (launchd não herda shell config) ---
export PATH="/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin:$HOME/.local/bin:$PATH"

# --- Verificar dependências ---
for cmd in glab python3; do
  if ! command -v "$cmd" &>/dev/null; then
    echo "[ERRO] Comando '$cmd' não encontrado no PATH."
    exit 1
  fi
done

# --- Verificar se cursor-cli existe ---
HAS_CURSOR_CLI=false
if command -v cursor &>/dev/null; then
  HAS_CURSOR_CLI=true
fi

# --- Só executa de segunda a sexta ---
DAY_OF_WEEK=$(date +%u)  # 1=seg, 7=dom
if [ "$DAY_OF_WEEK" -gt 5 ]; then
  echo "[INFO] Fim de semana (dia $DAY_OF_WEEK). Pulando execução."
  exit 0
fi

# --- Calcular data-alvo ---
if [ "$DAY_OF_WEEK" -eq 1 ]; then
  # Segunda-feira → resumo de sexta
  TARGET_DATE=$(date -v-3d +%Y-%m-%d)
else
  # Terça a sexta → resumo do dia anterior
  TARGET_DATE=$(date -v-1d +%Y-%m-%d)
fi

# Permite override via argumento: ./generate-daily.sh 2025-02-10
if [ "${1:-}" != "" ]; then
  TARGET_DATE="$1"
fi

TODAY_DIR="$BASE_DIR/$TARGET_DATE"
OUTPUT_FILE="$TODAY_DIR/summary.md"
COMMITS_RAW="$TODAY_DIR/commits-raw.json"
COMMITS_DETAIL="$TODAY_DIR/commits-detail.txt"

# --- Idempotência: não roda 2x no mesmo dia ---
if [ -f "$OUTPUT_FILE" ] && [ -s "$OUTPUT_FILE" ]; then
  echo "[INFO] Resumo para $TARGET_DATE já existe em $OUTPUT_FILE. Pulando."
  exit 0
fi

mkdir -p "$TODAY_DIR" "$LOG_DIR"

echo "============================================="
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Gerando resumo para: $TARGET_DATE"
echo "============================================="

# =============================================
# PASSO 1: Buscar push events do dia via API
# =============================================
AFTER_DATE="${TARGET_DATE}"
BEFORE_DATE=$(date -j -f "%Y-%m-%d" "$TARGET_DATE" +%Y-%m-%d -v+1d 2>/dev/null || date -d "$TARGET_DATE + 1 day" +%Y-%m-%d)

echo "[1/4] Buscando push events de $GITLAB_USERNAME em $TARGET_DATE..."

glab api "events?action=pushed&after=${AFTER_DATE}&before=${BEFORE_DATE}&per_page=100" \
  --method GET 2>/dev/null > "$COMMITS_RAW" || true

# Extrair project IDs únicos
PROJECT_IDS=$(python3 -c "
import json, sys
try:
    events = json.load(open('$COMMITS_RAW'))
    pids = set()
    for e in events:
        if e.get('action_name','').startswith('pushed'):
            pids.add(str(e.get('project_id','')))
    print('\n'.join(sorted(pids)))
except:
    pass
" 2>/dev/null)

if [ -z "$PROJECT_IDS" ]; then
  echo "[INFO] Nenhum push event encontrado para $TARGET_DATE."
  cat > "$OUTPUT_FILE" <<EOF
# Daily Summary - $TARGET_DATE

> Nenhum commit encontrado para este dia.
EOF
  exit 0
fi

echo "[INFO] Projetos com atividade: $(echo $PROJECT_IDS | tr '\n' ', ')"

# =============================================
# PASSO 2: Para cada projeto, buscar commits detalhados
# =============================================
echo "[2/4] Buscando commits detalhados por projeto..."

> "$COMMITS_DETAIL"  # limpar arquivo

for PID in $PROJECT_IDS; do
  # Buscar nome do projeto
  PROJECT_NAME=$(glab api "projects/$PID" --method GET 2>/dev/null | \
    python3 -c "import json,sys; print(json.load(sys.stdin).get('path_with_namespace','projeto-$PID'))" 2>/dev/null || echo "projeto-$PID")

  echo "  → Projeto: $PROJECT_NAME (ID: $PID)"
  echo "## $PROJECT_NAME" >> "$COMMITS_DETAIL"
  echo "" >> "$COMMITS_DETAIL"

  # Buscar todos os commits do author no dia
  # O endpoint aceita since/until em ISO 8601
  SINCE="${TARGET_DATE}T00:00:00Z"
  UNTIL="${TARGET_DATE}T23:59:59Z"

  COMMITS_JSON=$(glab api "projects/$PID/repository/commits?author=$GITLAB_USERNAME&since=$SINCE&until=$UNTIL&per_page=100" \
    --method GET 2>/dev/null || echo "[]")

  python3 -c "
import json, sys
try:
    commits = json.loads('''$COMMITS_JSON''')
    if not commits:
        print('- Nenhum commit encontrado (pode ser merge/push de outra branch)')
        print()
        sys.exit(0)
    for c in commits:
        sha = c.get('short_id', c.get('id','')[:8])
        msg = c.get('message','').strip().split('\n')[0]  # primeira linha
        branch = c.get('branch','')
        print(f'- \`{sha}\` {msg}')
    print()
except Exception as e:
    print(f'- Erro ao processar commits: {e}')
    print()
" >> "$COMMITS_DETAIL" 2>/dev/null

done

echo ""
echo "--- Commits encontrados ---"
cat "$COMMITS_DETAIL"
echo "----------------------------"

# =============================================
# PASSO 3: Gerar resumo via cursor-cli ou fallback
# =============================================
echo "[3/4] Gerando resumo com IA..."

PROMPT_CONTENT="Você é um assistente que gera resumos de daily standup para desenvolvedores.

Dado os seguintes commits realizados no dia **$TARGET_DATE**, gere um resumo conciso em markdown para apresentação em daily standup.

**Regras:**
- Organize por projeto (use os nomes dos projetos como headings ##)
- Agrupe commits relacionados em um único bullet point descritivo
- Use linguagem técnica mas acessível para a equipe
- Não repita hashes de commit no resumo final
- Formato esperado:

# Daily Summary - $TARGET_DATE

## Projeto X
- Descrição do que foi feito (agrupando commits relacionados)

## Projeto Y
- Descrição do que foi feito

---

**Commits brutos para analisar:**

$( cat "$COMMITS_DETAIL" )

Gere APENAS o markdown do resumo, sem explicações extras ou blocos de código."

if [ "$HAS_CURSOR_CLI" = true ]; then
  # ---- TENTATIVA 1: cursor-cli com flag direto ----
  echo "  Tentando cursor-cli..."
  cursor --model gemini-2.5-flash --message "$PROMPT_CONTENT" > "$OUTPUT_FILE" 2>/dev/null || true
fi

# ---- TENTATIVA 2: cursor-cli modo interativo via pipe/arquivo ----
if [ ! -s "$OUTPUT_FILE" ] && [ "$HAS_CURSOR_CLI" = true ]; then
  echo "  Tentando cursor-cli via stdin pipe..."
  echo "$PROMPT_CONTENT" > "$CURSOR_PROMPT_FILE"

  # Abordagem: pipe o prompt para o cursor em modo agent
  cat "$CURSOR_PROMPT_FILE" | cursor --model gemini-2.5-flash 2>/dev/null > "$OUTPUT_FILE" || true
fi

# ---- TENTATIVA 3: cursor-cli com arquivo de instrução ----
if [ ! -s "$OUTPUT_FILE" ] && [ "$HAS_CURSOR_CLI" = true ]; then
  echo "  Tentando cursor-cli com --file..."
  cursor --model gemini-2.5-flash --file "$CURSOR_PROMPT_FILE" > "$OUTPUT_FILE" 2>/dev/null || true
fi

# ---- FALLBACK: Resumo estruturado sem IA ----
if [ ! -s "$OUTPUT_FILE" ]; then
  echo "  [WARN] cursor-cli não disponível ou falhou. Gerando resumo estruturado sem IA."

  cat > "$OUTPUT_FILE" <<EOF
# Daily Summary - $TARGET_DATE

> *Resumo gerado automaticamente (sem IA — cursor-cli indisponível)*

$(cat "$COMMITS_DETAIL")

---
*Gerado em $(date '+%Y-%m-%d %H:%M:%S')*
EOF
fi

# =============================================
# PASSO 4: Finalização
# =============================================
echo "[4/4] Resumo salvo em: $OUTPUT_FILE"
echo ""
cat "$OUTPUT_FILE"
echo ""
echo "[OK] Concluído com sucesso."
