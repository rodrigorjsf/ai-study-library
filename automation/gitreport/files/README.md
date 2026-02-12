# Daily Summary Generator

Automação para gerar resumos de daily standup a partir dos seus commits no GitLab.

## Como funciona

```
launchd (09:25, seg-sex)
  → generate-daily.sh
    → glab API /events (descobre projetos com push no dia)
    → glab API /projects/:id/repository/commits (busca commits detalhados por projeto)
    → cursor-cli + Gemini Flash (gera resumo em linguagem natural)
    → salva em ~/daily-summaries/yyyy-MM-dd/summary.md
```

**Segunda-feira**: gera o resumo de **sexta-feira** da semana anterior.

## Instalação

```bash
# 1. Copie a pasta para seu HOME
cp -r daily-summaries ~/daily-summaries

# 2. Execute o setup
bash ~/daily-summaries/setup.sh
```

## Uso diário

Os resumos são gerados automaticamente. Para acessar:

```bash
# Ver o resumo de hoje (gerado sobre ontem)
cat ~/daily-summaries/$(date -v-1d +%Y-%m-%d)/summary.md

# Abrir no editor
open ~/daily-summaries/$(date -v-1d +%Y-%m-%d)/summary.md
```

## Controle da automação

Use o `daily-ctl` para gerenciar:

```bash
# Adicione ao seu .zshrc ou .bashrc para usar de qualquer lugar:
alias daily-ctl="bash ~/daily-summaries/daily-ctl.sh"
```

| Comando | Descrição |
|---------|-----------|
| `daily-ctl start` | Ativa a automação |
| `daily-ctl stop` | **Desativa temporariamente** |
| `daily-ctl status` | Mostra estado e últimos resumos |
| `daily-ctl run` | Executa agora (dia anterior) |
| `daily-ctl run-date 2025-02-10` | Executa para data específica |
| `daily-ctl logs` | Mostra logs recentes |

## Estrutura de pastas

```
~/daily-summaries/
├── generate-daily.sh          # Script principal
├── daily-ctl.sh               # CLI de controle
├── setup.sh                   # Instalador
├── com.user.daily-summary.plist  # LaunchAgent
├── logs/
│   ├── stdout.log
│   └── stderr.log
├── 2025-02-10/
│   ├── summary.md             # Resumo final
│   ├── commits-raw.json       # Push events brutos
│   └── commits-detail.txt     # Commits detalhados por projeto
└── 2025-02-11/
    └── ...
```

## Sobre o cursor-cli

O script tenta 3 abordagens para o cursor-cli:

1. **Flag direto**: `cursor --model gemini-2.5-flash --message "prompt"`
2. **Stdin pipe**: `echo "prompt" | cursor --model gemini-2.5-flash`
3. **Arquivo**: `cursor --model gemini-2.5-flash --file prompt.md`

Se nenhuma funcionar, gera um resumo estruturado sem IA (os commits ficam organizados por projeto no markdown).

> **Dica**: Verifique a interface do seu cursor-cli com `cursor --help` e ajuste a tentativa correta no script.

## Troubleshooting

**Automação não executou?**
- O Mac precisa estar **ligado e desbloqueado** no horário (09:25)
- Verifique: `daily-ctl status`
- Veja logs: `daily-ctl logs`

**Nenhum commit encontrado?**
- Verifique seu username: `glab auth status`
- O endpoint `/events` pode ter delay. Teste manualmente: `daily-ctl run-date 2025-02-10`
- O `author` na busca de commits usa o username do GitLab; se seus commits usam email diferente, ajuste no script

**cursor-cli não funciona?**
- O fallback estruturado ainda será gerado
- Verifique: `cursor --help` e ajuste os flags no script
