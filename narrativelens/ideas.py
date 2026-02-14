from __future__ import annotations

from typing import Any


IDEA_TEMPLATES = [
    ("Build", "Build a simple dashboard that tracks {name} signals daily; include alerts + source links."),
    ("Research", "Write a research note: 'What is {name} and why now?' Include key players, catalysts, risks."),
    ("Content", "Create a short thread/video explaining {name} in plain language; end with 3 actionable takeaways."),
    ("Tooling", "Ship a small open-source dataset/labeler for {name} posts to improve narrative detection."),
    ("Market", "Identify 3 startups in {name} and compare traction; publish a scored leaderboard."),
    ("Community", "Host a weekly community call around {name} and collect problems to turn into product ideas."),
    ("Trading", "Design a watchlist + rules for trading {name} catalysts; backtest on a small historical sample."),
]


def generate_ideas(report: dict[str, Any], max_per_narrative: int = 7) -> dict[str, Any]:
    out: dict[str, Any] = {"generated_from": report.get("generated_at"), "ideas": []}

    for nar in report.get("narratives", []):
        name = nar.get("name") or "this narrative"
        keywords = nar.get("keywords", [])
        ideas = []
        for label, tmpl in IDEA_TEMPLATES[:max_per_narrative]:
            ideas.append({"type": label, "text": tmpl.format(name=name), "keywords": keywords[:5]})

        out["ideas"].append(
            {
                "cluster_id": nar.get("cluster_id"),
                "name": name,
                "keywords": keywords,
                "score": nar.get("score"),
                "volume": nar.get("volume"),
                "trend_ratio": nar.get("trend_ratio"),
                "ideas": ideas,
            }
        )

    return out


def ideas_to_markdown(ideas_obj: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# NarrativeLens — Ideas")
    lines.append("")

    for nar in ideas_obj.get("ideas", []):
        lines.append(f"## {nar['name']}")
        lines.append("")
        lines.append(
            f"- score: {nar.get('score'):.3f} | volume: {nar.get('volume')} | trend_ratio: {nar.get('trend_ratio'):.2f}"
        )
        if nar.get("keywords"):
            lines.append("- keywords: " + ", ".join(nar["keywords"][:10]))
        lines.append("")
        for idea in nar.get("ideas", []):
            lines.append(f"- **{idea['type']}**: {idea['text']}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"
