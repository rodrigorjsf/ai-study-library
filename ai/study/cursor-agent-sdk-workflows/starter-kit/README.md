# Cursor Workflows Starter Kit

Esqueleto de repositório para criar **workflows de agentes determinísticos** sobre o
[Cursor SDK](https://cursor.com/docs/sdk/typescript) (`@cursor/sdk`). Os workflows podem ser invocados do **chat do
Cursor IDE** (via MCP), do **terminal** e de **CI** (via CLI).

Um workflow é um arquivo TypeScript em que **o código decide** a ordem das etapas, os ramos, os laços, o modelo de
cada etapa, quando revisar e quando parar. Cada etapa é um agente do Cursor com uma tarefa pequena e uma saída
validada por schema. Assim, modelos menores executam bem a maior parte do trabalho, e o fluxo termina por completo
ou falha de forma explícita, nunca "pula" uma etapa em silêncio.

A ideia é a mesma dos *dynamic workflows* do Claude Code (`agent`, `parallel`, `pipeline`, `phase`), trazida para o
Cursor, que não tem esse runtime nativo. O porquê e a comparação completa estão em
[`../00-relatorio-pesquisa.md`](../00-relatorio-pesquisa.md).

> **Status:** blueprint.
> - O código passa no typecheck contra `@cursor/sdk@1.3.1`.
> - O controle de fluxo está coberto por 8 testes offline com um SDK falso: schema, validação de args, retries,
>   timeout, concorrência, teto de custo e resume.
> - O MCP server foi exercitado pelo protocolo stdio. O CLI (`start`/`wait`, jobs órfãos, guarda de recursão,
>   workflows em `.agents/workflows/`) foi testado num repositório temporário.
> - Um revisor independente auditou código e afirmações contra os `.d.ts` do SDK; as correções foram aplicadas.
> - **Nada foi executado contra a API real do Cursor ainda.** O primeiro passo ao adotar é o
>   [teste de fumaça](docs/01-instalacao.md#5-teste-de-fumaça-real).

## Estrutura

```
.
├── AGENTS.md               # instruções dos agentes (Cursor, etapas dos workflows, Codex)
├── CLAUDE.md               # só `@AGENTS.md`, para o Claude Code ler as mesmas instruções
├── src/
│   ├── runtime/
│   │   ├── workflow.ts     # tipos públicos + defineWorkflow()
│   │   ├── engine.ts       # agent/parallel/pipeline/phase, retries, modelo, teto de custo
│   │   ├── structured.ts   # saída estruturada via custom tool submit_result + Ajv
│   │   ├── journal.ts      # resume sem repetir etapas concluídas
│   │   ├── jobs.ts         # execução assíncrona com estado em disco (start/wait)
│   │   └── registry.ts     # descobre workflows/*.ts
│   ├── cli.ts              # wf login | list | run | start | wait | status | jobs
│   └── mcp-server.ts       # tools MCP: list_workflows, start_workflow, wait_workflow, get_workflow_status
├── workflows/
│   └── implement-issue.ts  # exemplo: tier por label → plano → código → testes → review condicional → PR
├── test/                   # testes offline do engine (fake SDK)
├── .agents/                # local neutro (Cursor e Codex leem nativamente)
│   ├── skills/
│   │   ├── run-workflow/       # /run-workflow <nome> <args>: dispara e acompanha
│   │   ├── workflow-authoring/ # referência para escrever workflows
│   │   └── skill-to-workflow/  # /skill-to-workflow: converte skills e subagents em workflow
│   └── workflows/          # workflows do repositório (carregados junto com workflows/)
├── .cursor/mcp.json        # MCP server no Cursor
├── .mcp.json               # o mesmo MCP server no Claude Code
├── scripts/link-claude-skills.sh  # expõe .agents/skills ao Claude Code (que não lê .agents/)
└── docs/
```

## Começo rápido

```bash
npm ci
npm test && npm run typecheck
npm run wf -- login          # login do Cursor no navegador; o uso fica na SUA conta
npm run models               # IDs de modelo liberados para você
# primeiro run real: num repositório de teste (com commit e remote GitHub), com teto baixo
npm run wf -- run implement-issue --cwd /caminho/do/repo-de-teste --args '{"issue":1}' --max-cents 100
```

No Cursor IDE, abra o repositório, habilite o MCP server `workflows` (Settings → MCP) e digite no chat:

```
/run-workflow implement-issue 123
```

## Documentação

| Documento | Conteúdo |
|---|---|
| [01 · Instalação](docs/01-instalacao.md) | Requisitos, dependências, instalação, teste de fumaça |
| [02 · Configuração inicial](docs/02-configuracao-inicial.md) | Autenticação (conta do usuário × service account), modelos, teto de custo, variáveis |
| [03 · Arquitetura](docs/03-arquitetura.md) | Como o runtime funciona e o que ele garante (e o que não garante) |
| [04 · Invocação no Cursor IDE](docs/04-invocacao-no-cursor-ide.md) | MCP, CLI, skill, hooks; paridade com o Claude Code |
| [05 · Escrevendo workflows](docs/05-escrevendo-workflows.md) | API, padrões, regras, testes |
| [06 · Convertendo skills e subagents](docs/06-convertendo-skills-e-subagents.md) | O processo da skill `/skill-to-workflow`, com um exemplo |
| [07 · Governança e custos (Enterprise)](docs/07-governanca-e-custos.md) | Orçamento por usuário, políticas de admin, auditoria, riscos |

## Transparência: o que este kit faz por baixo

- Cada etapa cria um **agente local** do Cursor SDK na sua máquina. A inferência roda nos servidores da Cursor e é
  cobrada na conta da chave usada.
- Os agentes **executam tools sem pedir aprovação** (é o padrão das runs locais do SDK). O kit limita isso com
  allowlist de tools por etapa e carrega os hooks e as regras do projeto. Leia
  [07 · Governança](docs/07-governanca-e-custos.md) antes de usar em um repositório sensível.
- O estado fica em `.workflows/` (journal, jobs, logs, worktrees) do repositório onde o workflow roda. O runtime
  o adiciona a `.git/info/exclude`, sem mexer no `.gitignore` do repositório.
- Os agentes das etapas carregam `AGENTS.md`, regras, skills, hooks e MCP do projeto, e hooks do time e
  Enterprise (`settingSources: ["project","team","mdm"]`). Eles não conseguem disparar outro workflow.
- Commit, push e PR são feitos pelo **código do workflow**, com `git` e `gh`, e só quando você pede (`openPr`).
