# Daily Summary Generator + Apple Notes

Automação que busca seus commits no GitLab, gera um resumo para a daily standup e salva direto no **Apple Notes** (além de um backup local em markdown).

## Como funciona

```
launchd (09:25, seg-sex)
  → generate-daily.sh
    → glab API /events        (descobre projetos com push no dia)
    → glab API /commits       (busca commits detalhados por projeto)
    → cursor-cli + Gemini     (gera resumo em linguagem natural)
    → markdown → HTML         (pandoc ou conversor embutido)
    → osascript → Apple Notes (salva na pasta "Daily Summaries")
    → salva backup em ~/daily-summaries/yyyy-MM-dd/summary.md
```

**Segunda-feira** → gera resumo de **sexta-feira**.

## Instalação

```bash
# 1. Copie a pasta para seu HOME
cp -r daily-summaries ~/daily-summaries

# 2. Execute o setup
bash ~/daily-summaries/setup.sh

# 3. Aceite o popup de permissão do Apple Notes quando aparecer

# 4. Teste a integração
daily-ctl test-notes

# 5. Adicione o alias ao Fish shell
echo "alias daily-ctl='bash ~/daily-summaries/daily-ctl.sh'" >> ~/.config/fish/config.fish
```

## Onde encontrar os resumos

### Apple Notes
Abra o app **Notes** → conta **iCloud** → pasta **Daily Summaries**.
Cada nota tem o título `Daily Summary - yyyy-MM-dd`.

### Backup local
```bash
cat ~/daily-summaries/2025-02-11/summary.md
```

## Controle da automação

| Comando | Descrição |
|---------|-----------|
| `daily-ctl start` | Ativa a automação |
| `daily-ctl stop` | **Desativa temporariamente** |
| `daily-ctl status` | Mostra estado e últimos resumos |
| `daily-ctl run` | Executa agora (dia anterior) |
| `daily-ctl run-date 2025-02-10` | Executa para data específica |
| `daily-ctl test-notes` | Testa integração com Apple Notes |
| `daily-ctl logs` | Mostra logs recentes |

## Configuração

No início do `generate-daily.sh`:

```bash
NOTES_ACCOUNT="iCloud"           # Nome da conta no Notes
NOTES_FOLDER="Daily Summaries"   # Pasta dentro do Notes
```

Para descobrir o nome exato da sua conta, abra o Notes.app e veja na sidebar.

## Permissões do Apple Notes

Na primeira execução, o macOS pede permissão para o Terminal controlar o Notes.
Se negou sem querer ou precisa resetar:

1. **Ajustes do Sistema** → **Privacidade e Segurança** → **Automação**
2. Encontre **Terminal** (ou iTerm)
3. Ative o toggle para **Notes**

Ou resete via terminal:
```bash
tccutil reset AppleEvents com.apple.Terminal
```

## Estrutura

```
~/daily-summaries/
├── generate-daily.sh              # Script principal
├── daily-ctl.sh                   # CLI de controle
├── setup.sh                       # Instalador
├── com.user.daily-summary.plist   # LaunchAgent
├── logs/
│   ├── stdout.log
│   └── stderr.log
├── 2025-02-10/
│   ├── summary.md                 # Backup markdown
│   ├── commits-raw.json           # Push events brutos
│   └── commits-detail.txt         # Commits por projeto
└── 2025-02-11/
    └── ...

Apple Notes (iCloud):
└── Daily Summaries/
    ├── Daily Summary - 2025-02-10
    ├── Daily Summary - 2025-02-11
    └── ...
```

## Troubleshooting

**"Não foi possível acessar o Apple Notes"**
→ Verifique permissões em Ajustes → Privacidade → Automação
→ Rode `daily-ctl test-notes` para validar

**Nota criada sem formatação / texto bruto**
→ Instale pandoc: `brew install pandoc`
→ O conversor embutido é básico; pandoc gera HTML muito melhor

**"Nenhum commit encontrado"**
→ Verifique seu username: `glab auth status`
→ Teste com data específica: `daily-ctl run-date 2025-02-10`

**Automação não executou no horário**
→ O Mac precisa estar ligado e desbloqueado às 09:25
→ Verifique: `daily-ctl status` e `daily-ctl logs`

**cursor-cli não funciona**
→ O fallback estruturado ainda será gerado (commits organizados por projeto)
→ Verifique a sintaxe: `cursor --help`
