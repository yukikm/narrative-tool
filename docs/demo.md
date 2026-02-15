# Demo (reproducible)

This demo is designed to be reproducible **offline** using the included sample dataset.

## Commands

```bash
# Ubuntu/Debian deps (if missing)
sudo apt-get update
sudo apt-get install -y python3-venv python3-pip

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python -m narrativelens detect data/sample_posts.jsonl --out out/report.json
python -m narrativelens ideas out/report.json --out out/ideas.md

# (Optional) also write to docs/examples for a shareable artifact
python -m narrativelens detect data/sample_posts.jsonl --out docs/examples/report.json
python -m narrativelens ideas docs/examples/report.json --out docs/examples/ideas.md
```

## Expected artifacts

- `out/report.json` (detected narratives)
- `out/ideas.md` (ideas grouped by narrative)
- `docs/examples/report.json` + `docs/examples/ideas.md` (same, committed for easy review)

## Notes

- This is a prototype; clustering quality depends on dataset size and text quality.
- For real usage, swap in a bigger dataset and/or add better topic modeling (embeddings).
