# Três novos eixos de review para o `/run-spec`: Security, UX/UI/AIX e Design

> **Estudo, 2026-11-15.** Síntese de uma deep research (5 ângulos, 23 fontes buscadas, 109 claims extraídas, 25 verificadas por votação adversarial 3 a 3) mais leitura direta de fontes primárias e dos arquivos locais. Cada afirmação traz a fonte. O que não foi verificado está marcado como tal.

## 1. Problema

O review final do `/run-spec` (step 6 de `~/.claude/skills/run-spec/SKILL.md`) roda a skill `mattpocock-skills:code-review`, pinada em 1.3.1. Ela tem dois eixos fixos:

- **Standards**: o código segue os padrões documentados do repo, mais um baseline de code smells de Fowler.
- **Spec**: o código faz o que a spec pediu.

A skill diz explicitamente "two axes, don't merge or rerank". Faltam três lentes: segurança, experiência (de humanos e de agentes) e design de módulos. Este estudo define as fontes e o formato de brief de cada uma.

## 2. Decisões tomadas (2026-11-15)

| Decisão | Escolha | Motivo |
|---|---|---|
| Quais eixos bloqueiam a saída do loop | Standards, Spec e **Security** | Design e UX são julgamento. Se bloqueassem, um round limpo ficaria raro com o teto de 3 rounds. |
| Destino de Design e UX/AIX | Vão para o `review-fixer` (corrige com >80% de confiança, senão dispensa com motivo), sem reabrir round | Mesma regra que o fixer já aplica a Standards |
| Onde os eixos novos rodam | Só no review final (step 6). O review por ticket do `ticket-implementer` continua com 2 eixos | Custo: 5 eixos × N tickets × rounds |
| Quem orquestra | O `/run-spec` spawna os 3 eixos novos com briefs próprios, ao lado da skill pinada | A skill é de terceiro, pinada à mão, e hardcoda dois eixos |
| Filtro de falso positivo no Security | Um reviewer único: exploit path obrigatório, lista de exclusões, corte ≥8/10, e um balde `needs-human` para crypto/config | Evita N spawns de filtro. Ver o custo em §3.4. |
| Quando o eixo UX/UI/AIX roda | **Só quando o diff toca o domínio.** O orquestrador decide pela lista de arquivos alterados antes de spawnar o reviewer (ver §4.1) | Pedido do usuário: o run-spec deve ser inteligente o bastante para pular o eixo |
| Versionamento | Editar direto em `~/.claude` (sem importar para git) | Escolha do usuário. Fica sem rollback. |

## 3. Eixo Security

### 3.1 Fontes de critério

