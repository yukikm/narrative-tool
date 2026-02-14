from __future__ import annotations

import typer
from rich.console import Console

from .detect import DetectParams, detect_narratives
from .ideas import generate_ideas, ideas_to_markdown
from .io import load_jsonl, read_json, write_json, write_text

app = typer.Typer(add_completion=False)
console = Console()


@app.command()
def detect(
    inp: str = typer.Argument(..., help="Input JSONL file"),
    out: str = typer.Option("out/report.json", help="Output report JSON"),
    time_field: str = typer.Option("created_at", help="Timestamp field name"),
    recent_days: int = typer.Option(3, help="Recent window (days) for trend scoring"),
    k_min: int = typer.Option(2, help="Min clusters"),
    k_max: int = typer.Option(8, help="Max clusters"),
):
    items = load_jsonl(inp, time_field=time_field)
    params = DetectParams(k_min=k_min, k_max=k_max, recent_days=recent_days)
    report = detect_narratives(items, params=params)
    write_json(out, report)
    console.print(f"[green]Wrote[/green] {out} (narratives={len(report['narratives'])}, items={report['item_count']})")


@app.command()
def ideas(
    report: str = typer.Argument(..., help="Report JSON from `detect`"),
    out: str = typer.Option("out/ideas.md", help="Output markdown"),
    max_per_narrative: int = typer.Option(7, help="Max ideas per narrative"),
):
    rep = read_json(report)
    obj = generate_ideas(rep, max_per_narrative=max_per_narrative)
    md = ideas_to_markdown(obj)
    write_text(out, md)
    console.print(f"[green]Wrote[/green] {out}")


if __name__ == "__main__":
    app()
