#!/bin/bash
# =============================================================================
# Daily Summary Generator
# Busca commits do dia anterior (ou sexta, se segunda) via glab,
# gera resumo via cursor-cli + Gemini Flash e salva no Apple Notes + markdown.
# =============================================================================
set -euo pipefail

# --- Config ---
GITLAB_USERNAME="${GITLAB_USERNAME:-}"
BASE_DIR="$HOME/daily-summaries"
LOG_DIR="$BASE_DIR/logs"
CURSOR_PROMPT_FILE="/tmp/daily-summary-prompt.md"

# Configuração do Apple Notes
NOTES_ACCOUNT="iCloud"           # Altere se usar outra conta (ex: "On My Mac", "Gmail")
NOTES_FOLDER="Daily Summaries"   # Pasta dentro do Notes

# --- Garantir PATH (launchd não herda shell config) ---
export PATH="/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin:$HOME/.local/bin:$PATH"

# =============================================================================
# FUNÇÃO: Detectar username do GitLab
# =============================================================================
detect_gitlab_user() {
  if [ -n "$GITLAB_USERNAME" ]; then
    return
  fi
  # Tentar extrair do glab auth status
  GITLAB_USERNAME=$(glab auth status 2>&1 | grep -oE 'as [^ ]+' | head -1 | sed 's/as //' || echo "")
  if [ -z "$GITLAB_USERNAME" ]; then
    echo "[ERRO] Não foi possível detectar o username do GitLab."
    echo "       Configure a variável GITLAB_USERNAME no script ou faça login: glab auth login"
    exit 1
  fi
}

# =============================================================================
# FUNÇÃO: Converter markdown para HTML (pandoc ou fallback python3)
# =============================================================================
md_to_html() {
  local MD_CONTENT="$1"

  if command -v pandoc &>/dev/null; then
    echo "$MD_CONTENT" | pandoc -f markdown -t html 2>/dev/null
    return
  fi

  # Fallback: conversão básica via python3
  python3 <<'PYEOF' <<< "$MD_CONTENT"
import sys, re

md = sys.stdin.read()
lines = md.split('\n')
html_lines = []
in_list = False

for line in lines:
    stripped = line.strip()

    if in_list and not stripped.startswith('- '):
        html_lines.append('</ul>')
        in_list = False

    if re.match(r'^#{1,6} ', stripped):
        level = len(stripped.split(' ')[0])
        text = stripped.lstrip('#').strip()
        html_lines.append(f'<h{level}>{text}</h{level}>')
    elif stripped == '---':
        html_lines.append('<hr>')
    elif stripped.startswith('> '):
        text = stripped[2:]
        html_lines.append(f'<blockquote>{text}</blockquote>')
    elif stripped.startswith('- '):
        if not in_list:
            html_lines.append('<ul>')
            in_list = True
        text = stripped[2:]
        text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
        text = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', text)
        html_lines.append(f'<li>{text}</li>')
    elif stripped == '':
        html_lines.append('<br>')
    else:
        text = re.sub(r'`([^`]+)`', r'<code>\1</code>', stripped)
        text = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', text)
        text = re.sub(r'\*([^*]+)\*', r'<i>\1</i>', text)
        html_lines.append(f'<p>{text}</p>')

if in_list:
    html_lines.append('</ul>')

print('\n'.join(html_lines))
PYEOF
}