- **Prompt do `/security-review` da Anthropic** ([repo](https://github.com/anthropics/claude-code-security-review), [`security-review.md`](https://raw.githubusercontent.com/anthropics/claude-code-security-review/main/.claude/commands/security-review.md)). É o modelo mais bem documentado de reviewer de diff com LLM. A skill `security-review` desta sessão tem a mesma descrição, o que sugere que ela usa esse prompt.
- **OWASP Top 10 for Agentic Applications 2026** ([dez/2025](https://genai.owasp.org/resource/2025-12-09/owasp-top-10-for-agentic-applications-for-2026)): ASI01 Agent Goal Hijack, ASI02 Tool Misuse, ASI03 Identity and Privilege Abuse, ASI04 Agentic Supply Chain, ASI05 Unexpected Code Execution, ASI06 Memory & Context Poisoning, ASI07 Insecure Inter-Agent Communication, ASI08 Cascading Failures, ASI09 Human-Agent Trust Exploitation, ASI10 Rogue Agents.
- **Local**: `ai/agents/product-pipeline/shared/shared-security-architect.md` traz OWASP Top 10:2025, ASVS 5.0 e anti-patterns (generic Top 10 paste, severity inflation, IDs inventados). Ele revisa DFD e PRD, não diff, mas os anti-patterns valem para o eixo.

### 3.2 O que o prompt da Anthropic faz (verificado, 3-0)

- Revisa **só o que o diff adiciona**: "focus ONLY on security implications newly added by this PR" (linha 36).
- Exige ">80% confident of actual exploitability" (linha 39).
- Reporta só HIGH e MEDIUM. HIGH é diretamente explorável (RCE, vazamento de dados, auth bypass). MEDIUM exige condições específicas, e só entra se for "obvious and concrete". LOW é desencorajado.
- Cada finding traz: arquivo, linha, severidade, categoria (`sql_injection`, `xss`…), descrição, exploit scenario, recomendação e confiança.
- Roda em três passos: um finder; um sub-agente filtro por candidato, em paralelo, com nota 1–10; descarte abaixo de 8.
- **Hard exclusions**: DoS e esgotamento de recursos, rate limiting, falta de hardening, libs desatualizadas, arquivos só de teste, log spoofing, SSRF que só controla o path, conteúdo do usuário em system prompt, regex injection e ReDoS, docs/markdown, audit log ausente, segredos em disco já protegidos, validação em campo não crítico, race condition teórica e memory safety em linguagem memory-safe.

### 3.3 Padrões agentic checáveis no diff (OWASP, 3-0)

- **ASI05**: `eval()` sobre conteúdo não confiável, desserialização insegura, shell montado a partir de prompt ou output do modelo, instalação de pacote em runtime sem verificação.
- **ASI02**: cada tool com escopo de menor privilégio; ação destrutiva com confirmação humana ou dry-run; output do LLM tratado como input não confiável, validado antes de executar.
- Use os IDs para **marcar** findings, não como checklist obrigatório. ASI08–ASI10 são propriedades de runtime que o diff só mostra em parte.

### 3.4 Armadilhas de LLM em revisão de segurança (papers revisados)

- **Muitos falsos positivos.** Os modelos marcam como vulnerável código que já foi corrigido. Renomear variáveis inverteu a resposta em 26% (PaLM2) e 17% (GPT-4) dos casos ([Ullah et al., IEEE S&P 2024](https://arxiv.org/pdf/2312.12575)).
- **Benchmarks enganam.** No PrimeVul, GPT-4 com CoT acertou o par vulnerável/corrigido em 12,94% dos casos, contra 22,70% do chute aleatório ([Ding et al., ICSE 2025](https://arxiv.org/html/2403.18624v2)).
- **Filtrar demais perde achados reais.** Triagem agentic sobre SAST levou o falso positivo de 98,3% a 6,3%, mas descartou 314 vulnerabilidades reais. As perdas se concentram em crypto e policy (CWE-327 77%, CWE-328 85%, CWE-501 77%) ([Xiong & Zhang, preprint jan/2026](https://arxiv.org/html/2601.22952v1); benchmark sintético, não revisado por pares).
- **Consequência para o brief:**
  - exigir exploit path (source → sink) por finding;
  - checar se o próprio diff já mitiga;
  - nunca descartar crypto/config em silêncio, e sim mandar para `needs-human`;
  - tratar o eixo como apoio à decisão.

### 3.5 Outline do brief

- **Escopo**: só vulnerabilidades novas no diff `BASE...WORK`. Use Read/Grep fora do diff apenas para seguir o fluxo de dados.
- **Taxonomia**: OWASP Top 10:2025 para web/API, e ASI01–ASI10 quando o diff toca código de agente, tool, MCP ou LLM.
- **Evidência por finding**: `file:line`, categoria, exploit path, fix e confiança 1–10.
- **Report**: HIGH/MEDIUM com confiança ≥8. Abaixo disso só entram findings de crypto, config ou policy, e marcados `needs-human`.
- **Não flagrar**: as hard exclusions de §3.2, findings já mitigados no diff e problemas pré-existentes fora do diff.

## 4. Eixo UX/UI/AIX

"AIX" cobre os dois sentidos:

- **AI Experience**: a UX de features de IA para humanos.
- **Agent Experience (AX)**: o quanto o código, a CLI, as APIs e as tools são consumíveis por agentes.

### 4.1 Gatilho: o eixo só roda quando o diff toca o domínio

O orquestrador decide **antes** de spawnar, sem gastar um reviewer para ouvir "não se aplica":

1. Lista os arquivos do range revisado: `git diff --name-only BASE...WORK`.
2. Casa a lista com os padrões de `axes/ux-aix.triggers` (uma regex estendida por linha, `grep -E -f`), que podem ser ajustados por instalação.
   - **UI / front-end**: `*.tsx`, `*.jsx`, `*.vue`, `*.svelte`, `*.astro`, `*.html`, `*.css`, `*.scss`, `*.less`, templates (`*.hbs`, `*.ejs`, `*.erb`, `*.jinja*`, `*.njk`), strings e i18n (`locales/**`, `i18n/**`, `*.po`), design tokens (`tokens/**`, `tailwind.config.*`, `theme.*`).
   - **Agent Experience**: definições de tool/MCP (`**/mcp/**`, `**/tools/**`), entrypoints de CLI (`**/cli/**`, `bin/**`), prompts e mensagens voltados a agentes (`**/prompts/**`).
3. Sem casamento, o eixo é **pulado**. O relatório registra `## UX/AIX — skipped: no UI or agent-surface files in <range>`, para que a ausência seja visível e auditável.
O gatilho olha só a lista de arquivos, nunca a spec. O contrato do dispatcher proíbe que ele leia spec, tickets ou código (`SKILL.md`, "Dispatcher contract"). Uma mensagem de erro em código de backend que chega ao usuário escapa do gatilho.

Os padrões são heurística. Um repo com layout incomum ajusta o arquivo de triggers. O custo do falso negativo é perder um review de julgamento, que de qualquer forma não bloqueia a saída do loop.

### 4.2 Fontes de critério

- **UI**: as 10 heurísticas de Nielsen ([NN/g](https://www.nngroup.com/articles/ten-usability-heuristics/), verificado na fonte); a matriz de estados (ideal, loading, empty tipado, partial, error tipado, success) e as regras de strings de `ai/agents/product-pipeline/prd/prd-experience-designer.md`; e as SCs WCAG 2.2 AA que dá para checar no código, da lista de `shared-accessibility-reviewer.md` §5: 1.1.1, 1.3.1, 2.1.1, 2.4.3, 2.4.7, 3.3.1, 3.3.2, 4.1.2, 4.1.3.
- **AI Experience**: as 18 guidelines do HAX (Amershi et al., CHI 2019), em quatro fases: inicial, durante a interação, quando o sistema erra, ao longo do tempo ([HAX Toolkit](https://www.microsoft.com/en-us/haxtoolkit/ai-guidelines/), 3-0). A fase "when wrong" (dispensar, corrigir, explicar por que agiu) mapeia para fallback, correção e undo visíveis no código. Limite: as guidelines são anteriores à IA generativa e não falam de streaming, citação ou alucinação.
- **Agent Experience**:
  - Erros de tool dizem que correção fazer, idealmente com exemplo, em vez de código opaco ou traceback ([Anthropic, Writing tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents), 3-0).
  - Respostas limitam tokens com paginação, filtro ou truncamento. O Claude Code corta output de MCP em 25k tokens e avisa em 10k ([docs MCP](https://code.claude.com/docs/en/mcp.md)).
  - Na MCP spec 2025-11-25 (SEP-1303), erro de validação de input vira `isError: true`, para o modelo se corrigir.
  - Para CLI ([clig.dev](https://clig.dev), verificado na fonte): mensagens e erros vão para `stderr`; output legível por máquina quando não atrapalha (`--json`, `--plain`); erros esperados são capturados e reescritos para humanos, com a ação de correção.
- **Formato do reviewer**: o agente de acessibilidade do GitHub separa um reviewer passivo de um implementador, impõe uma ordem fixa de fases (pesquisa, auditoria de código, saída estruturada) e dá a cada finding critical/warning/info, a SC, `file:line`, experiência atual vs esperada e remediação ([GitHub Blog, mai/2026](https://github.blog/ai-and-ml/github-copilot/building-a-general-purpose-accessibility-agent-and-what-we-learned-in-the-process/); post único, sem dado de resultado).

### 4.3 Outline do brief

- **Checar**:
  - todo componente ou tela nova cobre loading, empty, error e success;
  - textos de erro dizem o problema e a recuperação;
  - SCs legíveis no código (nome acessível, semântica nativa antes de ARIA, foco, status messages);
  - features de IA têm caminho para dispensar, corrigir e desfazer;
  - erros de tool, MCP e CLI são acionáveis, e o output é limitado.
- **Não flagrar**: contraste, reflow e layout (precisam de render, então vão como `deferred-to-build`); gosto visual; nunca declarar conformidade WCAG.
- **Evidência**: `file:line`, a SC, heurística ou guideline violada, e a experiência atual vs esperada.
- **Severidade**: critical / warning / info.

## 5. Eixo Design

### 5.1 Fonte

A base são as skills locais pinadas (`~/.claude/plugins/cache/mattpocock/mattpocock-skills/1.3.1/skills/engineering/`), idênticas ao upstream nesta data:

- **`codebase-design`**: vocabulário obrigatório. **module**, **interface** (tudo que o caller precisa saber, inclusive invariantes, erros e ordem), **depth** (leverage por unidade de interface), **seam** (Feathers), **adapter**, **leverage**, **locality**. Termos proibidos: "component", "service", "API" e "boundary".
- **Princípios**:
  - deletion test;
  - "the interface is the test surface";
  - "one adapter = hypothetical seam, two = real one";
  - "replace, don't layer" nos testes.
- **Framing rejeitado**: profundidade como razão linhas/interface de Ousterhout. Vale depth como leverage.
- **`improve-codebase-architecture`**: severidade `Strong` / `Worth exploring` / `Speculative`; usa `GLOSSARY.md` para nomes de domínio; só reabre um ADR em `docs/adr/` quando a fricção é real.

A pesquisa web não verificou nada sobre Ousterhout, Feathers ou DDD além do que as skills já citam. O eixo se apoia no texto das skills.

### 5.2 Adaptação de "codebase inteira" para "diff"

A skill original varre o repo. O eixo de review olha **só os módulos que o diff cria ou cuja interface ele muda**:

- **Módulo raso novo**: a interface é quase tão grande quanto a implementação. Evidência: o deletion test, contando callers com Grep fora do diff.
- **Teste passando por fora da interface**: o teste toca internals, ou exige mudança quando só a implementação muda.
- **Seam hipotético**: port ou interface nova com um único adapter.
- **Perda de locality**: a mesma regra de negócio aparece espalhada em callers em vez de concentrada no módulo.
- **Vocabulário**: conceito novo sem termo no `GLOSSARY.md`, ou nome que contradiz o glossário.
- **Conflito com ADR**: só quando a fricção é concreta.

### 5.3 Outline do brief

- **Não flagrar**: Speculative Generality, Middle Man e Shotgun Surgery (já estão no baseline do eixo Standards); estilo; refactors de código fora do diff.
- **Evidência**: `file:line`, número de callers, princípio violado e o deepening proposto em uma linha.
- **Severidade**: `Strong` / `Worth exploring` / `Speculative`.

## 6. Claude Code vs Cursor

| Aspecto | Claude Code | Cursor | Gap |
|---|---|---|---|
| Onde o reviewer mora | `~/.claude/agents/ticket-reviewer.md` | Cursor lê `~/.claude/agents/` por compatibilidade ([subagents](../cursor/subagents/subagents-guide.md)) | — |
| Read-only | `tools: Read, Grep, Glob, Bash` | Não há campo `tools`; o equivalente é `readonly: true` | Adicionar `readonly: true` ao agent para o Cursor não ter escrita |
| Modelo | `model: claude-opus-5-5` | `inherit` ou ID do Cursor (`claude-opus-5[effort=high]`) | ID pode não resolver no Cursor; não verificado |
| Orquestração (`/run-spec`) | Skill em `~/.claude/skills/run-spec/` | Cursor carrega skills de `~/.claude/skills/` ([skills](../cursor/skills/agent-skills-guide.md)) | O fluxo depende de ferramentas do Claude Code (`ListAgents`, worktrees de subagent); a execução no Cursor não foi testada |
| Review hospedado em PR | — | Bugbot lê só Team Rules, `.cursor/BUGBOT.md` (raiz + aninhados) e arquivos linkados dele; ignora `.cursor/rules/*.mdc`; 30k caracteres por regra, 100k no total ([bugbot](../cursor/bugbot/bugbot.md)) | Os briefs são markdown puro: o repo-alvo linka cada um a partir do seu `.cursor/BUGBOT.md` |
| Review local | `code-review` + eixos do run-spec | `/review-bugbot` roda o Bugbot do agente sobre o diff da branch, sincronizado por patch ID | — |
| Hooks | Não usados por este fluxo | Não usados | — |
| MCP | Não usado pelos reviewers | Não usado | — |

## 7. Lacunas

- **Google PAIR** não foi verificado: a página é renderizada em JS e o PDF falhou.
- **Não verificados**: OWASP ASVS 5.0, CWE Top 25, Semgrep/CodeQL, Aardvark/Big Sleep e `llms.txt`. O brief de Security usa só o que está em §3.
- A evidência sobre armadilhas de LLM vem de modelos de 2023–2024 classificando funções isoladas, não de review agentic com contexto de repo.
- Os cortes 0,7 e 8/10 são instruções de prompt, não garantias.
- O fluxo do run-spec de 2026-11-12 ainda não rodou. Os eixos novos entram sobre um loop não testado.
