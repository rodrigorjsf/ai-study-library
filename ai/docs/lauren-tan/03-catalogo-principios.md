# Catálogo dos princípios do `pstack`

Catálogo dos princípios de engenharia que Lauren Tan (poteto) publica no plugin `pstack`. Fonte: espelho verbatim de `github.com/cursor/plugins` no commit `bf0c7cd8` (MIT), em `mirror/pstack/`. Todos os caminhos citados são relativos a este diretório de estudo (`ai/docs/lauren-tan/`).

**Contagem.** O `pstack` traz **24** princípios, não 23. Há 24 diretórios `mirror/pstack/skills/principle-*/`. O guia confirma: "pstack ships 24 principles as individual skills" (`mirror/pstack/docs/guide/08-principles.md`, linha 3). O README também diz "twenty-four short skills, one principle each" (`mirror/pstack/README.md`, linha 225). Este catálogo cobre os 24.

## O que é uma skill de princípio

Cada princípio é uma skill curta em `skills/principle-<nome>/SKILL.md`, com uma regra só. O frontmatter de todas as 24 traz `disable-model-invocation: true`. Logo, nenhum princípio é carregado pelo modelo por conta própria a partir da `description`.

- **Claude Code.** `disable-model-invocation: true` impede que o Claude carregue a skill automaticamente. Também impede o preload da skill em subagentes (`ai/docs/claude-code/skills/extend-claude-with-skills.md`, linha 405).
- **Cursor.** Com o campo em `true`, a skill entra no contexto só quando o usuário digita `/skill-name`. O agente não a aplica sozinho pelo contexto (`ai/docs/cursor/skills/agent-skills-guide.md`, linhas 177 e 218).

**Como os princípios chegam ao agente.** O caminho é o `poteto-mode` (`mirror/pstack/skills/poteto-mode/SKILL.md`), não o mecanismo de skills do harness:

1. O `poteto-mode` tem uma seção `## Principles` com um índice inline. O índice agrupa os princípios em **Core**, **Architecture**, **Verification**, **Delegation** e **Meta**. Cada entrada diz quando o princípio se aplica, em uma ou duas frases.
2. Essa seção instrui: "Read the leaf skill in full for any principle you apply." A folha é o arquivo `principle-<title>`, com o título em kebab case.
3. Os "Non-negotiables" exigem: "In your reply, name each principle that shaped a decision and the specific choice it changed. Cite only principles whose leaf SKILL.md you read this session."
4. O guia completa: "A principle citation with no decision behind it means the agent named the rule without applying it." (`08-principles.md`, linha 27).
5. Subagentes delegados usam `subagent_type: "poteto-agent"`. Esse agente lê o `poteto-mode` inteiro, incluindo o índice de princípios, antes de qualquer trabalho. O README avisa que trocar por `generalPurpose` "skips that read and drifts" (`README.md`, linha 217).

**Como o humano usa os princípios.** Ele não os invoca. Ele cita o nome para corrigir o rumo do agente: "You don't invoke principles. You use their names to steer." Um exemplo do guia: "apply prove it works. run the real import flow and show me the written records." (`08-principles.md`, linhas 5 e 18).

**Diferença em relação aos playbooks.** Um playbook é um procedimento por tipo de tarefa (Bug fix, Feature, Refactoring, Babysit e outros). Fica em `skills/poteto-mode/playbooks/<title>.md`. O `poteto-mode` casa a tarefa com um playbook (o playbook "Opening a PR" é invocado ao fim de todos os outros) e copia os passos dele, verbatim, para o início de uma todolist. Um princípio não tem passos. É uma regra de decisão que vale em qualquer playbook, disparada por uma situação ("Debugging", "After a task, before declaring done"). O agente a cita na resposta junto da decisão que ela mudou. Este catálogo não leu os arquivos de playbook e não descreve o conteúdo deles.

**Instalação nos dois harnesses** (`README.md`, linhas 17-30):

- No Cursor: `/add-plugin pstack`. O comando de entrada é `/poteto-mode`.
- No Claude Code: `/plugin marketplace add cursor/plugins`, depois `/plugin install pstack@cursor-plugins`. Os comandos ganham prefixo, então o modo vira `/pstack:poteto-mode`. Um passo que depende de recurso exclusivo do Cursor (bugbot, automations) "is skipped with a one-line note".
- Os princípios em si são Markdown puro e não dependem de harness. A diferença está só em como chegam ao contexto. Nos dois harnesses chegam pela leitura que o `poteto-mode` ou o `poteto-agent` faz da folha.

