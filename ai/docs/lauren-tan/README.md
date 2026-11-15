# Lauren Tan (poteto), pstack e a validação de fluxos agênticos

> **Estudo, 2026-11-15.** São três falas de Lauren Tan, lidas na íntegra pelas transcrições, com os slides capturados do vídeo. Inclui um mirror verbatim do pstack e a leitura de todos os seus artefatos. A pergunta central é como o método dela ajuda a validar um fluxo agêntico, e se e como ele se aplica ao `/run-spec` e ao `software-factory`.

## A ideia em quatro frases

Lauren Tan, ex-Meta, do time core do React Compiler, veio do Cursor ("which is now SpaceX AI", nas palavras dela) e hoje é Principal Engineer no Grok Bot da SpaceXSI. Ela diz ter shippado 3.000 PRs em um mês. O time dela shippou 11k, com revert em torno de 0,5%. Ela diz que o segredo não é orquestração: é **confiança** construída no ambiente. A ordem é a "poteto pyramid": codebase → análise estática → verificação → prosa → review humano. Toda correção vira check determinístico, o agente verifica o próprio trabalho rodando o app de verdade, e só depois disso se automatiza o loop ("don't automate a bad loop").

## Como ler

| # | Documento | Para quê |
|---|---|---|
| 01 | [A palestra (e mais duas falas)](01-a-palestra.md) | O que ela disse, slide a slide (30 frames), mais a sessão de agosto e a live com Matt Pocock; glossário dos termos |
| 02 | [pstack: visão geral e paridade Cursor × Claude Code](02-pstack-visao-geral.md) | Anatomia do plugin, como instalar e usar em cada harness, lacunas de paridade |
| 03 | [Catálogo dos 24 princípios](03-catalogo-principios.md) | Cada `principle-*`, com relevância para validação |
| 04 | [Catálogo das skills, agentes e Benny](04-catalogo-skills-agentes-automacoes.md) | As 33 skills situacionais, `poteto-agent`, `comment-sicko`, a automação Benny e o exemplo de verify skill |
| 05 | [Catálogo do `poteto-mode` e dos 23 playbooks](05-catalogo-poteto-mode-playbooks.md) | Roteamento, contratos, `check-plan.mjs` regra a regra, `watch-pr`, cada playbook |
| 06 | [O método como validação de fluxo agêntico](06-validacao-de-fluxo-agentico.md) | Oito pilares, diagrama, checklist de 15 perguntas, limites |
| 07 | [Aplicação ao `/run-spec` e ao `software-factory`](07-aplicacao-software-factory-e-run-spec.md) | Onde já se alinham, o que não transfere, tabela por camada, 10 propostas priorizadas |
| 08 | [Referências e o que ela valoriza](08-referencias.md) | 17 valores, fontes primárias e secundárias, refutações, divergências |

Se o tempo for curto, leia 01 (até o resumo dos termos), 06 e 07.

## Acervo

- [`mirror/pstack/`](mirror/pstack/): cópia verbatim de `cursor/plugins/pstack` no commit `bf0c7cd80abdbf7fe47b634978a7d1b4071f71a7` (2026-11-15T03:36Z), v0.15.42, licença MIT ([`LICENSE`](mirror/pstack/LICENSE)). Tem ~7,9 MB, a maior parte no corpus de testes do `statechart` (~3,8 MB) e nas imagens do guia (~2,3 MB). Extraído com `git -c core.autocrlf=false archive` para manter LF.
- [`mirror/verification-skill-example/`](mirror/verification-skill-example/): `poteto/verification-skill-example@d5abe70`. **Única alteração no mirror:** o diretório `.cursor/` foi renomeado para `dot-cursor/`. O Cursor descobre `.cursor/skills/` em qualquer subdiretório do repositório (`ai/docs/cursor/skills/agent-skills-guide.md:129-141`), e a skill fictícia `verify-atlas` seria carregada em sessões neste repo. O conteúdo dos arquivos está intacto. O `README.md` do exemplo ainda cita o caminho original.
- [`assets/talk/`](assets/talk/): 30 frames da palestra de novembro, nomeados `HHMMSS-assunto.jpg`.
- [`sources/`](sources/): transcrições automáticas das três falas.
- [`sources/software-factory-validation-map.md`](sources/software-factory-validation-map.md): mapa de como o `software-factory@1dffd43` valida hoje, em inglês, com evidência `file:line` e ADR. É a base da seção do software-factory no 07.

## Método

- **Vídeo.**
  - A legenda veio do `youtube_transcript_api`.
  - O vídeo de novembro foi baixado com `yt-dlp` em 720p. Os frames foram extraídos com `ffmpeg` (binário do `imageio-ffmpeg`), primeiro um a cada 10 s em contact sheets para mapear os slides, depois um por slide escolhido. Não foram prints de navegador.
  - Nomes e números vêm sempre do slide, porque a legenda automática troca nomes ("Potato", "Graph Bot", "P stack").
- **pstack.** Lido direto do mirror. Os catálogos 03–05 foram escritos por três subagentes com briefs de fidelidade (identificadores verbatim, caminho citado por item) e conferidos por contagem de seções e existência dos caminhos.
- **Deep research.** O workflow `deep-research` fez 5 ângulos, 19 fontes, 90 claims e 25 verificadas por voto adversarial 3 a 3: 23 confirmadas, 2 refutadas. Usado para achar fontes, como a palestra de agosto. Só entrou no texto o que foi rastreado até as falas, os slides ou o mirror.
- **Lado do usuário.**
  - O `/run-spec` foi analisado em `feat/run-spec-aaa@8f79b33`, a versão instalada, e não na cópia de `main`.
  - O `software-factory` foi mapeado por um agente só-leitura com CodeGraph e leitura de ADRs.
  - Nenhum dos dois foi editado.
- **Harness.** Cursor e Claude Code aparecem lado a lado (regra do `CLAUDE.md` deste repo). As afirmações sobre instalação e Custom Mode foram checadas em `ai/docs/claude-code/` e `ai/docs/cursor/`. O comando `/add-plugin` do Cursor vem só do README do pstack e não aparece nos docs espelhados do Cursor.
