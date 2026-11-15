# 08 — Referências e o que Lauren Tan considera valioso

## 1. O que ela considera valioso no desenvolvimento com agentes

Síntese das três falas ([01](01-a-palestra.md)) e do README do pstack. Cada item tem fonte nesses documentos.

1. **Confiança, não volume.** A meta é manter ou melhorar a qualidade enquanto a produtividade explode. "throughput without quality is not a goal i aspire to. if you want to go fast, go deep first."
2. **O ambiente é o trabalho.** Codebase, restrições, skills e ferramentas são "the new ingredients". "the new job of the engineer is really to spend time on the environment."
3. **Verificação acima de tudo.** É "the single most important skill"; dá ao agente "hands and eyes" e é o que faz um loop ser loop.
4. **Determinismo onde dá, julgamento onde precisa.** Extrair as partes determinísticas para código, CLI ou codemod, e deixar ao agente só o que exige julgamento.
5. **Cada correção vira estrutura.** Lint, tipo, CI ou arquitetura; prosa por último. Review humano que impõe invariante é "a code smell".
6. **O atalho deve ser o caminho certo.** "how do I make the easy thing the right thing?" / "the shortest path is the best path."
7. **Codebase limpo, porque o agente copia.** "code is memory"; "each copy makes the next copy more likely"; jardinagem contínua.
8. **Comentário e Markdown não solicitado são passivos.** Envelhecem, não são impostos e viram justificativa de atalho.
9. **Artefatos de verificação no lugar da leitura de diff.** Vídeos, screenshots, diagramas, statecharts e provas.
10. **Quem julga não escreveu.** E um finding só vale se um run o prova.
11. **Subir a curva com calma.** Começar local, observar, só depois automatizar. "don't automate a bad loop."
12. **Contexto, não controle.** Tirar-se do caminho, ensinando o agente a buscar o próprio contexto. "where am I the bottleneck?"
13. **Amostrar, não bloquear.** Review por amostragem; um padrão repetido volta para o ambiente.
14. **PRs pequenos e atômicos.** O histórico do git é contexto, e um PR pequeno é fácil de reverter.
15. **Domain expertise e linguagem.** O gargalo é expressar a intenção. Palavras certas comprimem intenção.
16. **Ferramentas próprias.** "everyone should have their own set of knives". Fork o pstack, minere seus transcripts, faça seu `-mode` com `/automate-me`.
17. **Gosto e observação.** Manter skills exige ler tool calls e thinking blocks, como um "backseat driver".

## 2. Fontes primárias