**Nota sobre o tamanho das folhas.** Em seis princípios o corpo do `SKILL.md` não repete a regra principal. A regra fica na `description` do frontmatter, e o corpo só traz complementos: `exhaust-the-design-space`, `encode-lessons-in-structure`, `guard-the-context-window`, `laziness-protocol`, `migrate-callers-then-delete-legacy-apis` e, em parte, `type-system-discipline`. As seis folhas foram comparadas, byte a byte, com o `main` upstream (`gh api repos/cursor/plugins/contents/pstack/skills/...`, 2026-11-15). As seis são idênticas ao espelho, então o espelho não está truncado. A comparação foi feita contra `main` porque a API do GitHub não resolveu o SHA curto `bf0c7cd8` ("No commit found for SHA", HTTP 422). Nesses casos, as seções abaixo tiram a regra da `description`, do índice do `poteto-mode` e do guia, e dizem isso.

**Escopo da linha de relevância.** Cada seção termina com "Relevância para validação de fluxo agêntico". A linha avalia se o princípio ajuda a verificar a saída de um agente: provar que o trabalho funciona, detectar resultado falso ou deixar a verificação reexecutável.

---

## principle-laziness-protocol

Fonte: `mirror/pstack/skills/principle-laziness-protocol/SKILL.md`

**Regra.** Preferir apagar código e fazer a menor mudança que resolve o problema. A `description` diz: "Bias toward deletion and the smallest change that solves the problem." Aplica-se ao refatorar, ao avaliar o tamanho de um diff ou quando surge a vontade de adicionar abstrações, camadas ou "signal threading".

**O que manda fazer.** O corpo tem só dois itens:
- "Consolidate decisions." Não repetir a mesma escolha em vários lugares. Pôr a escolha atrás de uma fonte única de verdade e passar o resultado como uma flag simples.
- "Minimize the diff." Fazer a menor mudança que resolve. "Fewer lines beat "elegant" boilerplate."

A regra de preferir deletar está na `description` e no índice do `poteto-mode`, não no corpo. Outros princípios citam este para reforçar o mínimo: `build-the-lever` ("build the smallest script that does or proves the job, never a framework") e `attack-the-premise` ("Remove the condition instead of compensating for it").

**Relevância para validação de fluxo agêntico:** baixa. Diffs menores ficam mais fáceis de revisar, mas o princípio não diz como verificar nada.

## principle-foundational-thinking

Fonte: `mirror/pstack/skills/principle-foundational-thinking/SKILL.md`

**Regra.** Escolher as estruturas de dados certas antes de escrever lógica, para que o código seguinte fique óbvio. "**Structural decisions** protect option value. **Code-level decisions** protect simplicity."

**O que manda fazer.**
- "Data structures first." Definir os tipos centrais cedo, rastrear cada padrão de acesso e escolher estruturas que sirvam aos caminhos dominantes.
- No nível do código: "DRY the structure, not every line." "Three similar statements still beat a premature abstraction." Preferir explícito a esperto.
- Corolário de concorrência. Antes de compartilhar estado entre atores, perguntar "what happens if another actor modifies this concurrently?" Se a resposta não for "nothing", isolar.
- "Scaffold first." Teste: "does every subsequent phase benefit from this existing?" CI, lint, infraestrutura de teste e tipos compartilhados são scaffold. Ordem: setup antes de features, testes antes de correções. Commits pequenos e com um só propósito.
- Cada incremento entrega uma abstração coerente ou aprofunda uma que já existe. Não espalhar uma capacidade nova pelos chamadores como coordenação de caso especial.
- "Subtraction comes before scaffolding." Remover código morto primeiro.

**Relevância para validação de fluxo agêntico:** baixa a média. A frase "tests before fixes" e a ordem de scaffold deixam a validação disponível cedo. O resto é design.

## principle-redesign-from-first-principles

Fonte: `mirror/pstack/skills/principle-redesign-from-first-principles/SKILL.md`

**Regra.** Ao integrar um requisito novo, não acoplá-lo ao design atual. Redesenhar "as if the requirement had been a foundational assumption from the start."

**O que manda fazer.**
- Ler todos os arquivos afetados e entender o design atual.
- Perguntar: "if we were writing this from scratch with this new requirement, what would we build?"
- Propagar a mudança por todas as referências: tipos, docs, exemplos, seções de justificativa.
- Pensar o redesign inteiro e entregá-lo de forma incremental.

É "the method for preserving option value". O `attack-the-premise` se distingue deste: este reconstrói o design em torno de um requisito novo, aquele questiona um fato que o design atual assume.

**Relevância para validação de fluxo agêntico:** baixa.

## principle-attack-the-premise

Fonte: `mirror/pstack/skills/principle-attack-the-premise/SKILL.md`

**Regra.** Quando duas ou mais correções com a mesma premissa falharam no mesmo gate, suspeitar da premissa, não das correções. Motivo: "Each failed fix is evidence against the belief it assumed."

