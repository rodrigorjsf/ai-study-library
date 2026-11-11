# Cursor Agent SDK: workflows determinísticos

Estudo de 2026-11-11 sobre usar o Cursor SDK para transformar fluxos executados por skills e subagents (em que o
modelo decide quando cada passo roda) em **workflows estruturados**: o código controla o que roda e quando, garante
a execução completa e permite modelos menores por etapa. O workflow pode ser invocado pelo chat do Cursor IDE com
a conta do próprio usuário, pensando no contexto empresarial.

| Arquivo | Para quê |
|---|---|
| [`00-relatorio-pesquisa.md`](00-relatorio-pesquisa.md) | O relatório: o que é o Workflow do Claude Code, o que o Cursor SDK oferece, a comparação 1:1, invocação no IDE, auth e billing enterprise, paridade, exemplos, incertezas e recomendação |
| [`starter-kit/`](starter-kit/README.md) | **Semente de um novo repositório:** runtime TS (`agent`/`parallel`/`pipeline`/`phase`/journal/budget), MCP server, CLI, workflow de exemplo (`implement-issue`), skills do Cursor (`/run-workflow`, `workflow-authoring`, `/skill-to-workflow`) a documentação de instalação à governança, e observabilidade (SQLite por usuário, `wf stats`, dashboard localhost) |

## Para criar o novo repositório

```bash
cp -r ai/study/cursor-agent-sdk-workflows/starter-kit ~/code/cursor-workflows
cd ~/code/cursor-workflows && git init && npm install && npm test && npm run typecheck
```

Em seguida, siga [`starter-kit/docs/01-instalacao.md`](starter-kit/docs/01-instalacao.md), começando pelo teste
de fumaça real (o kit ainda não foi executado contra a API do Cursor).

## Fontes locais relacionadas

- [`ai/docs/claude-code/workflows/workflows.md`](../../docs/claude-code/workflows/workflows.md): doc oficial dos
  dynamic workflows do Claude Code.
- [`docs/cursor/sdk/cursor-agent-sdk-reference.md`](../../../docs/cursor/sdk/cursor-agent-sdk-reference.md):
  referência do SDK, da Cloud API e da CLI (espelho de 2026-05-28).
- [`docs/cursor/hooks/`](../../../docs/cursor/hooks/hooks-guide.md),
  [`docs/cursor/subagents/`](../../../docs/cursor/subagents/subagents-guide.md),
  [`docs/cursor/skills/`](../../../docs/cursor/skills/agent-skills-guide.md),
  [`docs/cursor/mcp/`](../../../docs/cursor/mcp/mcp-guide.md).
