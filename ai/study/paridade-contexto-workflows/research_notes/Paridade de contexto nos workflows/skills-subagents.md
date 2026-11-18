# Skills, subagents e o que um step headless do Cursor SDK carrega

Verificado em 2026-11-17. `cursor.com` e `code.claude.com` responderam HTTP 200 neste fetch (não houve 403). O pacote lido é `@cursor/sdk` **1.3.1** em `/home/rodrigo/Workspace/cursor-workflows-starter/node_modules/@cursor/sdk` (`package.json` `version`). As páginas Cursor de skills, subagents, SDK TypeScript e plugins, baixadas hoje, coincidem com o espelho `ai/docs/cursor/` de 2026-11-11 no conteúdo citado abaixo; a diferença vista foi o rodapé Sitemap e a seção local "Agent Skills standard" do espelho. A página de skills do Claude Code baixada hoje difere do espelho `ai/docs/claude-code/skills/extend-claude-with-skills.md` (cabeçalho "mirrored 2026-10-11") na frase de cloud threads; a tabela de frontmatter de controle continua a mesma. O relatório de estudo de 2026-11-11 não foi usado como fonte.

Não existe tipo "workflow step" em `@cursor/sdk`. O step do kit `cursor-workflows-starter` é `ctx.agent(prompt, opts)` e chama `Agent.create`. O `agent()` de dynamic workflow do Claude Code é outro runtime.

## Onde o Cursor e o Claude Code descobrem skills, e o que o SDK carrega sozinho

### Takeaway

O IDE Cursor descobre `SKILL.md` em pastas de projeto, de usuário, de compatibilidade e de plugin, e apresenta as skills ao agente; o corpo entra no turno quando a skill é invocada. Um agente local do `@cursor/sdk` 1.3.1 só monta esse catálogo se `local.settingSources` ligar a camada correspondente. Sem esse campo, o runtime não descobre skills. Não há campo de API para entregar um `SKILL.md`.

### Cited Findings