**O que manda fazer.**
- "Write the premise down." É a frase que toda correção que falhou assumia.
- "Test the premise before the next fix." Achar uma observação que daria resultado diferente se a premissa fosse falsa, e fazê-la. Olhar como as falhas se distribuem, não só o tamanho delas. Deixar o teste reexecutável (via `build-the-lever`).
- "Follow the evidence." Se a evidência contradiz a premissa, a causa está em outro lugar. Se a confirma, perguntar o próximo "why" (via `fix-root-causes`).
- "Remove the condition instead of compensating for it." Um mecanismo que limpa depois do problema deixa a causa no lugar.

**Gate de parada:** "Do not start the next fix before the premise is written down and tested."

**Relevância para validação de fluxo agêntico:** alta. O princípio dá um critério objetivo para parar um agente que gira em correções que falham: duas falhas com a mesma premissa. Também exige um teste reexecutável da premissa antes de qualquer nova tentativa.

## principle-subtract-before-you-add

Fonte: `mirror/pstack/skills/principle-subtract-before-you-add/SKILL.md`

**Regra.** Ao evoluir um sistema, remover complexidade primeiro e depois construir. "Default to subtraction." Deixar o design "slightly simpler and more capable behind the same or smaller surface than you found it."

**O que manda fazer.**
- Pôr a remoção antes da construção.
- "Cut before you polish." Chegar ao mínimo antes de investir em qualidade.
- Projetar para o uso observado, não para casos de borda especulativos.
- "No speculative validators, parsers, or guards beyond what the spec demands."
- Simplificar prompts: remover instruções redundantes e templates excessivos.
- Quando uma referência não tem conteúdo novo, apagá-la em vez de deixar um stub.

**Relevância para validação de fluxo agêntico:** baixa.

## principle-minimize-reader-load

Fonte: `mirror/pstack/skills/principle-minimize-reader-load/SKILL.md`

**Regra.** Manutenibilidade é o trabalho que um leitor tem para entender o código. O princípio mede dois eixos independentes: "**layers to trace**" e "**state to hold**". LOC, complexidade ciclomática e "clean architecture" são só proxies. O texto se apresenta como o análogo humano de `guard-the-context-window`.

**O que manda fazer.**
- Colapsar camadas que custam mais do que poupam: wrappers com um só chamador, adapters sem segunda implementação, indireção especulativa.
- Cada camada adjacente deve mudar a abstração. Camadas pass-through são colapsadas.
- "Demand interface compression." Preferir fronteiras que escondem decisões relevantes.
- Reduzir o escopo do estado: funções puras, depois locais, depois campos, depois estado de módulo, depois globais. "Derive instead of sync."
- Nomear o invariante na fronteira, não em cada consumidor.
- Antes de adicionar camada ou estado, perguntar se isso reduz a carga do leitor em outro lugar na mesma medida.

**Teste:** um leitor novo responde "where does X come from?" e "what can change X?" em menos de 30 segundos?

**Relevância para validação de fluxo agêntico:** baixa. O teste dos 30 segundos serve para revisar código, não para verificar a saída de um agente.

## principle-outcome-oriented-execution

Fonte: `mirror/pstack/skills/principle-outcome-oriented-execution/SKILL.md`

**Regra.** Otimizar para o estado final pretendido e verificável, não para estados intermediários estáveis. Manter cada passo estável "often creates temporary compatibility code that becomes long-lived debt."

**O que manda fazer.**
- "Prioritize end-state integrity over transitional stability."
- Quebra intermediária é aceitável quando é "planned, scoped, and reversible".
- Guardrails: usar só em reescritas e migrações planejadas com fronteiras de fase explícitas. Declarar onde a quebra temporária é aceitável. Manter checks de alto sinal nas áreas tocadas durante a migração. "Require full static and runtime verification at plan completion."

**Relevância para validação de fluxo agêntico:** média. O princípio põe a verificação completa, estática e em runtime, num ponto declarado: o fim do plano. Durante a migração, exige checks de alto sinal nas áreas tocadas. Não diz como verificar.

## principle-experience-first

Fonte: `mirror/pstack/skills/principle-experience-first/SKILL.md`

**Regra.** "When implementation convenience conflicts with user delight, choose delight."

**O que manda fazer.**
- Justificar cada feature, controle e opção.
- "Ship less, ship better": três features polidas valem mais que dez cruas.
- Prototipar antes de se comprometer. Decisões de design são mais baratas em HTML descartável.
- Acertar os detalhes: transições, alinhamento, espaçamento, feedback, estados de erro.
- Enxugar o loop central.

O "usuário" é quem consome o trabalho. Pode ser o usuário final, o colega que importa a biblioteca ou o engenheiro que vai manter o código. Sobre a relação com `foundational-thinking`: "Foundational thinking governs the *sequence* of work. This principle governs the *target*."

**Relevância para validação de fluxo agêntico:** baixa.

## principle-exhaust-the-design-space

Fonte: `mirror/pstack/skills/principle-exhaust-the-design-space/SKILL.md`

