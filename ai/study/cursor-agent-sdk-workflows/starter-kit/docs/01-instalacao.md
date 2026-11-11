# 01 · Instalação

## 1. Requisitos

| Item | Versão | Por quê |
|---|---|---|
| Node.js | **≥ 22.13** | Exigência do `@cursor/sdk` (`engines.node`) |
| Sistema | macOS (arm64/x64), Linux (arm64/x64) ou Windows x64 | O SDK traz binários por plataforma como dependências opcionais (`@cursor/sdk-<os>-<arch>`) |
| Conta Cursor | Plano pago (Pro, Teams ou Enterprise) | Relatos indicam erro `plan_required` em runs locais no plano Free |
| Cursor IDE | Atual | Para usar pelo chat (MCP e skills). Terminal e CI não precisam da IDE |
| `git` | qualquer recente | O workflow de exemplo cria worktrees e commits |
| `gh` (GitHub CLI) | autenticado (`gh auth login`) | O exemplo lê a issue e, opcionalmente, abre o PR |

> **Não** use `npm install --omit=optional`: isso remove o binário de plataforma do SDK e do `esbuild` (usado
> pelo `tsx`).

## 2. Dependências

| Pacote | Uso |
|---|---|
| `@cursor/sdk` (fixado em `1.3.1`) | Criar agentes, enviar prompts, consultar custo. O SDK está em beta pública: **fixe a versão** e atualize de forma deliberada |
| `@modelcontextprotocol/sdk` | MCP server (stdio) para o Cursor IDE |
| `ajv` | Validação de JSON Schema da saída estruturada |
| `tsx` | Roda os `.ts` direto, sem build |
| `zod` | Peer dependency do `@cursor/sdk` |
| `typescript`, `@types/node` (dev) | Typecheck |

## 3. Instalar

```bash
git clone <seu-fork-deste-kit> cursor-workflows && cd cursor-workflows
npm install
npm run typecheck     # deve terminar sem erros
npm test              # testes offline do engine (sem rede, sem conta)
```

## 4. Login e modelos

```bash
npm run wf -- login     # abre o navegador e grava uma chave de usuário (90 dias) em ~/.cursor/sdk/auth.json
npm run wf -- whoami    # confirma a conta
npm run models          # lista os IDs liberados para você pelo plano e pelo admin
```

Ajuste os IDs do mapa de modelos em `workflows/implement-issue.ts` ou nas variáveis `WF_MODEL_*`
([02 · Configuração](02-configuracao-inicial.md)).

## 5. Teste de fumaça real

Primeiro contato com a API. Use um teto baixo para limitar o custo:

```bash
# Repositório de teste com uma issue simples rotulada "complexity:low"
npm run wf -- run implement-issue --cwd /caminho/do/repo-de-teste --args '{"issue":1}' --max-cents 50
```

O que conferir:

1. No stderr aparecem eventos `step-start`/`step-end` com o modelo pedido em cada etapa.
2. Não há `warning` de "fallback do Cursor". Se houver, o admin ou o plano não liberam aquele modelo.
3. A saída final tem `status: "finished"` e `spentCents`.
4. Em `/caminho/do/repo-de-teste/.workflows/worktrees/` existe a branch `wf/issue-1` com o commit.
5. Rodando de novo com `--resume <runId>`, nenhuma etapa de agente executa outra vez: todas aparecem como "(cache)".

Se algo divergir, anote em um issue do seu fork. Os pontos marcados "a validar" em
[`../00-relatorio-pesquisa.md` §8](../../00-relatorio-pesquisa.md#8-o-que-foi-refutado-e-o-que-segue-incerto)
são os candidatos mais prováveis.

## 6. Habilitar no Cursor IDE

1. Abra o repositório no Cursor.
2. Settings → MCP: o servidor `workflows` vem de `.cursor/mcp.json`. Habilite-o.
3. Confira que as skills `/run-workflow`, `/workflow-authoring` e `/skill-to-workflow` aparecem no chat ao digitar
   `/`.
4. No chat: `/run-workflow implement-issue 1`.

Para usar os workflows **em outros repositórios** sem copiar o kit para dentro deles, veja
[04 · Invocação](04-invocacao-no-cursor-ide.md#usar-o-kit-em-outros-repositórios).