# =============================================================================
# FUNÇÃO: Salvar no Apple Notes via AppleScript
# =============================================================================
save_to_apple_notes() {
  local DATE="$1"
  local MD_CONTENT="$2"
  local NOTE_TITLE="Daily Summary - $DATE"

  echo "  Convertendo markdown → HTML..."
  local HTML_BODY
  HTML_BODY=$(md_to_html "$MD_CONTENT")

  # Escapar para AppleScript (backslashes e aspas)
  HTML_BODY=$(printf '%s' "$HTML_BODY" | sed 's/\\/\\\\/g; s/"/\\"/g')

  echo "  Criando nota no Apple Notes..."
  osascript <<EOF
tell application "Notes"
    tell account "$NOTES_ACCOUNT"
        -- Criar pasta se não existir
        if not (exists folder "$NOTES_FOLDER") then
            make new folder with properties {name:"$NOTES_FOLDER"}
            delay 0.5
        end if

        -- Verificar se já existe nota com mesmo título (idempotência)
        set noteExists to false
        try
            set existingNotes to every note of folder "$NOTES_FOLDER" whose name is "$NOTE_TITLE"
            if (count of existingNotes) > 0 then
                set noteExists to true
            end if
        end try

        if noteExists then
            -- Atualizar nota existente
            set body of (first note of folder "$NOTES_FOLDER" whose name is "$NOTE_TITLE") to "$HTML_BODY"
            log "Nota atualizada: $NOTE_TITLE"
        else
            -- Criar nova nota
            make new note at folder "$NOTES_FOLDER" with properties {name:"$NOTE_TITLE", body:"$HTML_BODY"}
            log "Nota criada: $NOTE_TITLE"
        end if
    end tell
end tell
EOF

  local EXIT_CODE=$?
  if [ $EXIT_CODE -eq 0 ]; then
    echo "  [OK] Apple Notes: $NOTES_ACCOUNT → $NOTES_FOLDER → $NOTE_TITLE"
  else
    echo "  [WARN] Falha ao salvar no Apple Notes (exit: $EXIT_CODE)."
    echo "         Verifique permissões em: Ajustes → Privacidade → Automação → Terminal → Notes"
    echo "         O resumo markdown ainda está disponível em: $OUTPUT_FILE"
  fi
}

# =============================================================================
# INÍCIO DA EXECUÇÃO
# =============================================================================

# --- Verificar dependências ---
for cmd in glab python3 osascript; do
  if ! command -v "$cmd" &>/dev/null; then
    echo "[ERRO] Comando '$cmd' não encontrado no PATH."
    exit 1
  fi
done

# --- Detectar username ---
detect_gitlab_user
echo "[OK] GitLab user: $GITLAB_USERNAME"

# --- Verificar se cursor-cli existe ---
HAS_CURSOR_CLI=false
if command -v cursor &>/dev/null; then
  HAS_CURSOR_CLI=true
  echo "[OK] cursor-cli encontrado."
else
  echo "[INFO] cursor-cli não encontrado. Será usado fallback sem IA."
fi

# --- Só executa de segunda a sexta ---
DAY_OF_WEEK=$(date +%u)  # 1=seg, 7=dom
if [ "$DAY_OF_WEEK" -gt 5 ]; then
  echo "[INFO] Fim de semana (dia $DAY_OF_WEEK). Pulando execução."
  exit 0
fi

# --- Calcular data-alvo ---
if [ "$DAY_OF_WEEK" -eq 1 ]; then
  TARGET_DATE=$(date -v-3d +%Y-%m-%d)
else
  TARGET_DATE=$(date -v-1d +%Y-%m-%d)
fi

# Override via argumento: ./generate-daily.sh 2025-02-10
if [ "${1:-}" != "" ]; then
  TARGET_DATE="$1"
fi

TODAY_DIR="$BASE_DIR/$TARGET_DATE"
OUTPUT_FILE="$TODAY_DIR/summary.md"
COMMITS_RAW="$TODAY_DIR/commits-raw.json"
COMMITS_DETAIL="$TODAY_DIR/commits-detail.txt"

# --- Idempotência ---
if [ -f "$OUTPUT_FILE" ] && [ -s "$OUTPUT_FILE" ]; then
  echo "[INFO] Resumo para $TARGET_DATE já existe. Pulando."
  echo "       Para regenerar, delete: rm -rf $TODAY_DIR"
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
BEFORE_DATE=$(date -j -f "%Y-%m-%d" "$TARGET_DATE" +%Y-%m-%d -v+1d 2>/dev/null \
  || date -d "$TARGET_DATE + 1 day" +%Y-%m-%d)