**Regra** (da `description`). Diante de uma interação de UI nova ou de uma decisão arquitetural sem precedente no codebase: "Build 2-3 competing prototypes and compare side by side before committing."

**O que manda fazer.** O corpo tem uma frase só, que estende o escopo: "It also applies to product design decisions where user experience depends on feel, not logic." O guia resume o princípio como "builds two or three competing prototypes when there's no precedent." Não há checklist nem exemplo.

**Relevância para validação de fluxo agêntico:** baixa. Comparar protótipos lado a lado é escolha de design, não verificação de saída.

## principle-build-the-lever

Fonte: `mirror/pstack/skills/principle-build-the-lever/SKILL.md`

**Regra.** Quando o trabalho não é trivial, construir a ferramenta que o faz ou que o prova, em vez de fazê-lo à mão. "A deterministic script turns "trust me" into "run this"." O limite é a trivialidade, não a repetição.

**O que manda fazer.**
- Fazer a primeira unidade à mão para aprender a receita, depois construir a ferramenta. Provar a ferramenta rodando-a nessa mesma unidade e comparando o diff com a versão manual. A ferramenta deve ser segura de reexecutar.
- Codemod ou script para edições, gerador para arquivos repetitivos, consulta dump-to-sqlite para análise, "a rerunnable check for verification".
- "A deterministic lever beats fan-out." Não espalhar delegados para aplicar à mão o que um script faz.
- Ao delegar a subagentes, escrever a ferramenta como uma skill que todos leem: receita, contrato de verificação e cercas de "do-not-touch". A skill fica fora do escopo de escrita dos delegados, para que não alterem o contrato.
- Teste de aplicação: "If you cited it and there is no codemod, script, generator, or delegate skill in the diff, you didn't apply it."
- Commitar a ferramenta quando o trabalho dura além da sessão.

**Relevância para validação de fluxo agêntico:** alta. O princípio transforma a verificação num artefato reexecutável por um revisor. Exige que o contrato de verificação dos delegados fique fora do alcance deles. E dá um critério para checar se foi aplicado de fato: existe um arquivo-ferramenta no diff.

## principle-model-the-domain

Fonte: `mirror/pstack/skills/principle-model-the-domain/SKILL.md`

**Regra.** Codificar o domínio real numa estrutura de dados em vez de espalhá-lo em condicionais. Uma estrutura fiel ao domínio "makes invalid states unrepresentable and deletes branches."

**O que manda fazer.** Usar, conforme o caso:
- uma máquina de estados em vez de booleanos e checagens de fase espalhados;
- um modelo tipado em vez de parâmetros soltos;
- map, registry, tabela de lookup ou união discriminada em vez de branches espalhados por arquivos;
- um reducer ou modelo de comando/evento;
- um módulo organizado em torno de um corpo de conhecimento do domínio, não de uma sequência load/validate/transform/save ("Execution order is not ownership");
- fila, cache, índice, grafo ou árvore quando o padrão de acesso pede.

Não forçar abstração: "Prefer boring code if the current shape is already clear, local, and unlikely to grow."

**Sinais de que o princípio foi pulado:** uma feature nova que acrescenta mais um branch a uma cadeia if/else; um segundo booleano que precisa ficar em sincronia com o primeiro; módulos com nome de fase que repetem as mesmas regras do domínio.

No `poteto-mode`, "Any code" dispara este princípio: "name the data shape first".

**Relevância para validação de fluxo agêntico:** baixa. Os "sinais" servem para revisar código, não para verificar resultado.

## principle-boundary-discipline

Fonte: `mirror/pstack/skills/principle-boundary-discipline/SKILL.md`

**Regra.** Pôr validação, estreitamento de tipo e tratamento de erro nas fronteiras do sistema. O código interno é confiável sem condição. A lógica de negócio fica em funções puras. "The shell is thin and mechanical."

**O que manda fazer.**
- Nas fronteiras (args de CLI, arquivos de config, APIs externas, protocolos de rede): validar, retornar erros, agir de forma defensiva.
- Dentro do sistema: dados tipados, propagação de erro, sem revalidação.
- Através da fronteira: expor conceitos do domínio, não a representação privada da fronteira. Não reexportar tipos de transporte, storage, framework ou wire pela superfície pública.
- Lógica de negócio, parsing, construção de prompt ("structured state in, string out") e scoring como transformações puras.

**Testes:** "Is this data crossing a system boundary right now?" Se não está, validar ali é redundante. "Can this be a pure function that the shell just calls?" Se pode, extrair.

**Relevância para validação de fluxo agêntico:** baixa a média. O princípio deixa a lógica testável sem o framework, mas não verifica nada por conta própria.

## principle-type-system-discipline

Fonte: `mirror/pstack/skills/principle-type-system-discipline/SKILL.md`

