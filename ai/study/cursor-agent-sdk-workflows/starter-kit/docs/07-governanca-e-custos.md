# 07 · Governança e custos (Cursor Teams/Enterprise)

## Orçamento por usuário

| Pergunta | Resposta (nov/2026) | Confiança |
|---|---|---|
| O workflow pode rodar com a conta do próprio usuário? | Sim: `wf login` (browser) cria uma chave de usuário de 90 dias | Alta (pacote do SDK) |
| Pode reaproveitar o login da IDE sem novo login? | **Não.** O SDK não lê as credenciais da IDE nem da CLI | Alta |
| De quem é a cobrança? | "User keys bill the user; service-account keys bill the team." Aparece com a tag "SDK" no dashboard de uso | Alta (espelho da doc do SDK, marcado como confirmado) |
| O uso segue as mesmas regras de plano, pools e Privacy Mode do IDE? | Sim, segundo um resumo da página do SDK; não está no espelho local | Baixa [S]: confirmar na página ao vivo |
| Entra no **limite individual em dólares** do membro? | Provável, porque o uso é cobrado do usuário, mas a doc não fala do limite por membro | Média: valide com o admin |
| Service account debita de quem? | Do time, sem atribuição por pessoa | Alta |
| Chave Team Admin funciona? | Não | Alta |

**Como validar:** rode um workflow pequeno com a chave de um usuário de teste e confira no dashboard do time se o
gasto aparece no membro, com a tag SDK, e se o limite por membro é respeitado.

## Controles de custo no kit

Para as práticas de implementação (cache, contexto, prompts, memo), veja
[08 · Custos, cache e boas práticas](08-custos-e-cache.md). Os controles abaixo são os de governança.

1. **Teto por run:** `--max-cents`, `--max-tokens`, `WF_MAX_CENTS` ou `WF_MAX_TOKENS`. É checado antes de cada
   tentativa, e a ultrapassagem pode chegar a concorrência × custo de uma etapa (ver
   [02 §3](02-configuracao-inicial.md#3-teto-de-custo)).
2. **Modelo por etapa:** a maior parte das etapas roda em modelos baratos. Use o modelo caro só para
   planejamento difícil e review.
3. **Review condicional:** o review só roda quando o tier ou o tamanho do diff justificam.
4. **Laços com teto:** nenhum "repita até passar" sem limite.
5. **Concorrência baixa** (default 4): N agentes em paralelo custam ~N vezes os tokens.
6. **Resume:** relançar não paga de novo as etapas já concluídas.
7. **Visibilidade:** `spentCents` e `usage` (tokens por tipo e `cacheHitRatio`) no resultado; `chargedCents` e
   `usage` por etapa nos eventos.
8. **Memo entre runs:** etapas de leitura repetidas sobre o mesmo estado do repositório não custam nada.
9. **Histórico e dashboard:**
   - banco SQLite por usuário com custo bruto do Cursor, que aparece mesmo quando o uso é incluído no plano e o
     cobrado é 0;
   - custo por entrega e faixa de contexto × custo;
   - export anonimizado para consolidar no time ([09](09-observabilidade.md)).

> Uso incluído no plano reporta `chargedCents = 0`. Nesse caso, o teto em centavos não protege a franquia: use
> também `--max-tokens`.

## Segurança

| Risco | Fato | Mitigação no kit / recomendação |
|---|---|---|
| Tools sem aprovação | Runs locais do SDK executam shell, edit e write sem pedir aprovação, e as custom tools nunca pedem | Allowlist de `tools` por etapa: no exemplo, classificar e planejar só leem. Implementar e corrigir recebem todas as tools, shell incluído, porque precisam rodar testes. Em repositórios sensíveis, ligue `sandbox: true` nessas etapas (escrita só no cwd, rede só na allowlist de `.cursor/sandbox.json`; testes que baixam pacotes podem falhar) |
| Repositório não confiável | `settingSources: ["project"]` carrega regras e hooks do repositório | Para repositórios de terceiros, remova `"project"` em `engine.ts` |
| Chave em disco | `~/.cursor/sdk/auth.json` em texto puro, 90 dias | Em máquinas compartilhadas, use `CURSOR_API_KEY` vinda de um gerenciador de segredos |
| Efeitos externos | Push e PR | Feitos só pelo código, só com `openPr: true` e depois das verificações |
| Prompt injection via issue | O corpo da issue entra no prompt de classificar, planejar e implementar | Classificar e planejar não têm `shell` nem `edit`. **Implementar tem**, então um corpo de issue malicioso pode induzir comandos: use `sandbox: true`, restrinja quem pode rotular issues para o workflow e mantenha o review com lente de segurança. Revisores têm `shell` para ler o `git diff`; troque por um diff passado no prompt se quiser tirar o shell deles |
| Workflow disparando workflow | As etapas carregam o `.cursor/mcp.json` do projeto e veriam o próprio servidor `workflows` | O engine marca `WF_INSIDE_WORKFLOW=1`; dentro de uma etapa, o MCP server não expõe tools e o CLI recusa `run`/`start` |
| Vazamento da chave | `wf login` gera uma chave | O CLI imprime só e-mail e validade, nunca a chave |

## Políticas de admin que se aplicam

- **Hooks Enterprise (MDM) e Team** (dashboard): o engine carrega `team` e `mdm` por padrão
  (`settingSources: ["project","team","mdm"]`). Um deny em qualquer fonte vence ask e allow. Exemplos úteis do cookbook: auditoria em JSONL, bloqueio de prompts
  com segredos e bloqueio de modelos por origem do repositório.
- **Políticas de MCP, rede e tools do admin:** um comentário interno do SDK sugere que se aplicam às runs locais,
  mas não há doc pública afirmando isso [I]. Teste com o admin antes de contar com elas.
- **Restrições de modelo:** em runs locais, o SDK recusa um ID fora do catálogo da conta ("Cannot use this
  model"), e a etapa falha. Uma substituição feita do lado do servidor por política não é visível ao SDK. Onde o
  modelo for requisito de conformidade, garanta a configuração com o admin, porque o kit não detecta a
  substituição.
- **Privacy Mode:** segundo um resumo da doc do SDK, as runs seguem a mesma configuração do IDE [S]. Confirme
  na página oficial.
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
