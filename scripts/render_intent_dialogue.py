#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


def parse_frontmatter(text: str) -> tuple[dict, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text
    try:
        end_index = lines[1:].index("---") + 1
    except ValueError:
        return {}, text
    frontmatter = "\n".join(lines[1:end_index])
    body = "\n".join(lines[end_index + 1 :]).lstrip()
    if yaml is not None:
        payload = yaml.safe_load(frontmatter) or {}
        return payload if isinstance(payload, dict) else {}, body
    data = {}
    for line in frontmatter.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"')
    return data, body


def extract_title(body: str, fallback: str) -> str:
    for line in body.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def classify_focus(description: str) -> str:
    lowered = description.lower()
    if any(token in lowered for token in ["review", "audit", "incident", "risk", "govern"]):
        return "quality-and-boundary"
    if any(token in lowered for token in ["export", "package", "adapter", "client", "portable"]):
        return "portability-and-contract"
    if any(token in lowered for token in ["workflow", "coordinate", "orchestrate", "process"]):
        return "execution-and-assets"
    return "trigger-and-output"


def build_questions(focus: str) -> list[dict]:
    base = [
        {
            "question": "What recurring job should this skill own every time?",
            "why": "This defines the core capability sentence and keeps the package from drifting.",
        },
        {
            "question": "What inputs will users actually hand to this skill?",
            "why": "Input shape decides whether references, scripts, or templates are needed.",
        },
        {
            "question": "What concrete outputs must the skill produce?",
            "why": "Outputs should drive the package structure before extra guidance is added.",
        },
        {
            "question": "Which near-neighbor requests should not trigger this skill?",
            "why": "The exclusion list is the fastest route to better trigger quality.",
        },
        {
            "question": "What constraints matter: privacy, naming, local fit, portability, or governance?",
            "why": "Constraints decide how much structure, packaging, and review the skill actually needs.",
        },
    ]
    if focus == "quality-and-boundary":
        base.append(
            {
                "question": "What failure would make this skill untrustworthy in practice?",
                "why": "The answer usually reveals the first evaluation gate worth adding.",
            }
        )
    elif focus == "portability-and-contract":
        base.append(
            {
                "question": "Which environments or clients must be able to consume this skill?",
                "why": "This sets the minimum metadata and degradation strategy.",
            }
        )
    else:
        base.append(
            {
                "question": "What repeated manual step should become a deterministic asset first?",
                "why": "This usually reveals whether a script or reference should be created next.",
            }
        )
    return base


def build_summary(skill_dir: Path) -> dict:
    skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    frontmatter, body = parse_frontmatter(skill_text)
    name = frontmatter.get("name", skill_dir.name)
    description = frontmatter.get("description", "No description found.")
    title = extract_title(body, name.replace("-", " ").title())
    focus = classify_focus(description)
    questions = build_questions(focus)
    output = {
        "capability_sentence": f"{title} should turn a recurring request into a reliable reusable output without widening the boundary unnecessarily.",
        "required_capture": [
            "recurring job",
            "real inputs",
            "required outputs",
            "exclusions",
            "constraints",
            "first evaluation target",
        ],
        "recommended_first_gate": "trigger and boundary" if focus != "portability-and-contract" else "portability and contract",
    }
    return {
        "skill_name": name,
        "title": title,
        "description": description,
        "focus": focus,
        "questions": questions,
        "output": output,
    }


def render_markdown(summary: dict) -> str:
    lines = [
        "# Intent Dialogue",
        "",
        f"Skill: `{summary['skill_name']}`",
        "",
        "## Why Start Here",
        "",
        "Use this short dialogue before deep authoring. The goal is to learn the real job, output, exclusions, and constraints so the first package is small but accurate.",
        "",
        "## Current Anchor",
        "",
        f"- Title: `{summary['title']}`",
        f"- Description: {summary['description']}",
        f"- Focus: `{summary['focus']}`",
        "",
        "## Questions To Ask",
        "",
    ]
    for idx, item in enumerate(summary["questions"], start=1):
        lines.extend(
            [
                f"{idx}. {item['question']}",
                f"   Why: {item['why']}",
            ]
        )
    lines.extend(
        [
            "",
            "## Capture Before Drafting",
            "",
            f"- Capability sentence: {summary['output']['capability_sentence']}",
            f"- Recommended first gate: `{summary['output']['recommended_first_gate']}`",
        ]
    )
    for item in summary["output"]["required_capture"]:
        lines.append(f"- Capture: `{item}`")
    return "\n".join(lines).strip() + "\n"


def render_intent_dialogue(skill_dir: Path, output_md: Path | None = None, output_json: Path | None = None) -> dict:
    skill_dir = skill_dir.resolve()
    reports_dir = skill_dir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_md = output_md or reports_dir / "intent-dialogue.md"
    output_json = output_json or reports_dir / "intent-dialogue.json"

    summary = build_summary(skill_dir)
    output_md.write_text(render_markdown(summary), encoding="utf-8")
    output_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "ok": True,
        "skill_dir": str(skill_dir),
        "artifacts": {
            "markdown": str(output_md),
            "json": str(output_json),
        },
        "summary": summary,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Render an intent dialogue guide for a skill package.")
    parser.add_argument("skill_dir", nargs="?", default=".")
    parser.add_argument("--output-md")
    parser.add_argument("--output-json")
    args = parser.parse_args()
    result = render_intent_dialogue(
        Path(args.skill_dir),
        output_md=Path(args.output_md).resolve() if args.output_md else None,
        output_json=Path(args.output_json).resolve() if args.output_json else None,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
