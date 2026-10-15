# Lost in the Middle: How Language Models Use Long Contexts

**Source:** https://arxiv.org/abs/2307.03172
**Authors:** Nelson F. Liu, Kevin Lin, John Hewitt, Ashwin Paranjape, Michele Bevilacqua, Fabio Petroni, Percy Liang
**Year:** 2023 (preprint); 2024 (published in TACL)
**arXiv ID:** 2307.03172 [cs.CL]
**DOI:** https://doi.org/10.48550/arXiv.2307.03172
**Category:** Long Context Research

> **Currency check (2026-10-11):** Partially outdated
>
> - **Still holds as a historical result:** the U-shaped curve was measured on 2023-era models (GPT-3.5-Turbo and Claude-1.3 among them), with context lengths far below today's 1M-token windows. The source URL is still live and the paper is unchanged.
> - **Could not verify on 2026 models:** I found no replication of this exact setup on current frontier models (Claude 5.5 family, GPT-5.x, Gemini 3.x). Do not quote the 20+ point drop as a property of today's models.
> - **Refined by later work:** Veseli et al. (Aug 2025) show the effect depends on how full the window is — strongest when the input fills up to ~50% of the window, then primacy fades and only a recency (distance-from-the-end) bias remains (https://arxiv.org/abs/2508.07479).
> - **Superseding frame is "context rot":** Chroma's July 2025 study of 18 models (Claude Opus 4 / Sonnet 4, GPT-4.1, o3, Gemini 2.5, Qwen3) found reliability drops as input grows, non-uniformly, even on simple tasks (https://www.trychroma.com/research/context-rot); Anthropic's own docs now state "as token count grows, accuracy and recall degrade" for models that all ship a 1M-token window (https://platform.claude.com/docs/en/build-with-claude/context-windows).
> - **Practical reading in Oct 2026:** keep the placement heuristic (critical material at the start or end, query near the end) as cheap insurance, but treat window size, not position alone, as the main variable.

## Abstract / Summary

While recent language models have the ability to take long contexts as input, relatively little is known about how well they use longer context. The authors analyze the performance of language models on two tasks that require identifying relevant information in their input contexts: multi-document question answering and key-value retrieval. Performance can degrade significantly when changing the position of relevant information, indicating that current language models do not robustly make use of information in long input contexts. Performance is often highest when relevant information occurs at the beginning or end of the input context, and significantly degrades when models must access relevant information in the middle of long contexts, even for explicitly long-context models.

## Key Findings

- **Positional bias confirmed across models:** All examined language models (including those explicitly designed for long contexts) show a pronounced bias toward beginning and end positions.
- **Multi-document QA benchmark:** Using the NaturalQuestions-Open dataset, performance varies significantly based solely on which position the relevant document is placed in a list of 20 documents.
- **Key-value retrieval task:** A synthetic retrieval task over long JSON inputs confirms the same U-shaped performance curve.
- **Performance degrades in the middle:** Even when relevant information is present in the context, models fail to reliably retrieve it if it is positioned in the middle.
- **Evaluation protocol contribution:** Proposed new evaluation methodologies for long-context language model benchmarking.

## Content

### Submission History

- **[v1]** Thu, 6 Jul 2023 17:54:11 UTC (410 KB)
- **[v2]** Mon, 31 Jul 2023 17:48:48 UTC (416 KB)
- **[v3]** Mon, 20 Nov 2023 23:09:34 UTC (334 KB)

### Abstract (Full)

While recent language models have the ability to take long contexts as input, relatively little is known about how well they use longer context. We analyze the performance of language models on two tasks that require identifying relevant information in their input contexts: multi-document question answering and key-value retrieval. We find that performance can degrade significantly when changing the position of relevant information, indicating that current language models do not robustly make use of information in long input contexts. In particular, we observe that performance is often highest when relevant information occurs at the beginning or end of the input context, and significantly degrades when models must access relevant information in the middle of long contexts, even for explicitly long-context models. Our analysis provides a better understanding of how language models use their input context and provides new evaluation protocols for future long-context language models.

### Metadata

- **Subjects:** Computation and Language (cs.CL)
- **Paper length:** 18 pages, 16 figures
- **Status:** Accepted for publication in Transactions of the Association for Computational Linguistics (TACL), 2023

### Notes

This is the arXiv preprint of the paper officially published in TACL 2024 (ACL Anthology ID: 2024.tacl-1.9). The published version is also available at:
- ACL Anthology: https://aclanthology.org/2024.tacl-1.9
- MIT Press DOI: https://doi.org/10.1162/tacl_a_00638

See also `lost-in-the-middle-acl.md` for the official ACL Anthology entry and `lost-in-the-middle-researchgate.md` for the ResearchGate reference.
