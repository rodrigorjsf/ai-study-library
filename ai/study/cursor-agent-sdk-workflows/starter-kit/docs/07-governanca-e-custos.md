# 07 · Governança e custos (Cursor Teams/Enterprise)

## Orçamento por usuário

| Pergunta | Resposta (nov/2026) | Confiança |
|---|---|---|
| O workflow pode rodar com a conta do próprio usuário? | Sim: `wf login` (browser) cria uma chave de usuário de 90 dias | Alta (pacote do SDK) |
| Pode reaproveitar o login da IDE sem novo login? | **Não.** O SDK não lê as credenciais da IDE nem da CLI | Alta |
| O uso entra no mesmo plano e nos mesmos pools do IDE? | Sim, segundo a doc do SDK: mesmas regras de plano, pools e Privacy Mode; aparece com a tag "SDK" no dashboard | Média (espelho da doc) |
| Entra no **limite individual em dólares** do membro? | Provável, porque a chave é do usuário, mas **não confirmado** | Baixa: valide com o admin |
| Service account debita de quem? | Do pool do time, sem atribuição por pessoa | Média |
| Chave Team Admin funciona? | Não | Alta |

**Como validar:** rode um workflow pequeno com a chave de um usuário de teste e confira no dashboard do time se o
gasto aparece no membro, com a tag SDK, e se o limite por membro é respeitado.

## Controles de custo no kit

1. **Teto por run:** `--max-cents`, `--max-tokens` ou `WF_MAX_CENTS`. É checado antes de cada etapa.
2. **Modelo por etapa:** a maior parte das etapas roda em modelos baratos. Use o modelo caro só para
   planejamento difícil e review.
3. **Review condicional:** o review só roda quando o tier ou o tamanho do diff justificam.
4. **Laços com teto:** nenhum "repita até passar" sem limite.
5. **Concorrência baixa** (default 4): N agentes em paralelo custam ~N vezes os tokens.
6. **Resume:** relançar não paga de novo as etapas já concluídas.
7. **Visibilidade:** `spentCents` no resultado e `chargedCents` por etapa nos eventos.

> Uso incluído no plano reporta `chargedCents = 0`. Nesse caso, o teto em centavos não protege a franquia: use
> também `--max-tokens`.

## Segurança

| Risco | Fato | Mitigação no kit / recomendação |
|---|---|---|
| Tools sem aprovação | Runs locais do SDK executam shell, edit e write sem pedir aprovação, e as custom tools nunca pedem | Allowlist de `tools` por etapa (etapas de leitura não recebem `edit`/`shell`). Use `sandboxOptions: { enabled: true }` no engine em repositórios sensíveis (restringe escrita ao cwd e rede à allowlist) |
| Repositório não confiável | `settingSources: ["project"]` carrega regras e hooks do repositório | Para repositórios de terceiros, remova `"project"` em `engine.ts` |
| Chave em disco | `~/.cursor/sdk/auth.json` em texto puro, 90 dias | Em máquinas compartilhadas, use `CURSOR_API_KEY` vinda de um gerenciador de segredos |
| Efeitos externos | Push e PR | Feitos só pelo código, só com `openPr: true` e depois das verificações |
| Prompt injection via issue | O corpo da issue entra no prompt | Etapas que leem a issue não recebem `shell`; review com lente de segurança em tier HIGH |

## Políticas de admin que se aplicam

- **Hooks Enterprise (MDM) e Team** (dashboard): carregados por quem usa `settingSources` com `team`/`mdm`. Um
  deny em qualquer fonte vence ask e allow. Exemplos úteis do cookbook: auditoria em JSONL, bloqueio de prompts
  com segredos e bloqueio de modelos por origem do repositório.
- **Políticas de MCP, rede e tools do admin** e a *Cloud Agent Allowlist* valem nas runs locais do SDK.
- **Restrições de modelo:** o Cursor pode cair em outro modelo em silêncio. Use `strictModel: true` onde o
  modelo for requisito de conformidade.
- **Privacy Mode:** as runs do SDK seguem as mesmas configurações do IDE (segundo a doc).
- **Self-hosted** (pools, My Machines): checkout e execução na sua infraestrutura, mas orquestração e inferência
  continuam na Cursor. Não há residência de dados completa.

## Checklist de adoção no time

- [ ] Admin confirma a atribuição de custo por membro para chaves de usuário do SDK.
- [ ] Admin libera os modelos do mapa de tiers, e eles aparecem em `npm run models` para um membro comum.
- [ ] Teto padrão `WF_MAX_CENTS` definido no `mcp.json` do kit.
- [ ] Hook de auditoria (`beforeMCPExecution` em `start_workflow`) ativo, se o time exigir.
- [ ] `sandboxOptions` ligado para repositórios sensíveis.
- [ ] Service account criada para uso em CI.
- [ ] Teste de fumaça ([01 §5](01-instalacao.md#5-teste-de-fumaça-real)) executado com sucesso.
