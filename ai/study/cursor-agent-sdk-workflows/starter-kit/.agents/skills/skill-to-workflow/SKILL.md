---
name: skill-to-workflow
description: Converte um fluxo feito de skills e subagents (.agents/skills, .cursor/skills, .claude/skills, .codex/skills + .cursor/agents, .claude/agents, .codex/agents) em um workflow determinístico em workflows/*.ts ou .agents/workflows/*.ts. Use quando o usuário digitar /skill-to-workflow e indicar as skills ou subagents de referência.
disable-model-invocation: true
---

# Converter skills e subagents em workflow

**Entrada:** caminhos para um ou mais `SKILL.md` (`.agents/skills/`, `.cursor/skills/`, `.claude/skills/`,
`.codex/skills/`), arquivos de subagent (`.cursor/agents/*.md`, `.claude/agents/*.md`, `.codex/agents/*.md`) e, se
existirem, instruções (`AGENTS.md`, `CLAUDE.md`, `.cursor/rules/`), comandos ou hooks que participam do fluxo.

**Saída:** `workflows/<nome>.ts` (dentro do kit) ou `.agents/workflows/<nome>.ts` (num repositório que usa o kit
instalado fora), `test/<nome>.test.ts` e um relatório de conversão no chat.

Antes de começar, carregue a skill `workflow-authoring`: ela tem a API do runtime e as regras.

## Passo 1: inventário (só leitura)

Leia cada arquivo indicado e tudo o que ele referencia: scripts, templates, outros agentes e MCP servers. Monte esta tabela:

| Unidade | Caminho | Tipo | Gatilho atual | Harnesses que descobrem hoje | Entradas | Saídas | Tools | Modelo | Efeitos externos |
|---|---|---|---|---|---|---|---|---|---|

Para "Harnesses que descobrem hoje", use esta regra:

- **`.agents/skills/`**: Cursor e Codex. **Não** o Claude Code, que não lê nada sob `.agents/`.
- **`.claude/skills/`**: Claude Code, mais o Cursor por compatibilidade.
- **`.cursor/agents/`**: só o Cursor.
- **`.claude/agents/`**: Claude Code, mais o Cursor por compatibilidade.

Essa coluna mostra o que hoje só funciona num harness e passa a funcionar nos dois depois da conversão, porque o
workflow é disparado pelo mesmo MCP server.

Os campos vêm destas fontes:

- **Subagent**:
  - `name`, `description`, `model` (`inherit` = o do pai) e o corpo como prompt.
  - No Cursor, `readonly`/`is_background`.
  - No Claude Code, `tools`/`disallowedTools`, `permissionMode` e `skills`.
- **Skill**:
  - os passos numerados, as condições ("se X, faça Y") e os scripts chamados.
  - `disable-model-invocation`, que diz se a skill era explícita ou dependia do modelo para disparar.

## Passo 2: achar as decisões implícitas

Liste toda decisão que hoje **o modelo** toma. Sinais típicos:

- "quando relevante", "se necessário", "use o subagent X para…" (delegação decidida pelo modelo);
- "repita até…" sem número máximo;
- "verifique se os testes passam" (verificação feita por quem gerou o código);
- escolha de modelo implícita, quando tudo herda o modelo do chat.

Para cada decisão, proponha a regra em código que a substitui: um campo, uma label, uma contagem, um exit code ou
um schema. Se não houver regra objetiva possível, ela vira uma etapa `ctx.agent` com `schema` (um classificador
barato), e o **código** age sobre a resposta.

## Passo 3: mapear para o runtime

| Origem | Destino |
|---|---|
| Instruções gerais (`CLAUDE.md`, `.cursor/rules/`) usadas pelo fluxo | Mova o que for comum para `AGENTS.md`, que as etapas carregam via `settingSources: ["project"]`. Deixe no prompt da etapa só o que é específico dela |
| Passo de skill executado pelo modelo | `ctx.agent(prompt, { schema, tools, model })`. O prompt é o texto do passo mais as entradas explícitas |
| Subagent chamado por delegação | `ctx.agent(corpoDoSubagent + tarefa, { model, tools })`. `readonly: true` vira `tools: ["read","grep","glob","ls"]` |
| Vários subagents independentes | `ctx.parallel` (barreira) ou `ctx.pipeline` (por item) |
| Script chamado pela skill (lint, testes, build) | `execFileSync` no workflow; o resultado decide o próximo passo |
| "Repita até passar" | `for (let round = 1; round <= N && !ok; round++)` |
| Revisão/crítica | Etapa separada com modelo próprio e schema `{findings, severity}`; o código decide se bloqueia. Revisor que falha (`null`) encerra o run com status explícito; depois de corrigir, revise de novo |
| Hook `stop`/`subagentStop` com `followup_message` (loop) | Laço explícito no workflow; o hook deixa de ser necessário |
| Efeito externo (commit, PR, comentário) | Código no fim, depois das verificações |
| Subagent que o workflow quer delegar *dentro* de uma etapa | `agents: { nome: { description, prompt, model } }` na opção da etapa |
| Claude Code `isolation: worktree` | `git worktree add` no código e `cwd` da etapa apontando para ele |
| Claude Code `maxTurns` | `timeoutMs` e `retries` da etapa (o SDK não expõe teto de turnos) |
| Claude Code `effort` | `model.params` (ex.: `[{ id: "reasoning_effort", value: "high" }]`), se o modelo oferecer; confira em `npm run models` |
| Claude Code `tools` / `disallowedTools` | `tools` / `disallowedTools` do SDK (nomes diferentes: `Read`→`read`, `Bash`→`shell`, `Edit`/`Write`→`edit`) |

**Modelos:** troque `inherit` por um tier explícito. Use um modelo barato para etapas mecânicas e de leitura e reserve
o modelo de fronteira para planejamento difícil e revisão. Confirme os IDs com `npm run models`.

## Passo 4: gerar

1. Escreva o workflow seguindo `workflow-authoring`, com `meta.whenToUse` copiado e adaptado da
   `description` da skill original.
2. Escreva `test/<nome>.test.ts` com o fake SDK, cobrindo cada ramo criado no passo 2.
3. Rode `npm run typecheck` e `npm test` e corrija até passar.
4. **Não apague** as skills e os subagents originais. Sugira ao usuário marcar a skill antiga com
   `disable-model-invocation: true`, ou trocar o corpo dela por "use /run-workflow <nome>".

## Passo 5: relatório no chat

- Tabela do passo 1 e lista de decisões implícitas, com a regra adotada para cada uma.
- O que **não** foi convertido e por quê: por exemplo, uma interação com o humano no meio do fluxo. O runtime não
  pausa para perguntar; divida em dois workflows ou receba a resposta por `args`.
- Paridade: se o fluxo original era do Claude Code, aponte o que muda no Cursor (formato dos hooks, `loop_limit`,
  subagents lidos de `.claude/agents/`, MCP do time em cloud).
- O comando para o primeiro teste real com teto baixo: `npm run wf -- run <nome> --args '{...}' --max-cents 100`.
