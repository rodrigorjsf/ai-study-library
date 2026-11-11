# 02 · Configuração inicial

## 1. Autenticação: de quem é o uso?

O SDK procura a chave nesta ordem: opção `apiKey` → variável `CURSOR_API_KEY` → chave salva por
`Cursor.auth.login()` (`~/.cursor/sdk/auth.json`).

| Cenário | Configuração | Cobrança |
|---|---|---|
| **Desenvolvedor usando pelo chat** (recomendado) | `npm run wf -- login` uma vez por máquina | Conta do próprio usuário. Coerente com o orçamento individual do Enterprise |
| Desenvolvedor sem navegador (SSH, devcontainer) | Gerar uma chave de usuário no dashboard e exportar `CURSOR_API_KEY`, ou `NO_OPEN_BROWSER=1 npm run wf -- login` e abrir a URL em outra máquina | Conta do usuário |
| CI / GitHub Actions / Automations | Chave de **service account** (Enterprise) como secret `CURSOR_API_KEY` | Pool do time, sem atribuição por pessoa |
| Usuário em mais de um time | Passar `teamId` (o kit ainda não expõe a opção; adicione em `RunOptions` se precisar) | O time indicado |

**O que não funciona:**

- Chaves **Team Admin** não são aceitas pelo SDK.
- O SDK **não** reaproveita o login da IDE nem o da CLI `agent`: são credenciais separadas. Não tente ler o token
  da IDE (Keychain etc.). Não é suportado, quebra sem aviso e é ruim para conformidade.

**Segurança da chave salva:** `~/.cursor/sdk/auth.json` fica em texto puro e a chave vale 90 dias. Em máquinas
compartilhadas, prefira `CURSOR_API_KEY` vinda de um gerenciador de segredos.

Para passar a chave ao MCP server sem gravar em arquivo, use interpolação no `mcp.json`:

```json
{ "mcpServers": { "workflows": { "command": "npx", "args": ["tsx", "${workspaceFolder}/src/mcp-server.ts"],
  "env": { "CURSOR_API_KEY": "${env:CURSOR_API_KEY}", "WF_CWD": "${workspaceFolder}" } } } }
```

## 2. Modelos

Os IDs dependem do plano e das restrições do admin. Liste com `npm run models`. O exemplo usa quatro papéis:

| Variável | Papel | Default do exemplo |
|---|---|---|
| `WF_MODEL_CLASSIFY` | Classificar a complexidade quando a issue não tem label | `auto-low` |
| `WF_MODEL_LOW` | Tarefas mecânicas | `auto-low` |
| `WF_MODEL_MED` | Implementação típica | `composer-2` |
| `WF_MODEL_HIGH` | Implementação complexa | `gpt-5.3-codex` |
| `WF_MODEL_REVIEW` | Code review | `gpt-5.3-codex` |

Os defaults vêm do `dag-task-runner` do cookbook oficial. Confirme todos com `npm run models` antes de usar.

> **Fallback silencioso:** se o modelo pedido estiver bloqueado, o Cursor pode rodar outro sem erro. O engine
> compara o modelo pedido com `RunResult.model` e emite `warning`. Com `strictModel: true` na etapa, a etapa
> falha.

## 3. Teto de custo

| Onde | Como |
|---|---|
| CLI | `--max-cents 200`, `--max-tokens 2000000` |
| MCP / CLI (default) | Variável `WF_MAX_CENTS` (no `mcp.json` do exemplo: `500`) |
| Dentro do workflow | `ctx.budget.remainingCents()`, para rebaixar o modelo antes de estourar |

Como funciona:

- O teto é checado **antes** de cada etapa, então um run pode ultrapassá-lo pelo custo de uma etapa.
- `chargedCents` é **0 para uso incluído no plano**. Se a sua conta consome uma franquia, use também
  `--max-tokens`.
- Se o limite da conta ou do time estourar no meio, o SDK lança `RateLimitError` e o workflow falha com
  "Limite de uso do Cursor atingido".

## 4. Variáveis de ambiente

| Variável | Default | Efeito |
|---|---|---|
| `CURSOR_API_KEY` | — | Chave usada quando não há `apiKey` explícita |
| `WF_CWD` | diretório atual | Repositório onde os agentes trabalham (MCP) |
| `WF_MAX_CENTS` | sem teto | Teto padrão por run |
| `WORKFLOWS_DIR` | `./workflows` do kit | Pasta de onde os workflows são carregados |
| `WF_MODEL_*` | ver §2 | Mapa de modelos do exemplo |
| `NO_OPEN_BROWSER` | — | `wf login` imprime a URL em vez de abrir o navegador |

## 5. Contexto do projeto nos agentes

O engine cria os agentes com `settingSources: ["project", "team"]`, o que carrega:

- `AGENTS.md` e `.cursor/rules/**` do repositório;
- skills e hooks do projeto;
- regras e hooks do time.

Para isolar um agente das regras do repositório (por exemplo, num repositório não confiável), altere
`settingSources` em `src/runtime/engine.ts`.