**Regra.** Fazer o compilador rejeitar estados impossíveis, primitivos trocados e variantes não tratadas. "Prefer defining errors and special cases out of existence over proliferating handlers." Para sintaxe TypeScript, aponta para a skill `typescript-best-practices`.

**O que manda fazer.**
- "Brand semantic primitives." `UserId` e `OrderId` não podem ser intercambiáveis. Validar uma vez na criação e confiar no tipo depois.
- "External data is untyped until parsed." Isso vale para payloads de RPC, JSON, IPC, args de CLI, config, variáveis de ambiente e linhas de banco. Ter uma função de parse em cada fronteira.
- "Derive types from authoritative schemas": protobuf, OpenAPI, GraphQL, migrations, arquivo de design tokens.

A `description` também promete "exhaust variants", mas o corpo não tem um item próprio para isso.

**Relevância para validação de fluxo agêntico:** baixa a média. A verificação estática pelo compilador é uma forma de checagem automática, mas o princípio trata de design de tipos.

## principle-make-operations-idempotent

Fonte: `mirror/pstack/skills/principle-make-operations-idempotent/SKILL.md`

**Regra.** Uma operação deve convergir ao estado correto independentemente de quantas vezes roda ou de onde a execução anterior parou. Toda operação que muda estado responde: "What happens if this runs twice? What happens if the previous run crashed halfway?"

**O que manda fazer.**
- Derivar cada passo do estado que existe, não do que a execução anterior pretendia fazer. Ler o estado atual, comparar com o objetivo e aplicar só a diferença.
- O que uma execução deixa para trás (lock, arquivo temporário, registro pela metade, job reivindicado) precisa ser reconhecível como obsoleto na execução seguinte. A evidência de obsolescência deve valer em qualquer ponto de parada. Exemplos: escrever num caminho temporário e renomear para o lugar; comparar artefatos por conteúdo, não por ordem de criação.

**Teste em três perguntas:** (1) roda duas vezes seguidas? (2) a execução anterior quebrou em cada ponto possível? (3) a reexecução converge ao mesmo estado final? Se alguma resposta for "it depends on what state was left behind", falta um passo de reconciliação.

**Relevância para validação de fluxo agêntico:** média. O teste de três perguntas serve para verificar loops e etapas de agente que rodam com crash, restart e retry. Também vale para os próprios scripts de verificação, que `build-the-lever` quer seguros de reexecutar.

## principle-migrate-callers-then-delete-legacy-apis

Fonte: `mirror/pstack/skills/principle-migrate-callers-then-delete-legacy-apis/SKILL.md`

**Regra** (da `description`). Ao introduzir uma API interna nova enquanto chamadores antigos existem: "Migrate callers and delete the old API in the same wave instead of preserving compatibility layers."

**O que manda fazer.** O corpo começa direto num bullet: "Update tests to assert the new contract, and delete tests that only protect pre-refactor implementation details." Em seguida lista quando o princípio se aplica:
- nenhum usuário externo depende de compatibilidade retroativa;
- o projeto absorve breaking changes coordenadas;
- a API nova faz parte de uma iniciativa de simplificação ou refatoração.

**Relevância para validação de fluxo agêntico:** baixa. O único ponto de contato é reescrever os testes para o contrato novo, o que se liga a `test-behavior-not-implementation`.

## principle-separate-before-serializing-shared-state

Fonte: `mirror/pstack/skills/principle-separate-before-serializing-shared-state/SKILL.md`

**Regra.** Quando atores concorrentes podem compartilhar estado mutável, primeiro perguntar se precisam do mesmo objeto. Se não precisam, eliminar o compartilhamento. Se o compartilhamento é real, serializar de forma estrutural. "Instructions and conventions are not concurrency control."

**O que manda fazer.**
1. Identificar o estado mutável compartilhado: arquivos lidos e escritos por ambos, branches onde ambos dão push, APIs que ambos definem e consomem.
2. Padrão: eliminar o alvo de escrita compartilhado. Dar a cada ator o próprio arquivo, chave, branch ou diretório, e juntar só na fronteira de leitura. Exemplo do texto: dois workers escrevendo `lastX` em um `state.json` ainda é mutação compartilhada. `indexer-state.json` + `metrics-state.json` não é.
3. Só quando um alvo único é um invariante real, usar lockfile, fases sequenciais, ator escritor único ou compare-and-swap atômico. "Treat "we need a lock" as a design smell to check, not as the default answer."

O guia dá o exemplo para fan-out de agentes: "give each attempt its own worktree, no locks."

**Relevância para validação de fluxo agêntico:** média. O princípio não verifica saída. Ele previne uma classe de falha intermitente em execuções paralelas de agentes (worktree por tentativa), e essa falha é difícil de detectar numa validação posterior.

## principle-prove-it-works

Fonte: `mirror/pstack/skills/principle-prove-it-works/SKILL.md`

