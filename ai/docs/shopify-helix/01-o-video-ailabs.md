# 01 · O vídeo do AI LABS: o que ele mostra e o que acrescenta

> **Fonte:** AI LABS, [*"Shopify Just Released The Greatest AI Coding Workflow Ever"*](https://youtu.be/bBMp5tLxShQ),
> publicado em 2026-09-24, duração 891 s. Metadados obtidos com `yt-dlp --write-info-json` em 2026-10-14
> `[verificado]`. O transcript não pôde ser baixado (ver [Limitação](README.md#limitação-conhecida)). Este capítulo se
> apoia na descrição e nos capítulos oficiais do vídeo.

## A tese do vídeo

Segundo a descrição, a Shopify publicou o método do Helix sem mostrar a implementação. O AI LABS refez o caminho e
montou uma versão própria em **Claude Code**, testada com features de um app interno de RH que o canal estava
construindo `[verificado]`. A descrição deixa claro que o resultado não substitui o engenheiro: ainda é preciso aprovar
o plano e testar o resultado.

## Os capítulos

| Tempo | Capítulo (original) | O que cobre, segundo a descrição |
|---|---|---|
| 00:00 | Intro | O caso Shopify: app de 300 telas reconstruído com agentes |
| 00:55 | Core Mechanism | Um orquestrador conduz agentes por checkpoints e quatro gates |
| 03:01 | Checkpoints | Um agente *Checkpoint Planner* divide a feature em tarefas pequenas, da mais simples à mais complexa. Um viewer simples mostra o plano em linguagem comum antes de construir |
| 05:25 | Gates | Visão geral dos quatro gates |
| 06:38 | Sponsor | Patrocínio (fora do escopo) |
| 07:32 | Gate 1: Behavior | Testes planejados e escritos **antes** do código; todos precisam passar |
| 09:18 | Gate 2: UI | O app é comparado com um **protótipo HTML** e um arquivo **`design.md`**. Subagents Claude no lugar do Gemini |
| 11:56 | Gate 3: Code Review | Um agente parte do princípio de que o código está errado e caça problemas. Um agente *fixer* corrige, e os dois alternam até aprovar |
| 13:11 | Gate 4: Human Review | Você testa a feature. O feedback vira novos checkpoints e um **arquivo de learnings** que todo agente lê |
| 13:47 | The Orchestrator | Tudo roda como workflow dinâmico no Claude Code. Cada subagent começa com contexto novo, e o fluxo só para para você duas vezes |

## O que é da Shopify e o que é do AI LABS

Esta é a separação central do estudo. A coluna "Na Shopify?" foi conferida no texto bruto do post do Helix
`[verificado]`.

| Elemento do vídeo | Na Shopify? | Tier |
|---|---|---|
| Checkpoints pequenos e ordenados, revisados antes de construir | **Sim** | A |
| Gate 1 com testes gerados a partir da referência | **Sim**. Na Shopify, um subagent gera os testes, que rodam por uma CLI do app | A |
| Gate 2 com revisão visual por modelo multimodal | **Sim**, mas com **Gemini** julgando screenshots do app de referência | A |
| Gate 3 com revisão adversarial | **Sim**, mas com **dois** revisores de contexto isolado contra a arquitetura documentada | A |
| Gate 4 com aprovação humana que alimenta uma memória | **Sim** | A |
| Orquestrador | **Sim**, e a Shopify diz que é um modelo **GPT** | A |
| **Stop hook "estilo Ralph loop"** que impede o agente de parar antes dos gates | **Não**. O post não cita Ralph nem hooks | B |
| Subagents **Claude** no lugar do Gemini | **Não**. A Shopify usa Gemini e justifica a escolha pela noção espacial do modelo | B |
| Protótipo **HTML** e **`design.md`** como referência visual | **Não**. A referência da Shopify é o app React Native rodando | B |
| Par revisor ↔ *fixer* no gate 3 | **Não** nesse formato. Na Shopify, o agente implementador corrige o que os dois revisores apontam | B |
| **Arquivo de learnings** lido por todos os agentes | **Parcial**. A Shopify fala em "memória", sem dizer o formato | B (formato) |
| "Workflow dinâmico" do Claude Code com subagents de contexto novo | **Não**. É a ferramenta escolhida pelo AI LABS | B |

### Por que a troca de referência importa

A Shopify migra um app **que já existe**, então a referência visual é a tela real em React Native, capturada no mesmo
estado da tela nova. O AI LABS constrói **features novas**, e não há app de referência. Por isso precisou de um
substituto: um protótipo HTML e um `design.md`. A própria Shopify prevê esse caso ao dizer que, numa feature nova, o
Helix usa designs e docs de produto como referência `[verificado]`. O AI LABS, portanto, recriou a variante "feature
nova", e não a variante "migração" que deu origem ao Helix.

> **Cuidado com o nome `design.md`.** O Kiro (AWS) também gera um `design.md`, mas lá ele guarda decisões de
> arquitetura e tecnologia, não referência visual `[conferido]`. Pela descrição, o `design.md` do AI LABS é um
> documento de design visual. Os dois não devem ser confundidos.

## Perguntas abertas

Só o transcript ou a tela do vídeo responderiam a estas perguntas:

1. O Stop hook do AI LABS libera a parada com base em um **sinal externo** (arquivo de status escrito pelos testes e
   revisores) ou em uma **promessa do próprio modelo**, como no plugin `ralph-wiggum`? A diferença é decisiva. O
   [capítulo 04](04-claude-code-e-cursor.md#o-erro-a-evitar-confiar-na-promessa-do-modelo) explica por quê.
2. Como o hook lida com o teto de 8 continuações seguidas do Claude Code e com `stop_hook_active`?
3. Qual é o formato do arquivo de learnings, e quem o poda?
4. As skills do vídeo estão no AI Labs Pro, que é pago, e não foram inspecionadas.

---

[↑ README](README.md) · [Próximo → 02 · Helix segundo a Shopify](02-helix-fonte-primaria.md)
