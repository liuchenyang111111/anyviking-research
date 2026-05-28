# Synthetic AI News Demo

This demo uses project-owned synthetic markdown files. It is the safest demo to run in a meeting because it does not depend on a private old project folder and it does not copy real news articles into the repository.

## Corpus

Source folder:

```text
examples\synthetic_ai_news\source
```

Recommended OpenViking target URI:

```text
viking://resources/synthetic-ai-news
```

The corpus contains short synthetic notes about:

- AI search product direction.
- Edge LLM devices.
- Agent browsing and research workflows.
- Enterprise knowledge-base retrieval.
- Open-source retrieval tools.
- Evaluation and governance.
- Product roadmap planning.

## Run The Demo

```powershell
.\examples\synthetic_ai_news\run_demo.ps1
```

The script checks OpenViking health, imports the corpus, shows the resource tree, and runs one search.

## Generate A Research Draft

```powershell
.\examples\synthetic_ai_news\run_research.ps1
```

Default output:

```text
reports\synthetic_ai_news_research_draft.md
```

## Manual Commands

```powershell
ar import-local examples\synthetic_ai_news\source --to viking://resources/synthetic-ai-news
```

```powershell
ar search "How do edge LLMs and local retrieval complement each other?" --scope viking://resources/synthetic-ai-news --top-k 5 --documents-only --format text
```

```powershell
ar research examples\synthetic_ai_news\research_questions.yaml --output reports\synthetic_ai_news_research_draft.md --top-k 4
```

More search examples are in [queries.md](queries.md).