**Regra.** Verificar cada saída checando a coisa real diretamente. "Do not infer from proxies, self-reports, or "it compiles."" Motivo: "Acting on a wrong inference costs far more than checking the source."

**O que manda fazer.**
- Evitar verificação indireta: mtimes de arquivo, frescor de output, "agent self-reports", screenshots em cache.
- Checar a vivacidade de um processo diretamente, não por estado derivado.
- Ler o valor real, não uma representação em cache ou derivada.
- "When verification fails, suspect the observation method before suspecting the system."
- "Script the check when you can." A prova mais forte é um script determinístico que refaz a mesma comparação. Guardar o output como artefato que um revisor reexecuta.
- Manter o artefato visível para o humano. Commitá-lo só em trabalho grande ou complexo, em que a trilha precisa ser auditável depois (skill `show-me-your-work`).

No `poteto-mode` o gatilho é "After a task, before declaring done." Exemplo de uso pelo humano, do guia: "apply prove it works. run the real import flow and show me the written records."

**Relevância para validação de fluxo agêntico:** máxima. É o princípio central de verificação. Ele recusa o autorrelato do agente e o "compila" como prova, exige observar o artefato real e prefere um check scriptado e reexecutável. Também manda suspeitar primeiro do método de observação quando a verificação falha.

## principle-fix-root-causes

Fonte: `mirror/pstack/skills/principle-fix-root-causes/SKILL.md`

**Regra.** Ao depurar, corrigir a falha, não o lugar onde ela apareceu. "The symptom is where a wrong state became visible. The root cause is the first place the system did something it should not do."

**O que manda fazer.**
- "Reproduce first."
- Perguntar "why" a cada passo até chegar a uma decisão errada no código.
- Quando travar, instrumentar. "Read the actual error and the actual state. Do not guess."
- Perguntar se o estado que disparou o sintoma é legítimo. Se é, tratá-lo onde quebrou é a correção. Se não deveria existir, um check ali esconde o bug. Os meios usuais de esconder bugs são "Guards, retries, swallowed errors, clamped values, and discarded state".
- Falha só depois de restart: suspeitar primeiro de estado persistido (config, cache, lock files, estado serializado).
- Procurar o padrão, não só a instância. Corrigir todos os lugares com a mesma falha.
- Um workaround que precisa de comentário longo para se justificar indica código errado.
- Se o fato decisivo exigiu uma escavação funda, propor "the cheap, always-on signal that would have shown it at first look."

**Relevância para validação de fluxo agêntico:** alta. "Reproduce first" e "Do not guess" exigem evidência em runtime antes de mudar código. A lista de formas de esconder bugs serve de checklist para revisar correções feitas por agentes. E o último item converte cada investigação difícil num sinal de observabilidade permanente.

## principle-sequence-verifiable-units

Fonte: `mirror/pstack/skills/principle-sequence-verifiable-units/SKILL.md`

**Regra.** Ordenar o trabalho como uma sequência de unidades pequenas, cada uma terminando num estado checável. "don't advance until the current one is green." O `poteto-mode` o chama de **Sequence Work into Verifiable Units**.

**O que manda fazer.**
- Execução. Em sweeps, migrações ou séries de edições parecidas, verificar cada mudança antes da próxima. Cada unidade é um "before/after bracket": estado conhecido bom, uma mudança, rodar o check, prosseguir. Fazer rebase sobre trunk limpo antes, para que cada check meça contra a baseline real. Com um lever fazendo as edições, o check por unidade quase não custa: "Run it anyway."
- Entrega. Empilhar commits e PRs na ordem que prova o trabalho. A forma canônica é "the failing test first, then the fix on top". Outras ordens: subtração antes da remodelagem, captura de baseline antes do tratamento, scaffold antes da feature. "the sequence reads as an argument."

Motivo: "A break caught at the unit that caused it is cheap to localize." A entrega reexecutável muda "trust me" para "watch it go red, then green."

**Relevância para validação de fluxo agêntico:** alta. O princípio define a granularidade da verificação (um check por unidade, antes de avançar) e a ancora numa baseline real. Também torna o histórico de commits uma prova que um revisor reexecuta, do vermelho ao verde.

## principle-test-behavior-not-implementation

Fonte: `mirror/pstack/skills/principle-test-behavior-not-implementation/SKILL.md`

**Regra.** Um teste é uma afirmação sobre o que o código faz para seus usuários. Comportamento é o que eles observam pela interface: valores de retorno, erros, estado que leem de volta, efeitos externos ("a request sent, a row written, or a message emitted"). Implementação é o que não observam.