- Cursor, ao iniciar, descobre skills e as oferece ao Agent. O agente decide a relevância pelo contexto. Digitar `/` e escolher o nome anexa a skill a uma mensagem. Custom Mode (Option+Enter / Alt+Enter) mantém a skill na sessão inteira. — [Agent Skills](https://cursor.com/docs/skills.md) (fetch 2026-11-17)
- Pastas que o IDE carrega: `.agents/skills/` e `.cursor/skills/` (projeto); `~/.agents/skills/` e `~/.cursor/skills/` (usuário, nesta máquina). Compatibilidade: `.claude/skills/`, `.codex/skills/`, `~/.claude/skills/`, `~/.codex/skills/`. Cada skill é um diretório com `SKILL.md`. A caminhada é recursiva. Um `.cursor/skills/` ou `.agents/skills/` aninhado no repositório também entra, e a skill aninhada só aparece quando o agente trabalha em arquivos daquele diretório. — [Agent Skills](https://cursor.com/docs/skills.md)
- `~/.cursor/skills/` não vai para Cloud Agents até "Sync Skills for Cloud Agents". `~/.agents/skills/` e skills locais não sincronizadas não são copiadas para Cloud Agents, Agents Window em SSH remoto, nem self-hosted workers. Automations não carregam skills pessoais sincronizadas; a skill da automation fica em `.cursor/skills/` do repositório. — [Agent Skills](https://cursor.com/docs/skills.md)
- Skills de um repositório GitHub entram empacotadas num plugin publicado num marketplace (Customize → From GitHub Repository, com `.cursor-plugin/marketplace.json`, ou team marketplace). Publicar uma skill pessoal tira-a de `~/.cursor/skills/` e passa a carregá-la pelo plugin. — [Agent Skills](https://cursor.com/docs/skills.md), [Plugins](https://cursor.com/docs/plugins.md) (fetch 2026-11-17)
- Install de plugin: Customize → Install, escopo project ou user. Desenvolvimento local em `~/.cursor/plugins/local`. — [Plugins](https://cursor.com/docs/plugins.md)
- Descoberta de componente quando o manifest não fixa o caminho: `skills/` = cada subdiretório com `SKILL.md`; `agents/` = arquivos `.md`, `.mdc` ou `.markdown`; `SKILL.md` na raiz do plugin vale como skill única se não houver `skills/` nem campo `skills` no manifest. Um campo de caminho no manifest substitui a pasta default. — [Plugin reference](https://cursor.com/docs/reference/plugins.md) (fetch 2026-11-17)
- Skills built-in do IDE (`/automate`, `/canvas`, `/create-skill`, `/create-subagent`, `/review`, `/review-bugbot`, `/review-security`, `/sdk`, `/shell`, e as demais da tabela) são geridas pelo Cursor e aparecem junto das skills do usuário. Algumas o Agent também usa sozinho quando o pedido casa com o propósito. — [Agent Skills](https://cursor.com/docs/skills.md)
- `SettingSource = "project" | "user" | "team" | "mdm" | "plugins" | "all"`. `local.settingSources` escolhe as camadas de disco. A doc diz: sem `local.settingSources`, só entram MCP servers inline. Cloud ignora `local.settingSources` e sempre carrega `project`, `team` e `plugins`. — [Cursor TypeScript SDK](https://cursor.com/docs/sdk/typescript.md) (fetch 2026-11-17), tipos em `dist/esm/options.d.ts`
- No bundle 1.3.1, `DO(settingSources)` trata `undefined` ou `[]` como nenhuma camada (`FO([])`: project, user, team, mdm, plugins todos falsos). `"all"` liga `project`, `user`, `team`, `mdm`, `plugins` e recusa mistura com nomes individuais. A extensibilidade local (rules, skills, subagents de arquivo) só é construída quando project, user, team, managed-skills ou plugins está ligado. — `dist/esm/305.js`, funções `DO` / `FO` / `$O` e o bloco `localExtensibility:iO(...)` (pacote 1.3.1)
- Com a camada ligada, o mesmo bundle varre, no workspace e no home, estes subdiretórios: `.cursor/skills`, `.agents/skills`, e, porque `getThirdPartyExtensibilityEnabled` nesse executor é `() => true`, também `.claude/skills`, `.codex/skills`, `.grok/skills`. Escopo projeto usa as raízes de workspace; escopo usuário usa `os.homedir()`. — `305.js`, array `gm` e funções `Em`, `xm`, `Pm`
- `~/.cursor/skills-cursor` está marcado `builtin: true` (`bm(homedir)`). O filtro de raiz inclui esse diretório só quando o sync de managed skills devolve status `"synced"`, e esse sync só corre com `includeManagedSkills`, que o executor liga quando `settingSources` contém `"team"` e existe dashboard transport (API key). Caso contrário o diretório vai para `excludedRoots`. — `305.js`, `iO` / `prepareLocalExtensibility` / `allowedRoots`
- `local.dirs` é fundido com `cwd` para rules, skills e metadata de workspace. — `options.d.ts` (`LocalAgentOptions.dirs`); [SDK](https://cursor.com/docs/sdk/typescript.md)
- Com `local.fs`, "no skills are discovered", mesmo com `settingSources`. Rules de projeto ainda saem de `<workspace>/AGENTS.md` e `<workspace>/.cursor/rules/**/*.mdc` se `"project"` estiver ligado. O README diz para passar as skills ao agente. Não há parâmetro `skills` em `AgentOptions`. — `dist/esm/filesystem/session-context.d.ts`; `README.md` seções "Workspace and project rules" e "Tools under fs"; `options.d.ts` (`fs`)
- `systemPrompt` substitui o prompt de harness do loop principal. "Tool JSON schemas and ambient context (rules, skills, `<user_info>`) are unaffected." Subagents lançados por `task` mantêm os próprios prompts. — `options.d.ts`; [SDK](https://cursor.com/docs/sdk/typescript.md) seção "Replacing the system prompt"
- O scan de workspace (rules, skills, `AGENTS.md`, ignore) é reutilizado por 20s (`Cursor.configure({ local: { workspaceScanCacheTtlMs } })` ou `CURSOR_RIPWALK_CACHE_TTL_MS`). — `dist/esm/sdk-config.d.ts`
- Plugins no SDK: MCP, skills e subagents de plugin entram com `settingSources` contendo `"plugins"`. `importThirdPartyPlugins` default é `false`; plugins cuja source é `"claude-plugin"` são filtrados quando essa flag é falsa. — `305.js` (`includePluginExtensibility`, `importThirdPartyPlugins??!1`, filtro `"claude-plugin"`)
- Claude Code, página ao vivo: Enterprise em managed settings; pessoal `~/.claude/skills/<skill-name>/SKILL.md` (não em Cowork nem cloud sessions); projeto `.claude/skills/` (não em cloud threads de um project); aninhado `<subdir>/.claude/skills/`; diretório extra via `--add-dir`; plugin `<plugin>/skills/<skill-name>/SKILL.md` como `/plugin-name:skill-name`; skills da conta claude.ai. O nome de pasta `synced` é reservado para o download de claude.ai em `~/.claude/skills/synced/`. — [Extend Claude with skills](https://code.claude.com/docs/en/skills.md) (fetch 2026-11-17)
- Essas cargas de projeto dependem do setting source `project`, que no Claude Code está ligado por default. `strictPluginOnlyCustomization`, bare mode e `--safe-mode` restringem mais. — mesma página, seção de diretórios adicionais (o espelho de 2026-10-11 já dizia isso; a frase de "cloud threads" é da página de 2026-11-17)
- Plugin Claude Code: componentes na raiz do plugin em `skills/`, `agents/`, `hooks/hooks.json`, `.mcp.json`. Skill de plugin leva prefixo `/plugin-name:skill-name`. Uma pasta de skill com `.claude-plugin/plugin.json` carrega como plugin. — [Create a plugin](https://code.claude.com/docs/en/plugins) via espelho `ai/docs/claude-code/plugins/claude-create-plugin-doc.md` (cabeçalho mirrored 2026-10-11; esta página não foi rebuscada em 2026-11-17) e a página de skills ao vivo

### Inferences

- "O SDK carrega skills sozinho" só é verdade no disco do host, e só para as camadas presentes em `settingSources`. O default do tipo, quando o campo é omitido, é catálogo vazio. O default do kit (`["project","team","mdm"]`) não é o default do SDK.
- Com `"project"`, o runtime 1.3.1 também lê `.claude/skills`, `.codex/skills` e `.grok/skills` do workspace. A página de skills do IDE nomeia Claude e Codex e não nomeia `.grok/skills`.
- Skills built-in do IDE que vivem em `~/.cursor/skills-cursor` não acompanham um step que não tenha `"team"` com dashboard, mesmo que `"user"` esteja ligado: o filtro exclui essa pasta.
- Cloud Agent do SDK não usa `settingSources`. Skills de projeto vêm do repo clonado. Skills pessoais locais não. `cloud.agentServeAgent` é outro caminho: o pod procura skills em `/cursor/stores/user/agent-serve/<agentServeAgent>/skills` (`options.d.ts`, `CloudAgentOptions.agentServeAgent`).

### Gaps

- Não há, na doc pública do SDK, uma lista das pastas de skill. A lista `.grok/skills` e o gate de `skills-cursor` estão só no bundle minificado. A intenção de produto desse gate não está documentada.
- Não li o montador de prompt que decide se o corpo do `SKILL.md` entra no turno ou só a `description`. A doc do IDE diz que o agente "é apresentado" às skills e que recursos carregam sob demanda. Não há prova, no `.d.ts`, de um equivalente ao `/nome` que force o corpo.
- A página de plugins do Claude Code não foi rebuscada em 2026-11-17.

## Frontmatter que muda o fluxo: `name`, `description`, `argument-hint`, `disable-model-invocation`, `--review`, `--interview`

### Takeaway

Na doc de skills do Cursor, os campos que mudam se a skill entra no contexto são `description` (relevância), `paths` (quando a skill é oferecida) e `disable-model-invocation: true` (só via `/skill-name`). `argument-hint` não está nessa tabela. `--review` e `--interview` não são flags do harness Cursor; `/review` é o nome de uma skill built-in.

### Cited Findings

- Tabela oficial Cursor, fetch 2026-11-17. Obrigatórios: `name` (minúsculas, números, hífens; tem de ser igual à pasta pai) e `description` (o agente usa para decidir relevância). Opcionais: `paths` (globs; a skill só aparece quando o agente trabalha com arquivos que casam; `globs` legado ainda é aceito), `disable-model-invocation`, `icon`, `color`, `metadata`. — [Agent Skills](https://cursor.com/docs/skills.md) seção "Frontmatter fields"
- "`disable-model-invocation: true`" faz a skill comportar-se como slash command: só entra no contexto quando se digita `/skill-name`. O default é aplicação automática quando o agente a julga relevante. — mesma página, "Disabling automatic invocation"
- `/migrate-to-skills` converte slash commands em skills com `disable-model-invocation: true`. — mesma página
- A página não contém `argument-hint`, `allowed-tools`, `context`, `agent`, nem qualquer flag `--review` ou `--interview`. A busca na página baixada por `argument-hint` deu zero. `/review`, `/review-bugbot` e `/review-security` são nomes de skills built-in invocadas com `/`. — [Agent Skills](https://cursor.com/docs/skills.md)
- O bundle 1.3.1, na função `Rf`, lê `argument-hint` do frontmatter (string, ou array juntado como `[a b]`) e guarda `argumentHint` junto de `name`, `description` e `content`. A função `og` trata `disable-model-invocation: true`. Isso é parser do runtime, não uma linha da doc de skills. — `305.js`
- A skill built-in `create-skill` em `/home/rodrigo/.cursor/skills-cursor/create-skill/SKILL.md` documenta `disable-model-invocation: true` como o modo de carregar só quando o nome é explícito. O arquivo não contém `argument-hint` (grep no diretório `~/.cursor/skills-cursor`).
- Ilustração, não spec: `/home/rodrigo/.claude/skills/run-spec/SKILL.md` linhas 2–5 têm `name: run-spec`, uma `description`, `argument-hint: "<#spec-issue | .scratch/<slug> | run-spec handoff path> [more specs…] [--merge] [notes]"` e `disable-model-invocation: true`. `[--merge]` está dentro da string de hint.
- Spec aberta (espelho 2026-10-11 de agentskills.io): campos `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools` (experimental). Sem `argument-hint`. — `ai/docs/shared/skills-standard/agentskills-specification.md`
- Claude Code, página ao vivo: `argument-hint` é "Hint shown during autocomplete to indicate expected arguments". Não executa nada. `disable-model-invocation: true` impede carga automática, impede preload em subagents e impede a skill de correr como prompt de scheduled task. `user-invocable: false` esconde do menu `/`. `allowed-tools` pré-aprova tools no turno da invocação. `disallowed-tools` tira tools enquanto a skill está ativa. `context: fork` corre num subagent; `agent` escolhe o tipo; `background` (default `true`) manda o fork para background. `model` e `effort` valem pelo resto do turno, ou no fork. `paths` limita a ativação automática. `hooks` registra hooks na invocação. Campo desconhecido é ignorado. Fora do Claude Code, upload/packaging rejeita chave extra com `Unexpected key(s) in SKILL.md frontmatter: argument-hint. Allowed properties are: allowed-tools, compatibility, description, license, metadata, name`. — [Extend Claude with skills](https://code.claude.com/docs/en/skills.md) (fetch 2026-11-17)
- A mesma página não documenta `--review` nem `--interview` como campos. A busca na página baixada por `--review` e `--interview` deu zero. `/code-review` aparece como skill bundled, que é um nome, não uma flag.

### Inferences

- `--merge` no `argument-hint` de `run-spec` é convenção do texto daquela skill. O harness Cursor não tem um flag `--review` ou `--interview` na spec de `SKILL.md`. Quem quiser esse comportamento escreve-o no corpo.
- `argument-hint` pode sobreviver no parser do runtime Cursor 1.3.1 e alimentar autocomplete de comando, mas a doc de skills do Cursor não o lista e não lhe atribui efeito no contexto. Tratar o campo como controle de fluxo do IDE não tem fonte na página de skills.
- `allowed-tools` da spec aberta e do Claude Code não está na tabela Cursor. Um `SKILL.md` com `allowed-tools` não muda o allowlist de um `Agent.create` do SDK; o allowlist é `tools` / `disallowedTools`.

### Gaps

- Não há fonte pública que diga o que o IDE Cursor faz com um `argument-hint` presente. O parser do bundle mostra que o campo é lido; não mostra a UI que o consome.
- Não verifiquei se o IDE rejeita frontmatter desconhecido ou se o ignora. O Claude Code documenta "ignora campo desconhecido". A página Cursor não diz.

## Definições de subagent e o contexto que o filho recebe

### Takeaway

No IDE, subagents de arquivo vivem em `.cursor/agents/` (e pastas de compatibilidade, inclusive no home) e o filho começa com contexto limpo, herdando as tools do pai, MCP incluído. No SDK, o filho inline é `AgentDefinition` (`description`, `prompt`, `model`) passado em `agents`; arquivos `.cursor/agents/*.md` só entram com `settingSources` de projeto; `~/.cursor/agents` a doc do SDK marca como inexistente, e o bundle 1.3.1 não varre o home.

### Cited Findings

- IDE: cada subagent tem a própria janela. "Subagents start with a clean context. The parent agent includes relevant information in the prompt since subagents don't have access to prior conversation history." — [Subagents](https://cursor.com/docs/subagents.md) (fetch 2026-11-17)
- Built-in do IDE: `explore` (busca) e `browser` (MCP de browser). Não se configuram. — mesma página, FAQ
- Locais de arquivo no IDE: projeto `.cursor/agents/`, `.claude/agents/`, `.codex/agents/`; usuário `~/.cursor/agents/`, `~/.claude/agents/`, `~/.codex/agents/`. Em conflito de nome, `.cursor/` ganha de `.claude/` e `.codex/`. Projeto ganha de usuário. — mesma página, "File locations"
- Frontmatter IDE: `name` (opcional, senão o filename), `description` (o Agent lê para delegar; "use proactively" encoraja delegação automática), `model` (`inherit` default, ou id com parâmetros `id[effort=high,context=300k]`), `readonly` (default false: sem edição de arquivo e sem shell que mude estado), `is_background` (default false). — mesma página, "Configuration fields"
- Invocação explícita no IDE: `/verifier ...` ou menção em linguagem natural. O filho pode lançar filhos desde o Cursor 2.5, com limite: o agente principal e os subagents diretos podem lançar; um subagent lançado por outro não lança mais. — mesma página
- "Subagents inherit all tools from the parent, including MCP tools from configured servers." Exceção: cloud subagent usa o MCP do time em cursor.com/agents, não o da sessão local. — mesma página, FAQ
- SDK, tabela de fontes: subagents inline em `agents` no `Agent.create`; arquivo local só `.cursor/agents/*.md` (frontmatter `name`, `description`, `model?`); coluna de arquivo de usuário = "n/a". Inline com o mesmo nome ganha do arquivo. Cloud lê os mesmos arquivos do repo clonado. — [SDK](https://cursor.com/docs/sdk/typescript.md) "Configuration sources" e "Subagents"
- `AgentDefinition`: `description: string` (obrigatório), `prompt: string` (obrigatório, "System prompt for the subagent"), `model?: ModelSelection | "inherit"` (default `"inherit"`), `mcpServers?: Array<string | Record<string, McpServerConfig>>`. A doc diz que referências string são ignoradas e config inline lança `ConfigurationError`; o subagent herda os MCP do pai. O `.d.ts` de conversão diz o mesmo: "Inline `McpServerConfig` entries on a subagent are rejected". — [SDK](https://cursor.com/docs/sdk/typescript.md) tabela `AgentDefinition`; `dist/esm/subagent-conversion.d.ts`; `options.d.ts`
- `"task"` liga subagents. "Subagents launched through it keep their own curated toolsets; the restriction applies to the main agent loop." Proibir `"task"` impede subagents. O mesmo vale para `disallowedTools`. — `options.d.ts` (`tools`, `disallowedTools`); [SDK](https://cursor.com/docs/sdk/typescript.md)
- `local.subagentInherit` é opt-in. Sem ele, o filho fica com "host workspace path, host executors, and no tool-allowlist headers". Com ele, filhos e netos reusam os executor overrides, o reported workspace path, e recebem os mesmos headers de allowed/exclude tools do pai. `resourceProviderOptions` e `reportedWorkspacePath` do pai não passam ao filho, salvo por `subagentInherit`. — `options.d.ts`
- Com `local.fs`, Task children compartilham a árvore, o workspace e o `/tmp` do run, usam o allowlist de tools do pai e não têm shell. Combinar `fs` com `subagentInherit` ou `resourceProviderOptions` é `ConfigurationError`. — `options.d.ts`; `README.md` "Task children"
- Aninhamento no SDK: o filho direto recebe o mesmo executor de subagents e as mesmas custom tools. O neto não lança mais. Background: o resultado volta como turno seguinte no mesmo run (só local). — [SDK](https://cursor.com/docs/sdk/typescript.md) "Nested subagents", "Background subagents"
- `SDKCustomToolContext.sessionId` é outro id no filho da tool `Task`. — `options.d.ts`
- Bundle 1.3.1, classe `Pg.computeAgentsDirs`: só o workspace, pastas `.cursor/agents`, e com third-party ligado `.claude/agents` e `.grok/agents`. Não há `.codex/agents` nem `join(homedir, ".cursor", "agents")`. `new Pg` só é chamado para raízes de workspace quando `includeProjectExtensibility` é verdadeiro. Subagents de plugin vêm de `class Tg` quando plugins estão ligados. — `305.js`
- O Task tool do proto aceita `subagentType: { kind, name? }`, `prompt`, `model`, `resume`, `agentId`, `mode: "unspecified" | "agent" | "plan"`. — `dist/esm/vendor/cursor-sdk-shared/tool-call-types.d.ts`
- Claude Code, espelho 2026-10-11 (página não rebuscada em 2026-11-17): arquivos em `.claude/agents/`, `~/.claude/agents/`, managed settings e `agents/` do plugin. O corpo é o system prompt; o subagent não recebe o system prompt do Claude Code. Contexto inicial de um não-fork: system prompt do agente, mensagem de delegação, CLAUDE.md (Explore e Plan pulam; `omitClaudeMd: true` também), git status (Explore e Plan pulam), skills nomeadas no campo `skills` (conteúdo inteiro, até 32 nomes), roster de irmãos se houver `SendMessage`. Não herda histórico, skills já invocadas na conversa, output style, nem auto memory. — `ai/docs/claude-code/subagents/creating-custom-subagents.md` seções "What loads at startup" e frontmatter
- O mesmo espelho: `skills` faz preload; sem o campo, o subagent ainda pode invocar skills de projeto, usuário e plugin pela tool Skill. Não dá para preload de skill com `disable-model-invocation: true`. `tools` / `disallowedTools` e `mcpServers` são por subagent; em plugin subagent, `hooks`, `mcpServers` e `permissionMode` são ignorados. — mesma fonte
- A página de skills do Claude Code baixada em 2026-11-17 ainda aponta `disable-model-invocation` para o preload em subagents (`/docs/en/sub-agents`), então esse elo continua na doc atual.
- Dynamic workflow do Claude Code: `agent(prompt, { schema, label, stallMs, ... })` cria um subagent. O script não lê o disco; os agents leem. A página não lista um parâmetro `skills` nem `tools` nesse `agent()`. Modelo segue a ordem de subagent. Agentes de workflow não contam no limite de subagents da sessão. — `ai/docs/claude-code/workflows/workflows.md` (espelho local; não rebuscado em 2026-11-17)

### Inferences

- Um filho `Agent.create({ agents })` não recebe o catálogo de skills do IDE como campo. Se o pai tiver `settingSources` que descobrem skills, a doc não diz que o filho ganha essa lista. O que está escrito é contexto limpo no IDE, prompt próprio no `AgentDefinition`, e tools herdadas (doc do IDE) com a ressalva do SDK de que o allowlist do pai não vai no header do filho sem `subagentInherit`.
- A página de subagents do IDE e a página do SDK divergem, e o bundle 1.3.1 fica com o SDK: sem subagents de `~/.cursor/agents`. O IDE também documenta `.codex/agents`; o bundle varre `.grok/agents` e não `.codex/agents`.
- `readonly` e `is_background` existem no markdown do IDE. `AgentDefinition` do SDK não tem esses campos. Background no SDK é comportamento do run quando o modelo pede, não um booleano da definição.

### Gaps

- A doc do SDK não diz se o filho vê rules, skills e `<user_info>` do pai. `systemPrompt` do pai não se aplica ao filho; o resto do ambient context do filho não está especificado.
- Não confirmei se `explore` e `browser` existem num agente headless ou só no IDE. A página de subagents do IDE os lista; a seção Subagents do SDK só mostra definições nomeadas.
- Frontmatter de subagent do Claude Code e o contrato de `agent()` do workflow não foram rebuscados ao vivo em 2026-11-17.

## Como um step passa o corpo da skill, o prompt do subagent e as tools

### Takeaway

O step passa o corpo da skill como texto no `prompt` (ou, no SDK cru, em `systemPrompt`). O prompt do subagent vai em `agents[nome].prompt`. As tools vão em `tools` / `disallowedTools`. `mcpServers` e `local.customTools` são canais separados. Não há campo `instructions` nem `skills`.

### Cited Findings

- `AgentOptions` público: `model`, `apiKey`, `teamId`, `tools`, `disallowedTools`, `systemPrompt`, `name`, `local`, `cloud`, `mcpServers`, `agents`, `agentId`, `idempotencyKey`, `mode`. Sem `skills`, sem `instructions`, sem `argumentHint`. — `dist/esm/options.d.ts`; tabela em [SDK](https://cursor.com/docs/sdk/typescript.md)
- `local.customTools`: `Record<string, SDKCustomTool>` com `description?`, `inputSchema?`, `outputSchema?`, `annotations?`, `execute(args, context)`. Expostos como MCP server `custom-user-tools`. Aplicados em todo `send`, salvo override em `LocalSendOptions.customTools`. Não rodam em cloud (`ConfigurationError` no `send`). Não pedem aprovação interativa. `"mcp"` no allowlist cobre custom tools; omitir `"mcp"` desliga a família MCP inteira. — `options.d.ts`; [SDK](https://cursor.com/docs/sdk/typescript.md) "Custom tools"
- `mcpServers`: `Record<string, McpServerConfig>` stdio (`command`, `args?`, `env?`, `cwd?`) ou http/sse (`url`, `headers?`, `auth?`). Precedência local: send substitui o create (não mescla), depois plugins, depois `.cursor/mcp.json` (`"project"`), depois `~/.cursor/mcp.json` (`"user"`). — [SDK](https://cursor.com/docs/sdk/typescript.md) "What gets loaded"
- `agent.send` aceita string ou `SDKUserMessage` `{ text, images? }`. Esse texto é a mensagem do usuário, não um slot de skill. — `options.d.ts` `SDKUserMessage`
- Kit, `AgentCallOptions` em `packages/runtime/src/runtime/workflow.ts`: `tools`, `disallowedTools`, `agents`, `mcpServers`, `settingSources`, `schema`, `model`, `cwd`, `sandbox`, mais limites de tempo e retry. Sem `systemPrompt`, sem `customTools`, sem `skills`, sem `fs`.
- Default do kit: `DEFAULT_SETTING_SOURCES = ["project","team","mdm"]` em `packages/runtime/src/runtime/repo-code.ts`, aplicado em `engine.ts` quando o run não passa outro. O comentário de `settingSources` no `workflow.ts` diz que `[]` tira AGENTS.md, rules, hooks, MCP e skills, e que o prompt lista os arquivos de contexto que importam.
- O backend local do kit só põe `local.customTools` quando o step tem `schema`: a tool `submit_result`. — `packages/runtime/src/runtime/backend.ts` (`customTools: o.schema ? { [SUBMIT_TOOL]: ... } : undefined`)
- Step cloud do kit avisa que cloud ignora setting sources e que a VM carrega project, team e plugins. — `packages/runtime/src/runtime/backend-cloud.ts`
- Para um step local se comportar como o IDE com uma skill explícita (`disable-model-invocation: true`, que é o caso de `run-spec`): o catálogo, mesmo ligado, não inclui essa skill sozinho, e não existe `/run-spec` na API. O texto do `SKILL.md` tem de estar no `prompt` do `ctx.agent`, ou no `systemPrompt` de um `Agent.create` direto. Subagent usado pela skill (por exemplo um papel nomeado) tem de estar em `agents: { nome: { description, prompt, model? } }` se não estiver em `.cursor/agents/` com `"project"` ligado. Tools que a skill assume têm de estar em `tools`, porque `allowed-tools` do arquivo não é lido pelo SDK.
- `tools: undefined` oferece o toolset padrão do modelo. `tools: []` deixa só texto. Nomes: `"shell" | "read" | "edit" | "grep" | "glob" | "ls" | "task" | "mcp" | "webSearch" | "delete" | "readLints" | "webFetch" | "semSearch" | "updateTodos" | "readTodos" | "askQuestion" | "await" | "generateImage" | "applyAgentDiff"` mais `(string & {})`. Sob `fs`, Shell, ReadLints, SemanticSearch, applyAgentDiff, recordScreen e computerUse não são registrados. — `options.d.ts` `ToolName`; `README.md`

### Inferences

- O caminho mínimo para um step "igual ao IDE com esta skill" é: `settingSources` com a camada da skill se a skill for auto-invocável e o corpo puder ser descoberto; mais o corpo colado no prompt se a skill for `disable-model-invocation` ou se o step usar `fs`; mais `agents` inline para papéis que no IDE viriam de `~/.cursor/agents` ou de um plugin sem `"plugins"`; mais `tools` se o step não puder herdar o toolset cheio.
- `local.customTools` não injeta skill. Injeta uma tool MCP. O kit usa isso só para `submit_result`.

### Gaps

- Não há exemplo oficial de "passar o corpo de uma skill" no SDK. O README do `fs` diz "Pass skills to the agent yourself" sem mostrar o campo. A leitura consistente com os tipos é texto no prompt ou no `systemPrompt`.
- Não medi, nesta pesquisa, um run com `settingSources: ["project"]` para ver se a `description` da skill aparece no request. O código de carga de diretório está no bundle; o formato do bloco injetado no prompt não foi extraído.

## Lacunas de paridade que afastam o step do "rodar a skill aqui no IDE"

### Takeaway

O step headless diverge do IDE porque o catálogo é opt-in por camada, não há invocação `/nome`, skills com `disable-model-invocation` não entram sozinhas, subagents de usuário e de plugin ficam de fora do default, o filho não herda o allowlist sem `subagentInherit`, e `fs` apaga a descoberta de skills. Flags de hint e campos de fluxo do Claude Code não têm efeito documentado no Cursor.

### Cited Findings

- IDE carrega sozinho projeto, usuário, compatibilidade Claude/Codex e plugins instalados. SDK local com `settingSources` omitido não carrega nenhuma dessas camadas (`DO` → tudo falso; doc: sem o campo, só MCP inline). — [SDK](https://cursor.com/docs/sdk/typescript.md); `305.js`
- Default do kit `["project","team","mdm"]` cobre skills e subagents de projeto e o sync de team, e deixa de fora `"user"` (`~/.cursor/skills`, `~/.claude/skills`, `~/.agents/skills`) e `"plugins"`. — `repo-code.ts`; [Agent Skills](https://cursor.com/docs/skills.md)
- Invocação `/skill-name` e Custom Mode são UI do chat. O SDK não tem esses parâmetros. Skill com `disable-model-invocation: true` só entra "when explicitly invoked via `/skill-name`". Num step, isso significa que o corpo não entra pelo catálogo. — [Agent Skills](https://cursor.com/docs/skills.md)
- `local.fs` não descobre skills, não roda hooks, não manda git status, e não oferece shell. Rules de `AGENTS.md` e `.cursor/rules` ainda dependem de `"project"`. — `README.md`; `session-context.d.ts`; `options.d.ts`
- Subagents de `~/.cursor/agents` existem na doc do IDE e estão "n/a" na doc do SDK. O bundle não varre essa pasta. `.codex/agents` está na doc do IDE e não no `Pg` do bundle. `.grok/agents` está no bundle e não na doc do IDE. — [Subagents](https://cursor.com/docs/subagents.md); [SDK](https://cursor.com/docs/sdk/typescript.md); `305.js`
- Allowlist `tools` do pai não restringe o filho, salvo `subagentInherit` (incompatível com `fs`). Com `fs`, o filho compartilha a árvore e o allowlist e não tem shell. A FAQ do IDE diz que o filho herda todas as tools, MCP incluído. — `options.d.ts`; [Subagents](https://cursor.com/docs/subagents.md)
- `AgentDefinition.mcpServers` inline é rejeitado; o filho herda o MCP do pai. O IDE não documenta MCP por arquivo de subagent. O Claude Code documenta `mcpServers` e `skills` no frontmatter do subagent. — `subagent-conversion.d.ts`; espelho `creating-custom-subagents.md`
- `systemPrompt` apaga a identidade de harness do loop principal e não é repassado ao filho. Skills e rules do ambient context do pai continuam, segundo o `.d.ts`, mas isso não reconstitui um Custom Mode. — `options.d.ts`
- Cloud SDK ignora `settingSources`, ignora `local.customTools`, não aceita `tools` / `disallowedTools` / `systemPrompt` (lança `ConfigurationError`), e não carrega `~/.cursor/skills` não sincronizadas. Automations também não carregam skills pessoais sincronizadas. — [SDK](https://cursor.com/docs/sdk/typescript.md); [Agent Skills](https://cursor.com/docs/skills.md)
- `argument-hint`, `context: fork`, `allowed-tools`, `user-invocable` mudam fluxo no Claude Code. Na página de skills do Cursor, desses, só não há equivalente documentado, exceto `disable-model-invocation` e `paths`. `allowed-tools` da spec aberta não altera o `tools` do SDK. — [skills Claude Code](https://code.claude.com/docs/en/skills.md); [Agent Skills](https://cursor.com/docs/skills.md); `options.d.ts`
- Plugins Claude (`source: "claude-plugin"`) são filtrados no SDK enquanto `importThirdPartyPlugins` for false, que é o default do executor. — `305.js`
- O step do kit não expõe `systemPrompt` nem `customTools` ao autor do workflow. Um schema vira a tool `submit_result`, que não existe numa conversa do IDE. — `workflow.ts`; `backend.ts`

### Inferences

- "Rodar a skill aqui no IDE" inclui descoberta automática, menu `/`, e o estado da sessão (plugins instalados, skills de `~/.cursor/skills`, subagents de `~/.cursor/agents`, built-ins em `skills-cursor`). Um step que só cola o corpo no prompt reproduz as instruções e não reproduz esse estado, nem o gate `disable-model-invocation`, nem `paths`, nem Custom Mode.
- Para chegar mais perto no host, sem `fs`: `settingSources: ["project","user","plugins","team"]` (ou `"all"`), `agents` inline para o que estiver só no home, `tools` explícito, e o corpo da skill no prompt quando ela não é auto-invocável. Isso continua sem `/`, sem Custom Mode, e sem a garantia documentada de que o filho vê as skills.

### Gaps

- Não houve run de comparação IDE versus `Agent.create` nesta pesquisa. Os gates acima são da doc e do bundle, não de um transcript de turno.
- Não está documentado se o runtime, com o catálogo ligado, injeta só descrições ou também segue um ponteiro e lê o `SKILL.md` no meio do turno, como o IDE descreve para scripts e `references/`.
- O efeito de `paths` num agente SDK (sem "arquivos abertos" de editor) não está na página do SDK.
