# NarrativeLens (prototype)

Open-source **narrative detection + idea generation** tool.

- **Input:** a JSONL file of posts/articles (offline friendly)
- **Output:** detected narratives (clusters), narrative scores (volume + trend), and generated ideas per narrative

This is a working prototype intended for Superteam Earn listing **“develop-a-narrative-detection-and-idea-generation-tool”**.

## What it does

1. **Narrative detection**
   - Converts each item into a text document (title + optional body)
   - Vectorizes with **TF‑IDF**
   - Clusters with **KMeans** (auto-selects k in a small range)
   - Names each cluster using top keywords

2. **Narrative scoring**
   - **volume:** number of items in the cluster
   - **trend:** compares recent-window frequency vs baseline (simple growth ratio)
   - **score:** weighted combination (defaults tuned for demo)

3. **Idea generation (non-LLM, offline)**
   - Produces 5–10 actionable ideas per narrative using templates
   - (Optional) you can plug in an LLM later; the interface is separated

## Quickstart

### 1) Create a venv + install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Run on the included sample dataset

```bash
python -m narrativelens detect data/sample_posts.jsonl --out out/report.json
python -m narrativelens ideas out/report.json --out out/ideas.md
```

### 3) View a human-friendly report

```bash
cat out/ideas.md
```

## CLI

### Detect narratives

```bash
python -m narrativelens detect <input.jsonl> --out out/report.json
```

Options:
- `--time-field created_at` (default)
- `--recent-days 3` (default)
- `--k-min 2 --k-max 8`

### Generate ideas

```bash
python -m narrativelens ideas out/report.json --out out/ideas.md
```

## Input format (JSONL)

Each line is a JSON object:

```json
{"id":"1","created_at":"2026-02-10T12:00:00Z","source":"rss","title":"Solana DePIN projects surge","text":"...optional...","url":"https://..."}
```

## Output format

- `out/report.json` contains:
  - clusters (narratives): keywords, example items, volume, trend, score
  - global params used

## Demo evidence

See `docs/demo.md` for a reproducible run log (commands + expected artifacts).

## Roadmap / plug-ins

- Add real data sources (RSS/HN/GitHub trends/X) behind an interface.
- Add LLM-backed summarization + idea generation.
- Use better topic modeling (BERTopic / embeddings) when compute allows.

## License

MIT
