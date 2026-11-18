# Paridade de contexto nos workflows

Estudo de 2026-11-17 sobre como um passo do `cursor-workflows-starter`, executado pelo Cursor SDK, recebe regras, skills e subagents do Cursor, e sobre como esse projeto gera, gere e executa workflows de exploração que devolvem o resultado ao chat do Cursor IDE ou um estado intermediário para entrevista. A forma de conversão nas notas é a de uma skill com consultas MCP, CLI e ramos no estilo `--review` e `--interview`. Não há skill de exploração de banco no disco.

| Arquivo | Para quê |
|---|---|
| [`00-relatorio-pesquisa.md`](00-relatorio-pesquisa.md) | O relatório |
| [`reports/Paridade de contexto nos workflows.md`](reports/Paridade%20de%20contexto%20nos%20workflows.md) | A mesma redação, no caminho pedido |
| [`research_notes/Paridade de contexto nos workflows/regras.md`](research_notes/Paridade%20de%20contexto%20nos%20workflows/regras.md) | Regras de projeto e de conta, `settingSources`, diferença para o Claude Code |
| [`research_notes/Paridade de contexto nos workflows/skills-subagents.md`](research_notes/Paridade%20de%20contexto%20nos%20workflows/skills-subagents.md) | Skills, subagents e o que o passo headless carrega |
| [`research_notes/Paridade de contexto nos workflows/skill-para-workflow.md`](research_notes/Paridade%20de%20contexto%20nos%20workflows/skill-para-workflow.md) | Conversão de skill, args, MCP, CLI e custo |
| [`research_notes/Paridade de contexto nos workflows/exploracao-e-pausa.md`](research_notes/Paridade%20de%20contexto%20nos%20workflows/exploracao-e-pausa.md) | O que volta ao chat, resume e pausa |
| [`research_notes/Paridade de contexto nos workflows/runtime-starter.md`](research_notes/Paridade%20de%20contexto%20nos%20workflows/runtime-starter.md) | O que o runtime passa a `Agent.create` no commit lido |

## Repositório mantido

O código lido é o checkout [`12cba8f`](https://github.com/rodrigorjsf/cursor-workflows-starter/commit/12cba8f) de [rodrigorjsf/cursor-workflows-starter](https://github.com/rodrigorjsf/cursor-workflows-starter), em `/home/rodrigo/Workspace/cursor-workflows-starter`, com `@cursor/sdk` 1.3.1. As correções de medição que este estudo não reabre estão em [`docs/research/verificacoes-locais.md`](https://github.com/rodrigorjsf/cursor-workflows-starter/blob/12cba8f/docs/research/verificacoes-locais.md) e [`docs/research/relatorio-pesquisa.md`](https://github.com/rodrigorjsf/cursor-workflows-starter/blob/12cba8f/docs/research/relatorio-pesquisa.md).