| Fonte | Tipo | Onde neste estudo |
|---|---|---|
| "All Code Is Slop (Except Mine)", AI Engineer Code Summit, 2026-11-14 — <https://youtu.be/O_zcc6Xl12g> | palestra (17min31s) | [01](01-a-palestra.md), [`sources/talk-O_zcc6Xl12g-transcript.txt`](sources/talk-O_zcc6Xl12g-transcript.txt), [`assets/talk/`](assets/talk/) (30 frames) |
| Sessão sobre confiança, verificação e pstack (~ago 2026), re-upload "SpaceX AI engineer, Lauren Tan" no canal Ai insider, 2026-09-26 — <https://www.youtube.com/watch?v=I_oMJk6barY> | palestra/Q&A (55min30s); origem não identificada | [01](01-a-palestra.md#palestra-complementar-sessão-de-55-min-sobre-confiança-verificação-e-pstack), [`sources/talk-I_oMJk6barY-transcript.txt`](sources/talk-I_oMJk6barY-transcript.txt) |
| Live com Matt Pocock, "Poteto (creator of pstack) on shipping 1,000's of PR's a month at SpaceX", 2026-10-03 — <https://www.youtube.com/live/MN9dGgmLyso> | conversa (65min36s) | [01](01-a-palestra.md#live-com-matt-pocock-poteto-creator-of-pstack-on-shipping-1000s-of-prs-a-month-at-spacex), [`sources/talk-MN9dGgmLyso-transcript.txt`](sources/talk-MN9dGgmLyso-transcript.txt) |
| pstack — <https://github.com/cursor/plugins/tree/main/pstack>, commit `bf0c7cd80abdbf7fe47b634978a7d1b4071f71a7`, v0.15.42, MIT | código e docs | [`mirror/pstack/`](mirror/pstack/), [02](02-pstack-visao-geral.md)–[05](05-catalogo-poteto-mode-playbooks.md) |
| port Claude Code gerado — `cursor/plugins/harness/pstack/claude-code` + `.claude-plugin/marketplace.json` | código | [02 §3](02-pstack-visao-geral.md#3-cursor--claude-code) (não espelhado: é cópia gerada de `pstack/`) |
| `poteto/verification-skill-example` — <https://github.com/poteto/verification-skill-example>, commit `d5abe70` | exemplo de verify skill + feature map (Atlas, fictício) | [`mirror/verification-skill-example/`](mirror/verification-skill-example/), [04](04-catalogo-skills-agentes-automacoes.md) |
| `poteto/noodle` — <https://github.com/poteto/noodle> ("Orchestrate agents using skills", Go, último push 2026-03-19) | precursor do pstack, com `brain/principles/` (16 princípios) | [01, live §1](01-a-palestra.md#live-com-matt-pocock-poteto-creator-of-pstack-on-shipping-1000s-of-prs-a-month-at-spacex) (não espelhado) |
| X: <https://x.com/poteto> · GitHub: <https://github.com/poteto> | perfis | — |

## 3. Referências que ela cita

| Referência | Contexto |
|---|---|
| Cindy Sridharan (`@copyconstruct`), tweet de 2026-11-05: "70% of my daily token spend goes into verifying patches" | slide 11:51, [frame](assets/talk/001205-cindy-verification-tweet.jpg) |
| Cindy Sridharan, taxonomia de testes (pre-production / deploy / release / post-release) | slide 12:35, [frame](assets/talk/001235-testing-taxonomy.jpg) |
| Bombadil, property-based testing de UI — <https://github.com/antithesishq/bombadil> | slide 11:35 |
| TLA+ (model checking) e Lean (provas) | slide 10:50; skills formais |
| Bend (linguagem que une programa e prova) | live com Matt, §13 |
| Andrej Karpathy, "auto research" (citado por ela ao falar de hill climbing) | live com Matt, §5. A definição original de vibe coding foi citada por Matt, não por ela |
| Bret Taylor reescrevendo o Google Maps num fim de semana | palestra 0:00 ("coding machines") |
| Garry Tan, `gstack` | origem do nome pstack |
| "context, not control" (cultura da Netflix) | live com Matt, §8 |
| Diátaxis, Google developer style, ASD-STE100, Global English | skill `technical-writing` ([04](04-catalogo-skills-agentes-automacoes.md)) |
| `cursor-team-kit` (`deslop`, `control-cli`, `control-ui`) | dependências citadas mas não incluídas no pstack (README, "not shipped here") |

## 4. Fontes secundárias (deep research)

O workflow `deep-research` rodou 5 ângulos com 101 agentes. Buscou 19 fontes, extraiu 90 claims e verificou 25 por votação adversarial 3 a 3: 23 confirmadas e 2 refutadas. O resultado bruto ficou em `_work/` durante o estudo. **Só entrou nos documentos o que foi rastreado até as falas, os slides ou o mirror.** As fontes abaixo servem para orientação, não como evidência.

| Fonte | Qualidade (rótulo do workflow) |
|---|---|
| <https://sozai.app/transcript/spacex-ai-engineer-lauren-tan-part-1/> | secondary (transcrição de terceiro) |
| <https://youtubesummary.com/summary/I_oMJk6barY> | secondary (resumo por IA) |
| <https://archive.codenewsletter.ai/2097732320606507506> | arquivo de um artigo de X dela (guia do pstack, parte 2) |
| <https://maven.com/p/e23d9c/how-cursor-turned-ai-agents-into-better-engineers> | secondary, promocional |
| <https://github.com/backnotprop/pstack> | mirror de terceiro |
| <https://flaviocopes.com/pstack> · <https://alexop.dev/posts/learning-from-pstack/> · <https://redreamality.com/blog/lauren-tan-poteto-trust-before-parallel/> · <https://redreamality.com/garden/notes/pstack-skills-guide/> | blogs |
| <https://aiidelist.com/de/blog/lauren-tan-grok-bot-pstack-workflow> · <https://youmind.com/landing/x-viral-articles/pstack-guide-ai-verification-skills> · <https://youmind.com/landing/x-viral-articles/how-i-use-cursor-pstack> · <https://thenewstack.io/agentic-verification-distributed-systems> | secondary |
| <https://www.theneuron.ai/explainer-articles/pstack-explained-lauren-tans-system-for-trustworthy-ai-agents/> | marcada como unreliable, sem claims usadas |

**Refutadas 0–3 e excluídas:**

- "o `/architect` tem cinco fases (ground, sketch, cross-judge, implement, scrap)". O arquivo real está em [04](04-catalogo-skills-agentes-automacoes.md).
- "a palestra enquadra a adoção como uma 'agent trust curve'". Isso vem da página da Maven. Nota: a palestra de agosto usa sim um gráfico de "trust curve" ([01](01-a-palestra.md#palestra-complementar-sessão-de-55-min-sobre-confiança-verificação-e-pstack) §1). O que foi refutado é a atribuição dessa frase à palestra de novembro.

**Divergências entre fontes:**

- **Afiliação.** Na live de outubro, "Cursor which is now SpaceX AI". Em novembro, "Principal Engineer, SpaceX/SpaceXSI". A Maven (ago) diz "Member of Technical Staff at Cursor".
- **Volume.** Ela fala em 2.500 PRs/mês num talk anterior citado por Matt, e em 3.000 no slide de novembro.

## 5. Contexto local usado

- `/run-spec`: `ai/skills/run-spec/` em `feat/run-spec-aaa@8f79b33`; estudo anterior [`../run-spec-review-axes/`](../run-spec-review-axes/README.md).
- `software-factory`: `~/Workspace/software-factory@1dffd43` (spec #38, ADRs 0002, 0007, 0009, 0010, 0016, 0017, 0023, 0026, 0027, 0029, 0034).
- Docs dos harnesses: `ai/docs/claude-code/` (marketplace e plugins, skills) e `ai/docs/cursor/` (plugins, skills e Custom Mode).
