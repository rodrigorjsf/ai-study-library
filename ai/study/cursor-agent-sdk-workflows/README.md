# Cursor Agent SDK: workflows determinísticos

Estudo de 2026-11-11 sobre usar o Cursor SDK para transformar fluxos executados por skills e subagents (em que o
modelo decide quando cada passo roda) em **workflows estruturados**: o código controla o que roda e quando, garante
a execução completa e permite modelos menores por etapa. O workflow pode ser invocado pelo chat do Cursor IDE com
a conta do próprio usuário, pensando no contexto empresarial.

| Arquivo | Para quê |
|---|---|
| [`00-relatorio-pesquisa.md`](00-relatorio-pesquisa.md) | O relatório: o que é o Workflow do Claude Code, o que o Cursor SDK oferece, a comparação 1:1, invocação no IDE, auth e billing enterprise, paridade, exemplos, incertezas e recomendação |
| [`starter-kit/`](starter-kit/README.md) | **Semente de um novo repositório:** runtime TS (`agent`/`parallel`/`pipeline`/`phase`/journal/budget), MCP server, CLI, workflow de exemplo (`implement-issue`), skills do Cursor (`/run-workflow`, `workflow-authoring`, `/skill-to-workflow`) a documentação de instalação à governança, e observabilidade (SQLite por usuário, `wf stats`, dashboard localhost) |

## Repositório publicado

O kit virou o repositório público **[rodrigorjsf/cursor-workflows-starter](https://github.com/rodrigorjsf/cursor-workflows-starter)**
([release v0.1.0, pré-release](https://github.com/rodrigorjsf/cursor-workflows-starter/releases/tag/v0.1.0)), que é a versão mantida. A pasta `starter-kit/` e o
`00-relatorio-pesquisa.md` daqui ficam como retrato do estudo em `a69f2a2` e têm defeitos conhecidos.

**0.2.0 em `main` (2026-11-11):** o [PR #1](https://github.com/rodrigorjsf/cursor-workflows-starter/pull/1) foi mergeado
(`6fee634`); a pré-release v0.2.0 ainda não foi publicada.

- O `implement-issue` segue as skills `tdd`, `codebase-design`, `code-review` e `pr` de mattpocock/skills, com três
  peças novas: TDD conferido pelo código entre as etapas, review em três eixos e checkpoint de seams em dois runs.
  LOW e MED foram verificados contra a API real (§13 das verificações).
- As skills do kit foram reescritas pela `writing-for-agents`. A de autoria virou `cursor-workflow-authoring`, porque
  o Claude Code tem uma skill embutida `workflow-authoring`, e uma skill de projeto com o mesmo nome a substitui.
- A `run-workflow` passou a ser invocável pelo modelo nos dois harnesses. A trava de um workflow pago é a aprovação
  de `start_workflow`: no Cursor, pelo Run Mode, com a tool fora da allowlist; no Claude Code, pelo prompt de
  permissão de `mcp__workflows__start_workflow`.

Ele foi montado com [`PROMPT-publicar-repositorio.md`](PROMPT-publicar-repositorio.md), numa sessão local (WSL2), em
2026-11-11. A evidência de cada item está em
[`docs/research/verificacoes-locais.md`](https://github.com/rodrigorjsf/cursor-workflows-starter/blob/main/docs/research/verificacoes-locais.md).

**O que a verificação local mudou nos fatos:**

- **Documentação ao vivo:** das 74 afirmações conferidas, 27 foram confirmadas, 38 parcialmente, 3 refutadas e 6
  ficaram inconclusivas. As refutadas:
  - a tabela de preços do modo Auto (o Auto não tem preço fixo; é o Cursor Router);
  - "o Cursor não lê `CLAUDE.md`";
  - "a doc não diz se `inputTokens` inclui o cache".
- **Plano:** no Free o SDK não roda (`plan_required` já no `Agent.create`, inclusive local); no Premium da The X
  Subscription, roda. `auto-low` não existe, e modelos de terceiros exigem crédito pré-pago no Premium.
- **Medido na API:**
  - `RunResult.model` devolve o ID **resolvido**;
  - `inputTokens` já inclui o cache;
  - `settingSources` é opt-in para `AGENTS.md`, hooks (do Cursor e do Claude Code) e `.cursor/mcp.json`;
  - o `getUsage()` de agentes locais deu `feature_unavailable` mesmo no Premium.
- **Bugs do kit corrigidos:**
  - a guarda contra recursão não funcionava;
  - o teto em centavos ficava cego em uso incluído no plano, e os dois tetos quando o `getUsage()` falhava;
  - `npm run models` estava quebrado;
  - o SQL quebrava no Node 22.13 a 22.19;
  - os testes rodavam num shell de login.
- **Incidente:** no teste ponta a ponta, uma etapa sem sandbox editou um arquivo fora do repositório. O arquivo foi
  revertido. O kit ganhou regra de escopo e trava de segredos, e o reteste sobre a árvore publicada não escreveu
  fora do repositório.
- **Pendente:** Cursor IDE (MCP, skills, `/run-workflow`), sandbox, caminhos MED e HIGH, hooks do time e MDM, e
  políticas de admin.
- **Custo da verificação:** cerca de US$ 0,40 por preço de lista (Composer e Grok saem da franquia do plano).

## Fontes locais relacionadas

- [`ai/docs/claude-code/workflows/workflows.md`](../../docs/claude-code/workflows/workflows.md): doc oficial dos
  dynamic workflows do Claude Code.
- [`docs/cursor/sdk/cursor-agent-sdk-reference.md`](../../../docs/cursor/sdk/cursor-agent-sdk-reference.md):
  referência do SDK, da Cloud API e da CLI (espelho de 2026-05-28).
- [`docs/cursor/hooks/`](../../../docs/cursor/hooks/hooks-guide.md),
  [`docs/cursor/subagents/`](../../../docs/cursor/subagents/subagents-guide.md),
  [`docs/cursor/skills/`](../../../docs/cursor/skills/agent-skills-guide.md),
  [`docs/cursor/mcp/`](../../../docs/cursor/mcp/mcp-guide.md).
