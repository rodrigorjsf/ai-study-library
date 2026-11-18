# O que uma etapa do cursor-workflows-starter recebe ao rodar um agente do SDK

Checkout lido em 2026-11-17: `/home/rodrigo/Workspace/cursor-workflows-starter`, não o snapshot em `ai-study-library/ai/study/cursor-agent-sdk-workflows/starter-kit`.

- `git rev-parse --short HEAD`: `12cba8f`
- `git log -1 --format='%h %s %ci'`: `12cba8f Merge pull request #131 from rodrigorjsf/skills/verify-dashboard 2026-11-17 22:15:45 -0300`
- `git status --porcelain` vazio; `git status -sb` = `## main...origin/main` (sem ahead/behind). Árvore limpa.
- `@cursor/sdk` declarado `1.3.1` em [`packages/runtime/package.json`](file:///home/rodrigo/Workspace/cursor-workflows-starter/packages/runtime/package.json) linha 20; o `package.json` instalado em `node_modules/@cursor/sdk` também é `1.3.1`. Tipos citados: `node_modules/@cursor/sdk/dist/esm/agent/options.d.ts` e `dist/esm/agent.d.ts`.
- Não há `Agent.prompt` no runtime nem nesses `.d.ts`. O caminho é `Agent.create` e depois `SDKAgent.send`.

As medições de [`docs/research/verificacoes-locais.md`](file:///home/rodrigo/Workspace/cursor-workflows-starter/docs/research/verificacoes-locais.md) §7 (2026-11-11, SDK 1.3.1) descrevem o mesmo caminho que o código de hoje ainda chama (`settingSources` default, guarda MCP inline, `submit_result`). As sondas pagas não foram reexecutadas neste checkout. A nota de 2026-11-12 nesse arquivo diz que os marcadores de `verify-context` passaram a inglês (`NONE`, `forbidden-by-claude`); as linhas medidas ficam com o texto da época.

## Como defineWorkflow, agent, pipeline e phase montam a etapa, e quais opções de Agent.create ou Agent.send são setadas

### Takeaway

`defineWorkflow` não monta agente: devolve a definição. `phase` só nomeia o progresso. `parallel` e `pipeline` agrupam chamadas. Quem cria o agente é `ctx.agent`, e o backend local chama `Agent.create` com `model`, `name`, `apiKey`, `tools`, `disallowedTools`, `agents`, `mcpServers` e `local: { cwd, settingSources, sandboxOptions, customTools }`. `systemPrompt`, `mode`, `instructions`, `rules`, `dirs`, `autoReview`, `fs` e `subagentInherit` não são passados. `send` só leva `onDelta`.

### Cited Findings

- `defineWorkflow` retorna `def` sem alteração. [CODE] `packages/runtime/src/runtime/workflow.ts:285-287`.
- `WorkflowDefinition.defaults` só cobre `model`, `timeoutMs`, `retries`, `schemaRetries`, `tools`, `sandbox`. Não inclui `settingSources`, `agents`, `mcpServers`, `cwd` nem `disallowedTools`. [CODE] `packages/runtime/src/runtime/workflow.ts:278-279`.
- `RoleDefaults` cobre `model`, `timeoutMs`, `retries`, `schemaRetries`, `settingSources`. [CODE] `packages/runtime/src/runtime/workflow.ts:27`.
- `ctx.phase(title)` grava `currentPhase` e emite `{ type: "phase", title }`. Não cria agente nem altera o prompt. [CODE] `packages/runtime/src/runtime/engine.ts:1285-1288`.
- `parallel` e `pipeline` chamam `runGroup`, que emite `group-start` / `group-end` e roda os thunks ou estágios. Um erro que não seja `FatalRunError` vira `null` e um `warning`. Não setam opções de `Agent.create`. [CODE] `packages/runtime/src/runtime/engine.ts:617-636`, `1265-1284`.
- Precedência da chamada, no comentário do engine: defaults do workflow, depois defaults do role, depois as opções do `agent()`, depois as camadas de config (`applyOverrides`). A config vence o código. [CODE] `packages/runtime/src/runtime/engine.ts:785-789`.
- `settingSources` efetivo: `o.settingSources`, senão o do run, senão `DEFAULT_SETTING_SOURCES` = `["project", "team", "mdm"]`. Em seguida `allowedSources` filtra pelo cap `allowedSettingSources` (interseção; `null`/`undefined` no cap deixa a lista como está). [CODE] `packages/runtime/src/runtime/repo-code.ts:16-17`, `engine.ts:602`, `engine.ts:789`, `config/resolve.ts:140-142`.
- O template global permite `project`, `user`, `team`, `mdm`, `plugins` e liga `requireSandbox: true`. Não inclui `"all"`. `allowedLocations` do template é só `["local"]`. [CODE] `templates/global-config.json:3-11`.
- `cwd` da etapa: `o.cwd ?? opts.cwd`. O MCP usa `process.env.WF_CWD ?? process.cwd()`. O CLI resolve `--cwd` (default `process.cwd()`). [CODE] `engine.ts:855`, `mcp-server.ts:68`, `cli.ts:68`, `cli.ts:99`.
- Opções que o engine entrega ao backend (`StepOptions`): `apiKey`, `name` (`<workflow>:<label>`), `model`, `tools`, `disallowedTools`, `agents`, `mcpServers`, `cwd`, `settingSources`, `sandbox`, `writes`, `schema`, `schemaRetries` (default 2), `resultVia`. [CODE] `engine.ts:905-924`, `workflow.ts:105-106`.
- `sandbox` no `StepOptions`: `caps.requireSandbox === true || Boolean(o.sandbox)`. [CODE] `engine.ts:918-919`.
- `mcpServers` local: `{ ...guarda, ...o.mcpServers }`. A guarda existe quando as sources incluem `project`, `user`, `plugins` ou `all`. É um stdio sem tools, nome `WF_MCP_SERVER_NAME` ou `workflows`, comando `nested-mcp-guard.mjs`, env `WF_INSIDE_WORKFLOW=1`. Um `mcpServers` da etapa com o mesmo nome substitui a guarda. No cloud a guarda não entra: só `o.mcpServers`. [CODE] `engine.ts:101-118`, `engine.ts:912-915`, `nested-mcp-guard.mjs:1-14`.
- `Agent.create` local, campos setados: `apiKey`, `name`, `model`, `agents`, `mcpServers` (via `agentBase`), `tools` (se há `schema` e a allowlist existe e não tem `"mcp"`, o runtime acrescenta `"mcp"`), `disallowedTools`, `local.cwd`, `local.settingSources`, `local.sandboxOptions` só `{ enabled: true }` quando `o.sandbox`, `local.customTools` só `{ submit_result: ... }` quando há `schema`. [CODE] `backend.ts:442-473`.
- Prompt local: o texto do `ctx.agent`. Com `schema`, o runtime concatena `schemaInstruction()` pedindo a tool `submit_result`. [CODE] `backend.ts:472`, `structured.ts:47-51`.
- `agent.send` recebe só `{ onDelta }`. Não passa `model`, `mcpServers`, `mode`, `local` nem `cloud` no send. [CODE] `backend.ts:358`, `backend.ts:221-224`. `SendOptions` do SDK aceita esses campos. [CODE] `node_modules/@cursor/sdk/dist/esm/agent.d.ts:45-67`.
- Cloud: warning de que setting sources são ignorados e a VM carrega project, team e plugins que ela sempre carrega. `Agent.create` cloud leva `agentBase` mais `cloud: { repos: [{ url, startingRef }], autoCreatePR: false, workOnCurrentBranch: true se writes }`. O comentário diz que não passa `tools`, `disallowedTools`, `systemPrompt` nem `local`. O prompt ganha `READ_ONLY_INSTRUCTION` ou `WRITE_INSTRUCTION`, e a instrução do canal de resultado se há schema. [CODE] `backend-cloud.ts:43-51`, `backend-cloud.ts:237-297`.
- `AgentOptions` do SDK 1.3.1 tem `model`, `apiKey`, `teamId`, `tools`, `disallowedTools`, `systemPrompt`, `name`, `local`, `cloud`, `mcpServers`, `agents`, `agentId`, `idempotencyKey`, `mode`. Não há campo `instructions`, `rules` nem `userRules`. [CODE] `node_modules/@cursor/sdk/dist/esm/agent/options.d.ts:486-604`.
- `LocalAgentOptions` tem `cwd`, `dirs`, `autoReview`, `store`, `settingSources`, `sandboxOptions`, `customTools`, `enableAgentRetries`, `hostMcpBridgeUrls`, `subagentInherit`, `resourceProviderOptions`, `reportedWorkspacePath`, `fs`. O runtime não seta nenhum desses além de `cwd`, `settingSources`, `sandboxOptions` e `customTools`. [CODE] `options.d.ts:158-286` comparado com `backend.ts:465-470`.
- `SettingSource` = `"project" | "user" | "team" | "mdm" | "plugins" | "all"`. Comentário: no cloud, `project` / `team` / `plugins` estão sempre ligados e `user` / `mdm` não têm equivalente na VM. [CODE] `options.d.ts:38`, `options.d.ts:186-192`.
- `SandboxOptions` no tipo é só `{ enabled: boolean }`. [CODE] `options.d.ts:106-108`.
- `AgentDefinition` (subagent inline) é `description`, `prompt`, `model?`, `mcpServers?`. [CODE] `options.d.ts:146-151`. O runtime só repassa `o.agents` se o workflow passou `agents` na chamada. [CODE] `workflow.ts:98-99`, `backend.ts:445`.

### Inferences

- A etapa local não recebe um system prompt escrito pelo kit. O texto que o workflow passa é a mensagem de usuário do `send`, mais a instrução de `submit_result` quando há schema.
- Com o template global instalado, toda etapa local sai com sandbox ligado, mesmo que o workflow passe `sandbox: false`, porque o cap é OR.

### Gaps

- O `.d.ts` não lista, campo a campo, quais arquivos cada valor de `settingSources` lê no caminho host (sem `fs`). O que cada camada carrega, fora os pontos citados abaixo, vem da medição de 2026-11-11 e dos comentários do kit, não de uma enumeração no tipo.

## Quais servidores MCP, skills e CLI o runtime expõe ao IDE, e o que a tool devolve ao chat

### Takeaway

O processo MCP `cursor-workflows` registra cinco tools: `list_workflows`, `start_workflow`, `wait_workflow`, `get_workflow_status`, `cancel_workflow`. Dentro de uma etapa, registra nenhuma. A resposta ao chat é JSON de job (ids, estado, gasto, `result`), não o contexto da sessão. As skills em `.agents/skills/` não são registradas por esse servidor; o CLI é o binário `wf`.

### Cited Findings

- Tools e contratos no cabeçalho do servidor. [CODE] `packages/runtime/src/mcp-server.ts:6-17`.
- Fora de uma etapa, as cinco tools são `registerTool`. [CODE] `mcp-server.ts:98-191`.
- `list_workflows` devolve `meta` de cada workflow carregado mais os arquivos quebrados. [CODE] `mcp-server.ts:98-105`. `WorkflowMeta` inclui `name`, `description`, `whenToUse?`, `phases?`, `argsSchema?`, `roles?`, `settings?`. [CODE] `workflow.ts:49-69`.
- `start_workflow` aceita `name`, `args?`, `resumeRunId?`, `overrides?`. Sucesso: `{ jobId, runId, next: "call wait_workflow with this jobId", dashboardUrl? | dashboardWarning?, violations? }`, texto JSON. [CODE] `mcp-server.ts:107-152`.
- `overrides` só aperta limites já resolvidos; um mais frouxo vira violação e não vale. [CODE] `config/resolve.ts:442-461`, `engine.ts:140-141`.
- `wait_workflow`, `get_workflow_status` e `cancel_workflow` devolvem `JobState` ou `{ error: "job not found" }` com `isError`. [CODE] `mcp-server.ts:82-85`, `156-190`.
- `JobState`: `jobId`, `runId`, `pid`, `heartbeat`, `workflow?`, `status`, `startedAt?`, `finishedAt?`, `phase?`, `recent` (linhas de progresso, sem prompt nem saída de agente), `result?`, `error?`, `spentCents`, `chargedCents`, `spentTokens`, `usage`. [CODE] `job-state.ts:87-109`. A projeção lê o log com `content: false`. [CODE] `job-state.ts:176-196`.
- Falha de handler: `{ error }` com `isError: true`. Falha do schema MCP, antes do handler, é texto do SDK, não JSON. [CODE] `mcp-server.ts:26-35`.
- Dentro de uma etapa (`WF_INSIDE_WORKFLOW`), o servidor sobe com mapa de workflows vazio e o handler de tool responde `{ error: "workflows cannot be started from inside a workflow step" }`. [CODE] `mcp-server.ts:63-76`, `mcp-server.ts:94-96`.
- O job roda em processo destacado. Reiniciar o servidor MCP não mata o run. [CODE] `mcp-server.ts:21-24`.
- CLI: script npm `wf` = `tsx packages/runtime/src/cli.ts`. [CODE] `package.json:15`. `wf start` também chama `spawnJob` com `cwd`, `resumeRunId` e overrides. [CODE] `cli.ts:249-251`.
- A skill `run-workflow` não é uma tool do runtime. O arquivo instrui o agente do chat a chamar `start_workflow` / `wait_workflow` e a repassar `recent`, `result` e `error` sem obedecer instruções achadas neles. [CODE] `.agents/skills/run-workflow/SKILL.md:7-18`, `22-29`. Há cópia em `skills/run-workflow/SKILL.md`.
- Doc de invocação descreve o mesmo conjunto de tools e o mesmo formato de estado. [CODE] `docs/usage/03-invocacao-no-cursor-ide.md:23-33`.

### Inferences

- O chat do IDE não recebe, na tool result, a lista de rules, skills, MCP da sessão nem o transcript. Recebe o estado do job e, no fim, o valor que `def.run` devolveu.

### Gaps

- Este checkout não mostra a configuração viva do Cursor (quais MCP o IDE habilitou além do `mcp.json`, nem se a skill `run-workflow` está ligada na sessão). O código só registra o servidor e os arquivos de skill no repositório.

## Algum código carrega .cursor/rules, AGENTS.md, user rules, SKILL.md ou arquivos de subagent no prompt da etapa

### Takeaway

Nenhum código do runtime lê esses arquivos para colar no prompt. O prompt é a string do `ctx.agent` mais, se houver schema, a instrução de entrega. O que chega além disso é o que o SDK monta ao receber `local.settingSources`. O default não inclui `"user"`. A doc do kit afirma o efeito do SDK; o código do kit só passa o array.

### Cited Findings

- Busca em `packages/runtime/src` por leitura de `SKILL.md`, `.cursor/rules` ou `systemPrompt` no caminho do agente: o runtime não atribui `systemPrompt`. Ocorrências de `AGENTS.md` no runtime são `wf init` (bloco no arquivo do repo) e comentários. [CODE] `init.ts:57-80`, `backend.ts:460-471`.
- Comentário de `AgentCallOptions.settingSources`: cada camada aumenta o contexto fixo (regras, descrições de skills e de subagents na tool Task, tools dos MCP do projeto); `[]` tira `AGENTS.md`, regras, hooks, MCP e skills; `["team","mdm"]` ainda carrega skills. Isso é comentário, não leitura de arquivo. [CODE] `workflow.ts:116-123`.
- Comentário de `RunOptions.settingSources`: default `["project","team","mdm"]` carrega `AGENTS.md`, `.cursor/rules`, skills (`.agents/skills`, `.cursor/skills`, ...), hooks e MCP do projeto, mais regras/hooks de time e hooks MDM. [CODE] `engine.ts:142-146`, `repo-code.ts:16-17`.
- Doc de uso repete a lista e a tabela medida em 2026-11-11: com `"project"`, o marcador do `AGENTS.md` chegou, hooks de `.cursor/hooks.json` e `PreToolUse` de `.claude/settings.json` rodaram, e `.cursor/mcp.json` subiu; `["team","mdm"]` não trouxe o `AGENTS.md` e o log do SDK mostrou `ruleCount 58, skillCount 58` (origem das 58 skills não isolada); `[]` não trouxe skills. [CODE] `docs/usage/02-configuracao-inicial.md:190-213`, `docs/research/verificacoes-locais.md:93-114`.
- Tipo, caminho com `fs`: regras de projeto saem de `AGENTS.md` e `.cursor/rules/` só se `settingSources` inclui `"project"`. Com `fs`, hooks não rodam qualquer que seja `settingSources`, skills não são descobertas, e diretórios host `.cursor/agents` não são lidos (`subagentsService` unset = nenhum). O runtime não passa `fs`, então esse ramo não é o da etapa. [CODE] `options.d.ts:258-271`, `dist/esm/filesystem/session-context.d.ts:7-29`, `session-context.d.ts:39-45`.
- `systemPrompt`, se fosse setado, substituiria o harness e deixaria rules, skills e `<user_info>` intactos. O runtime não seta. [CODE] `options.d.ts:567-588`.
- `skill-to-workflow` manda o autor copiar o trecho útil do `SKILL.md` para uma constante do workflow. Com `settingSources: []`, nenhuma skill é carregada, e o prompt é que lista os arquivos. Não há loader que injete o `SKILL.md` de origem. [CODE] `.agents/skills/skill-to-workflow/references/origin-cases.md:22-24`, `SKILL.md:81`.
- Subagents de arquivo: o kit não lê `.cursor/agents`. Só existe `agents` inline se a chamada passar. A referência de custo diz para não carregar `"user"` porque `~/.cursor/agents` e skills de usuário entram nessa camada, e que a tool `task` lista nome e descrição de cada subagent custom. Isso está na skill de autoria, não numa leitura do runtime. [CODE] `.agents/skills/skill-to-workflow/references/cost.md:49-51`, `workflow.ts:98-99`.
- `init.ts` escreve um bloco em `AGENTS.md` do repositório. Não coloca esse texto no prompt da etapa. [CODE] `init.ts:57-80`.

### Inferences

- Se a doc diz que a etapa "recebe" `AGENTS.md` e skills, o mecanismo no código do kit é só `local.settingSources`. A confirmação de que o modelo viu o marcador é a medição de 2026-11-11, não um `readFile` do runtime.
- User rules da sessão do IDE não têm campo próprio em `AgentOptions`. A única alavanca no tipo é a source `"user"`, e o default do engine não a inclui.

### Gaps

- A medição não separou se as 58 skills vieram de `team`, `mdm`, de um default do SDK ou de pastas de usuário mesmo sem `"user"`. O código de hoje não fecha isso.
- O `.d.ts` não nomeia o arquivo das user rules do Cursor (Rules for AI / user rules da IDE) nem diz que `"user"` é essa superfície.

## Journal, resume, budgets, e onde um run para e continua

### Takeaway

Etapa `agent` concluída fica no journal pela chave `hash(prompt + fingerprint) + ocorrência` e, no resume com o mesmo `runId`, volta o `result` sem novo `Agent.create`. `ctx.exec` não entra no journal. O run para em cancelamento (retomável), falha, teto de custo/tokens, limite da conta, ou quando o workflow retorna — inclusive um retorno antecipado com `next`. Não há status `paused` no engine.

### Cited Findings

- Chave: SHA-256 de `prompt` + fingerprint, mais o índice de ocorrência desse hash. Fingerprint: `model`, `schema`, `cwd`, `tools`, `disallowedTools`, `agents`, `settingSources`. Não inclui `mcpServers`, `sandbox`, `disallowedTools` está incluído, `prompt` entra à parte. [CODE] `journal.ts:67-73`, `engine.ts:791-801`.
- Hit de journal: emite `step-start`/`step-end` com `cached: "journal"` e devolve `cached.result` sem chamar o backend. [CODE] `engine.ts:856-859`.
- O `result` gravado é o valor já redactado, para o resume e as etapas seguintes verem o mesmo texto. [CODE] `engine.ts:1094-1100`.
- `memo` é outro cache, entre runs, só com tools read-only e cwd git; cloud não memoriza. Não substitui o journal do mesmo run. [CODE] `engine.ts:862-883`, `workflow.ts:125-129`.
- Resume: o chamador passa o `runId` anterior. `start_workflow.resumeRunId` vira o `runId` do job. [CODE] `engine.ts:125-126`, `mcp-server.ts:122`, `job-spawn.ts:75`.
- Comentário do journal: editar o prompt reexecuta aquela etapa e as que passam a depender do resultado novo, não "tudo depois". [CODE] `journal.ts:1-7`.
- `ctx.exec` não é journaled; o resume roda o comando de novo. [CODE] `workflow.ts:253-259`.
- Cancelamento (`RunOptions.signal`, `cancel_workflow`, SIGINT/SIGTERM): agentes ativos cancelados, etapa de escrita em voo revertida, nada de novo começa, status `cancelled`, journal das etapas concluídas permanece. Mensagem: `relaunch with resumeRunId="<id>"`. [CODE] `engine.ts:157-161`, `engine.ts:674`, `engine.ts:1316-1319`, `projection.ts:12`.
- Processo morto ou heartbeat parado: o job aparece `failed` com a mesma dica de `resumeRunId`. [CODE] `job-state.ts:206-230`, `mcp-server.ts:23-24`.
- Cloud interrompido: a tentativa seguinte reanexa o `agentId` deixado no log; se não alcança, não cria outro naquela tentativa (`reattachFailed`). O texto de `cancel_workflow` diz que um resume depois de um cancel que nomeou cloud agents cria agentes novos, com custo novo. [CODE] `backend.ts:76-80`, `backend-cloud.ts:242-257`, `engine.ts:970-973`, `mcp-server.ts:183-187`.
- Budgets no contexto: `maxCents` compara com `spentCents()` = soma, por tentativa, de `max(rawCostCents, chargedCents)`, incluindo execuções anteriores. `maxTokens` vale mesmo se `getUsage` falhar (tokens dos `turn-ended`). `assertBudget` roda antes de trabalho novo: conta, teto de tokens do run, teto de centavos. [CODE] `workflow.ts:190-206`, `engine.ts:578-580`, `engine.ts:700-708`.
- Teto ao vivo: no fim do turno, se a soma (gasto já fechado + turnos em voo) passa `maxTokens`, corta todas as tentativas ativas. `maxTokensPerStep` corta só a etapa. Esses cortes não são retentados. [CODE] `engine.ts:651-669`, `engine.ts:1000-1012`, `engine.ts:1110-1116`.
- `getUsage` local pode falhar com 403 `feature_unavailable`; aí os tokens vêm dos eventos e o teto em centavos não conta a tentativa. [CODE] `engine.ts:721-739`.
- Defaults de tentativa: `retries` default 1 (logo 2 tentativas: `1 + retries`), `schemaRetries` default 2, timeout default 20 min no comentário da opção. Erro `not-retryable` (`ConfigurationError` / `AuthenticationError` com `isRetryable: false`) e `usage-limit` não retentam. [CODE] `workflow.ts:101-106`, `engine.ts:970`, `engine.ts:1134-1146`.
- Status finais do engine: `finished` com `result`, `failed` com `error`, `cancelled`. Recusa antes de escrever log: `refused: true`, status `failed`. Não há estado pausado. [CODE] `engine.ts:177-183`, `engine.ts:1301-1331`, `engine.ts:532`.
- Um workflow pode retornar cedo com `next` e o engine grava isso como `finished`. Exemplo: `implement-issue` devolve `status`, `runId` e `next` no checkpoint de seams. O `resumeRunId` na tool, não dentro de `args`, é o que reabre o journal. [CODE] `packages/runtime/workflows/implement-issue.ts:787`, `mcp-server.ts:122`, `.agents/skills/run-workflow/SKILL.md:26-28`.
- Retention: fora da janela (default últimas 30 runs ou 14 dias), o `result` do journal é apagado e o run não retoma. `RunPrunedError` recusa antes de escrever. [CODE] `engine.ts:150-155`, `engine.ts:557-558`, `journal.ts:48-50`.
- Config é relida no início de cada execução, resume incluído. Se o hash do código do workflow mudou, emite warning de versões misturadas; o journal antigo continua valendo para as chaves que batem. [CODE] `engine.ts:542`, `engine.ts:247-251`.

### Inferences

- Retomar não reenvia rules nem skills às etapas já gravadas: o chamador recebe o `result` salvo. Só a etapa cuja chave mudou, ou que não está no journal, cria agente de novo e aí passa pelo `settingSources` da execução nova.

### Gaps

- Não há, neste código, um ponto em que o engine pare no meio do `def.run` e persista a posição do programa além do journal de `agent()`. Um `return` antecipado é convenção do workflow (`next`), não um checkpoint do motor.

## Lacunas contra "a etapa deveria ver as mesmas rules, skills, subagents, MCP e cwd desta sessão do IDE"

Só o que o código ou os tipos mostram. A doc do kit não promete essa paridade: o default é opt-in `["project","team","mdm"]` e a skill de autoria manda não carregar `"user"`. [CODE] `engine.ts:142-146`, `.agents/skills/skill-to-workflow/references/cost.md:50`.

### Takeaway

A etapa não recebe o transcript, as user rules, a lista de MCP habilitados no chat, as skills da sessão nem os workspace roots do IDE. Recebe o `cwd` do processo (`WF_CWD` ou `--cwd`) e, no local, as camadas que `settingSources` nomear. `"user"` e `"plugins"` ficam de fora do default. Subagents de arquivo não são lidos pelo kit. No cloud, `settingSources`, tools, sandbox e `cwd` local nem são enviados.

### Cited Findings

- Nada em `start_workflow` aceita rules, skills, subagents, MCP da sessão ou cwd vindo do chat. O cwd do servidor é `WF_CWD` ou `process.cwd()`. [CODE] `mcp-server.ts:68`, `mcp-server.ts:117-124`.
- `local.dirs` (pastas extras do workspace) existe no SDK e não é setado. O comentário do tipo diz que rules, skills e metadata de workspace carregam de cada path único, com `cwd` primeiro. Sem `dirs`, só o `cwd` da etapa entra por esse campo. [CODE] `options.d.ts:164-170`, `backend.ts:465-470`.
- Default sem `"user"` e sem `"plugins"`. O tipo lista os dois. A skill de custo afirma que `"user"` traz `~/.cursor/agents`, `~/.cursor/skills`, `~/.claude/skills` e o MCP do usuário; o engine não liga essa source salvo config, role ou opção da chamada, e ainda assim o cap pode removê-la. [CODE] `repo-code.ts:17`, `options.d.ts:38`, `cost.md:50`, `config/resolve.ts:140-142`.
- `"all"` está no tipo e o comentário da API de autoria diz que o cap default deixa `"all"` de fora. O template não lista `"all"`. [CODE] `options.d.ts:38`, `templates/global-config.json:8`, `.agents/skills/skill-to-workflow/references/runtime-api.md:79`.
- MCP da etapa local = guarda `workflows` sem tools, mais o que o workflow passar em `mcpServers`, mais o que o SDK subir das sources. O runtime não copia os servidores habilitados no chat. Com `"project"`, a medição viu o `.cursor/mcp.json` subir, e a guarda inline vence o servidor `workflows` do arquivo pelo nome. [CODE] `engine.ts:104-118`, `verificacoes-locais.md:111-112`, `docs/usage/02-configuracao-inicial.md:226-233`.
- Skills e subagents da sessão não são enumerados nem colados no prompt. Subagent inline só se `agents` vier na chamada, e a tool `task` só existe se a allowlist a incluir (ou se não houver allowlist). [CODE] `workflow.ts:95-99`, `options.d.ts:530-531`.
- Cloud não recebe `local.cwd`, `settingSources`, `sandboxOptions`, `customTools`, `tools` nem `disallowedTools`. O warning diz que a VM carrega project, team e plugins sempre, e ignora o array pedido. [CODE] `backend-cloud.ts:237-297`, `options.d.ts:186-191`.
- `systemPrompt` e `mode` existem e ficam unset. Não há canal no create para "as rules desta conversa do IDE". [CODE] `options.d.ts:567-604`, `backend.ts:460-471`.
- Fingerprint do journal omite `mcpServers` e `sandbox`. Um resume pode devolver o resultado velho mesmo se esses dois tiverem mudado, sem criar agente. [CODE] `engine.ts:791-801`, `engine.ts:856-859`.

### Inferences

- Igualar a etapa à sessão do IDE exigiria, no mínimo, passar o que hoje não vai em `Agent.create`: `"user"` (e o que mais a sessão carregue que não esteja em project/team/mdm), `dirs` se houver mais de uma raiz, os `mcpServers` da sessão que não estão no `.cursor/mcp.json` do `cwd`, e algum texto de user rules se elas não forem a source `"user"`. Nenhum desses argumentos é preenchido pelo `start_workflow`.

### Gaps

- Os `.d.ts` não dizem que `"user"` é a mesma coisa que as user rules da conversa do Cursor. Sem isso, a afirmação "user rules da IDE não chegam" fica demonstrada só pela ausência de campo e de leitura de arquivo, não por um mapa oficial source → arquivo de user rules.
- Não foi medido, neste checkout, o conjunto real de skills que `["project","team","mdm"]` carrega numa máquina com skills de usuário. A contagem 58 continua com origem não isolada.