echo "[1/5] Buscando push events em $TARGET_DATE..."

glab api "events?action=pushed&after=${AFTER_DATE}&before=${BEFORE_DATE}&per_page=100" \
  --method GET 2>/dev/null > "$COMMITS_RAW" || true

# Extrair project IDs únicos
PROJECT_IDS=$(python3 -c "
import json
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
  NO_COMMITS_MSG="# Daily Summary - $TARGET_DATE

> Nenhum commit encontrado para este dia."
  echo "$NO_COMMITS_MSG" > "$OUTPUT_FILE"
  save_to_apple_notes "$TARGET_DATE" "$NO_COMMITS_MSG"
  exit 0
fi

echo "[INFO] Projetos com atividade: $(echo $PROJECT_IDS | tr '\n' ', ')"

# =============================================
# PASSO 2: Buscar commits detalhados por projeto
# =============================================
echo "[2/5] Buscando commits detalhados por projeto..."

> "$COMMITS_DETAIL"

for PID in $PROJECT_IDS; do
  PROJECT_NAME=$(glab api "projects/$PID" --method GET 2>/dev/null | \
    python3 -c "import json,sys; print(json.load(sys.stdin).get('path_with_namespace','projeto-$PID'))" \
    2>/dev/null || echo "projeto-$PID")

  echo "  → $PROJECT_NAME (ID: $PID)"
  echo "## $PROJECT_NAME" >> "$COMMITS_DETAIL"
  echo "" >> "$COMMITS_DETAIL"

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
        msg = c.get('message','').strip().split('\n')[0]
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
echo "[3/5] Gerando resumo com IA..."

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

$(cat "$COMMITS_DETAIL")

Gere APENAS o markdown do resumo, sem explicações extras ou blocos de código."

if [ "$HAS_CURSOR_CLI" = true ]; then
  echo "  Tentando cursor-cli..."
  cursor --model gemini-2.5-flash --message "$PROMPT_CONTENT" > "$OUTPUT_FILE" 2>/dev/null || true
fi

if [ ! -s "$OUTPUT_FILE" ] && [ "$HAS_CURSOR_CLI" = true ]; then
  echo "  Tentando cursor-cli via stdin pipe..."
  echo "$PROMPT_CONTENT" > "$CURSOR_PROMPT_FILE"
  cat "$CURSOR_PROMPT_FILE" | cursor --model gemini-2.5-flash 2>/dev/null > "$OUTPUT_FILE" || true
fi

if [ ! -s "$OUTPUT_FILE" ] && [ "$HAS_CURSOR_CLI" = true ]; then
  echo "  Tentando cursor-cli com --file..."
  cursor --model gemini-2.5-flash --file "$CURSOR_PROMPT_FILE" > "$OUTPUT_FILE" 2>/dev/null || true
fi

# Fallback sem IA
if [ ! -s "$OUTPUT_FILE" ]; then
  echo "  [WARN] cursor-cli indisponível. Gerando resumo estruturado."
  cat > "$OUTPUT_FILE" <<EOF
# Daily Summary - $TARGET_DATE

> *Resumo gerado automaticamente (sem IA — cursor-cli indisponível)*

$(cat "$COMMITS_DETAIL")

---
*Gerado em $(date '+%Y-%m-%d %H:%M:%S')*
EOF
fi

# =============================================
# PASSO 4: Salvar no Apple Notes
# =============================================
echo "[4/5] Salvando no Apple Notes..."

SUMMARY_CONTENT=$(cat "$OUTPUT_FILE")
save_to_apple_notes "$TARGET_DATE" "$SUMMARY_CONTENT"

# =============================================
# PASSO 5: Finalização
# =============================================
echo ""
echo "[5/5] Concluído!"
echo "  📄 Markdown: $OUTPUT_FILE"
echo "  📝 Apple Notes: $NOTES_ACCOUNT → $NOTES_FOLDER → Daily Summary - $TARGET_DATE"