**Heurística das duas edições imaginárias.**
- "Break the behavior." Fazer o código retornar valor errado, pular um efeito ou repeti-lo. Se o teste ainda passa, "it proves nothing". Causas usuais: asserção mais frouxa que o contrato; valor esperado calculado pelo próprio código sob teste; constante ou string de prompt repetida que nunca executa o código que a lê; asserção sobre dados que o próprio teste montou.
- "Change the internals." Manter os resultados observáveis e reestruturar por baixo. Se o teste falha, está preso à implementação.

Manter o teste que pega a primeira edição e sobrevive à segunda. Para escrevê-lo: dirigir o código pela interface dos usuários com entrada concreta, e "Derive the expected value from the requirement, not from a run of the code."

**Casos limite do texto.** "an empty cart never charges": asserir que o cliente de pagamento não recebeu chamada é comportamento, desde que haja um caso pareado em que a cobrança ocorre. O payload recebido por um serviço externo mockado é comportamento. Uma chamada a helper interno não é. Uma mensagem de erro exata fixa texto que nenhum chamador lê. O tipo de erro em que os chamadores ramificam é o contrato. Um invariante (chave presente em duas tabelas, checagem de tipo em compilação) também conta como comportamento.

**Relevância para validação de fluxo agêntico:** alta. O teste da "edição que quebra o comportamento" detecta testes ocos, um modo de falha típico de testes escritos por agentes: valor esperado tirado de uma execução do próprio código, asserção sobre dado montado pelo próprio teste, string de prompt repetida sem executar quem a lê.

## principle-explain-the-number

Fonte: `mirror/pstack/skills/principle-explain-the-number/SKILL.md`

**Regra.** Antes de medir, e antes de confiar num número medido, relatá-lo ou agir sobre ele (speedup, regressão, throughput, latência, resultado de eval): achar o que o limita e descartar que ele mediu outra coisa. O texto o distingue de `prove-it-works`, "which checks that an output is real".

**O que manda fazer.**
- "Write the decision before you run." Nomear o resultado que mudaria uma decisão e o piso de ruído. Parar quando a dispersão entre execuções for maior que o efeito.
- "Ask "why not double?"" Nomear o recurso ou caminho de código que limita o resultado: core, lock, disco, rede ou o próprio gerador de carga. Obtê-lo de um profile ou de contadores do sistema durante a execução. "A guess from reading the code is not a limiter."
- Listar o que mais o número poderia medir e descartar cada hipótese com evidência. Suspeitos usuais: erros, trabalho pulado ou em cache, código que nunca rodou, um lado não ajustado, ruído, uma parte pequena demais para importar no total.
- "Keep the evidence with the number": número de execuções, dispersão e limitador.

Para performance, rodar a skill `benchmark-checklist`. Para eval: "did every run do the task, does the gap hold across trials and models, and does the scenario matter."

**Sinais de que foi pulado:** a execução começou sem o resultado que mudaria a decisão; a evidência não tem número de execuções, dispersão ou limitador; ou "the time saved is larger than the time the changed piece took".

**Relevância para validação de fluxo agêntico:** alta. É o único princípio que trata explicitamente de **resultados de eval**. Exige que cada execução tenha feito a tarefa, que a diferença se mantenha entre trials e modelos e que o número venha com contagem, dispersão e limitador.

## principle-guard-the-context-window

Fonte: `mirror/pstack/skills/principle-guard-the-context-window/SKILL.md`

**Regra** (da `description` e do índice). Quando o contexto enche (outputs grandes, arquivos longos, leituras repetidas, planejamento de fan-out): "Route bulk to subagents; keep summaries in the main thread, not raw payloads."

**O que manda fazer.** O corpo traz o motivo, "Context overflow degrades reasoning quality, creates compression artifacts, and halts progress", e um único item de padrão: "**Size phases and cap scope.** Limit files per phase, set turn budgets, account for mechanism costs." O guia descreve o princípio como rotear "bulk reading to subagents" e manter as conclusões no chat principal. `minimize-reader-load` se declara o análogo humano deste.

**Relevância para validação de fluxo agêntico:** baixa. É gestão de contexto. O único ponto indireto é que um contexto saturado degrada o raciocínio, inclusive o de quem verifica.

## principle-never-block-on-the-human

Fonte: `mirror/pstack/skills/principle-never-block-on-the-human/SKILL.md`

**Regra.** O humano supervisiona de forma assíncrona e os agentes não podem ficar bloqueados. "Make reasonable decisions, proceed, and let the human course-correct after the fact."

**O que manda fazer.**
- "Proceed, then present." Não perguntar "should I do X?". Fazer X e explicar por quê.
- Sistema autocorretivo: ao notar um problema, registrá-lo e corrigi-lo na rodada seguinte.
- Ações irreversíveis (force-push, apagar dados de produção, enviar mensagens externas) ainda exigem confirmação.
- Ações reversíveis (escrever código, editar notas, dividir tarefas) seguem sem bloqueio.
- "Product direction comes from the human. Execution should not block."

