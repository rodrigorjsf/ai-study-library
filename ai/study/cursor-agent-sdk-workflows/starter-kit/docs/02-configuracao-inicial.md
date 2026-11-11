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
{ "mcpServers": { "workflows": { "command": "${workspaceFolder}/node_modules/.bin/tsx", "args": ["${workspaceFolder}/src/mcp-server.ts"],
  "env": { "CURSOR_API_KEY": "${env:CURSOR_API_KEY}", "WF_CWD": "${workspaceFolder}" } } } }
```

Só adicione essa linha se a variável estiver mesmo definida: interpolada vazia, ela pode encobrir o login salvo
(não verificado; na dúvida, deixe de fora e use `wf login`).

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

> **Validação de modelo:** em runs locais, o SDK confere o ID (ou alias) contra o catálogo da sua conta antes de
> rodar. Se o ID não existir para você, a etapa falha com "Cannot use this model". Uma substituição feita **do
> lado do servidor** por política do admin **não é detectável** pelo SDK: `RunResult.model` devolve o modelo
> pedido, não o que rodou. Para garantir o modelo, combine com o admin a lista liberada e confira em
> `npm run models`.

## 3. Teto de custo

| Onde | Como |
|---|---|
| CLI | `--max-cents 200`, `--max-tokens 2000000` |
| MCP / CLI (default) | Variável `WF_MAX_CENTS` (no `mcp.json` do exemplo: `500`) |
| Dentro do workflow | `ctx.budget.remainingCents()`, para rebaixar o modelo antes de estourar |

Como funciona:

- O teto é checado **antes** de cada etapa (e de cada nova tentativa). Etapas que já começaram não são
  interrompidas, então a ultrapassagem pode chegar a **concorrência × custo de uma etapa** (ex.: 4 etapas em
  `parallel`). Para tetos apertados, use `concurrency` baixa.
- O custo de cada etapa é lido com `agent.getUsage()` ao fim dela, inclusive quando ela falha ou estoura o tempo.
  O SDK avisa que o custo "pode atrasar um pouco depois do fim da run"; o engine tenta ler de novo algumas vezes,
  mas um custo que chegue depois disso fica de fora da soma.
- `chargedCents` é **0 para uso incluído no plano**. Se a sua conta consome uma franquia, use também
  `--max-tokens`.
- Se o limite da conta ou do time estourar no meio, o esperado é um `RateLimitError` (a doc do erro cita "usage
  limits exceeded"); o engine converte o não retentável em falha "Limite de uso do Cursor atingido". Pode ser que
  o teto apareça como run com `status: "error"` em vez de exceção [I]; nesse caso a etapa falha após as
  tentativas, com a mensagem do SDK.

## 4. Variáveis de ambiente

| Variável | Default | Efeito |
|---|---|---|
| `CURSOR_API_KEY` | — | Chave usada quando não há `apiKey` explícita |
| `WF_CWD` | diretório atual | Repositório onde os agentes trabalham (MCP) |
| `WF_MAX_CENTS` | sem teto | Teto padrão por run |
| `WF_MAX_TOKENS` | sem teto | Teto padrão de tokens por run |
| `WORKFLOWS_DIR` | — | Pasta extra de workflows (além de `workflows/` do kit e `.agents/workflows/` do repositório) |
| `WF_MODEL_*` | ver §2 | Mapa de modelos do exemplo |
| `NO_OPEN_BROWSER` | — | `wf login` imprime a URL em vez de abrir o navegador |

## 5. Contexto do projeto nos agentes

O engine cria os agentes com `settingSources: ["project", "team", "mdm"]`, o que carrega:

- `AGENTS.md` e `.cursor/rules/**` do repositório;
- skills do projeto (`.agents/skills/` e `.cursor/skills/` como nativas; `.claude/skills/`, `.codex/skills/` como
  compatibilidade), hooks e `.cursor/mcp.json` do projeto;
- regras e hooks do time e hooks Enterprise (MDM).

Para isolar os agentes das regras do repositório (por exemplo, num repositório não confiável), passe
`settingSources` sem `"project"` em `RunOptions`.

> **Recursão:** como o `.cursor/mcp.json` do projeto é carregado, o agente de uma etapa enxerga o próprio MCP
> server `workflows`. O engine marca o ambiente com `WF_INSIDE_WORKFLOW=1`, e o servidor e o CLI se recusam a
> iniciar workflows quando essa marca está presente.