O `poteto-mode` reforça isso ao classificar uma pergunta antes de fazê-la. Se a resposta é um fato observável executando algo, o agente prototipa em vez de perguntar.

**Relevância para validação de fluxo agêntico:** baixa a média. O princípio desloca a validação humana para depois do fato, o que só funciona se o resultado vier com evidência (ver `prove-it-works`). Ele mesmo não verifica nada.

## principle-encode-lessons-in-structure

Fonte: `mirror/pstack/skills/principle-encode-lessons-in-structure/SKILL.md`

**Regra** (da `description` e do índice). Ao escrever a mesma instrução pela segunda vez ou notar uma correção recorrente: "Encode the rule as a lint, metadata flag, runtime check, or script instead of more text."

**O que manda fazer.** O corpo traz só o caso de exceção e um corolário:
- "If the lesson needs judgment and cannot be encoded, make the instruction more prominent and add an example of the failure mode."
- "**Corollary:** If the fix is structural, only use the structural fix. The instruction is the symptom."

O guia aponta a skill `/correct` como aplicação no repositório inteiro. Ela minera o histórico por classes de erro e corrige cada uma no nível mais alto que funciona: "architecture, then types, lint, and ci, then tests, with docs last" (`README.md`, linha 145).

**Relevância para validação de fluxo agêntico:** média. O princípio transforma correções recorrentes de agentes em checks automáticos (lint, runtime check, script), que validam a saída de toda execução futura sem depender de o agente seguir texto.

---

## Tabela-resumo

A coluna "Grupo no pstack" reproduz o agrupamento do `poteto-mode` e do README. A coluna "Categoria inferida" usa as cinco categorias deste estudo (design / verification / execution / context / code hygiene) e é uma classificação nossa, não da fonte.

| Princípio | Essência em uma linha | Grupo no pstack | Categoria inferida |
|---|---|---|---|
| `principle-laziness-protocol` | Menor diff que resolve; consolidar decisões numa fonte única. | core | code hygiene |
| `principle-foundational-thinking` | Estruturas de dados e scaffold antes da lógica. | core | design |
| `principle-redesign-from-first-principles` | Integrar um requisito novo como se existisse desde o início. | core | design |
| `principle-attack-the-premise` | Após duas correções falhas com a mesma premissa, escrever e testar a premissa. | core | verification |
| `principle-subtract-before-you-add` | Remover peso morto antes de construir. | core | code hygiene |
| `principle-minimize-reader-load` | Cortar camadas e estado oculto que o leitor precisa carregar. | core | code hygiene |
| `principle-outcome-oriented-execution` | Convergir no estado final verificável, sem código de compatibilidade descartável. | core | execution |
| `principle-experience-first` | Escolher a experiência do usuário em vez da conveniência de implementação. | core | design |
| `principle-exhaust-the-design-space` | Sem precedente, 2-3 protótipos concorrentes comparados lado a lado. | core | design |
| `principle-build-the-lever` | Construir o script que faz ou prova o trabalho, reexecutável por um revisor. | core | execution |
| `principle-model-the-domain` | Codificar o domínio numa estrutura, não em condicionais espalhadas. | architecture | design |
| `principle-boundary-discipline` | Validar nas fronteiras, confiar nos tipos internos, lógica pura. | architecture | design |
| `principle-type-system-discipline` | Estados ilegais irrepresentáveis, primitivos com brand, parse na fronteira. | architecture | design |
| `principle-make-operations-idempotent` | Convergir ao mesmo estado final após crash, restart ou retry. | architecture | design |
| `principle-migrate-callers-then-delete-legacy-apis` | Migrar chamadores e apagar a API antiga na mesma onda. | architecture | code hygiene |
| `principle-separate-before-serializing-shared-state` | Eliminar o compartilhamento antes de recorrer a locks. | architecture | design |
| `principle-prove-it-works` | Verificar o artefato real, não proxy, autorrelato ou "it compiles". | verification | verification |
| `principle-fix-root-causes` | Reproduzir e corrigir onde o sistema errou primeiro, não onde o sintoma apareceu. | verification | verification |
| `principle-sequence-verifiable-units` | Unidades pequenas, cada uma verde antes da próxima; commits que provam o trabalho. | verification | verification |
| `principle-test-behavior-not-implementation` | Testes que falham quando o comportamento quebra e sobrevivem a refatorações. | verification | verification |
| `principle-explain-the-number` | Nomear o limitador e descartar medições espúrias antes de confiar num número. | verification | verification |
| `principle-guard-the-context-window` | Volume para subagentes, resumos no thread principal. | delegation | context |
| `principle-never-block-on-the-human` | Seguir em trabalho reversível e apresentar o resultado; pausar só no irreversível. | delegation | execution |
| `principle-encode-lessons-in-structure` | Instrução repetida vira lint, check ou script. | meta | code hygiene |
