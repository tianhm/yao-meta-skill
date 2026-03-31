#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


TEXT_EXTS = {".md", ".txt", ".yaml", ".yml", ".json", ".py", ".sh", ".js", ".ts"}


def estimate_tokens(text: str) -> int:
    # Fast heuristic suitable for local gating.
    return max(1, len(text) // 4)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="ignore")


def classify(path: Path) -> str:
    parts = set(path.parts)
    if path.name == "SKILL.md":
        return "skill_body"
    if "references" in parts:
        return "reference"
    if "scripts" in parts:
        return "script"
    if "assets" in parts:
        return "asset"
    if path.suffix in TEXT_EXTS:
        return "other_text"
    return "binary_or_other"


def summarize(skill_dir: Path) -> dict:
    files = []
    total_tokens = 0
    initial_tokens = 0
    for path in sorted(skill_dir.rglob("*")):
        if not path.is_file():
            continue
        kind = classify(path)
        if kind in {"binary_or_other", "asset"} and path.suffix not in TEXT_EXTS:
            size = path.stat().st_size
            files.append({"path": str(path.relative_to(skill_dir)), "kind": kind, "bytes": size})
            continue
        text = read_text(path)
        tokens = estimate_tokens(text)
        record = {
            "path": str(path.relative_to(skill_dir)),
            "kind": kind,
            "chars": len(text),
            "estimated_tokens": tokens,
        }
        files.append(record)
        total_tokens += tokens
        if kind in {"skill_body", "other_text"}:
            initial_tokens += tokens
    return {
        "skill_dir": str(skill_dir),
        "estimated_initial_load_tokens": initial_tokens,
        "estimated_total_text_tokens": total_tokens,
        "warning": initial_tokens > 2000,
        "files": files,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Estimate context size for a skill package.")
    parser.add_argument("skill_dir", help="Path to the skill directory")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    args = parser.parse_args()

    report = summarize(Path(args.skill_dir).resolve())
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return

    print(f"Skill: {report['skill_dir']}")
    print(f"Estimated initial-load tokens: {report['estimated_initial_load_tokens']}")
    print(f"Estimated total text tokens: {report['estimated_total_text_tokens']}")
    print(f"Initial-load warning (>2000): {'YES' if report['warning'] else 'NO'}")
    print("")
    for file in report["files"]:
        if "estimated_tokens" in file:
            print(f"{file['kind']:12} {file['estimated_tokens']:6}t  {file['path']}")
        else:
            print(f"{file['kind']:12} {file['bytes']:6}b  {file['path']}")


if __name__ == "__main__":
    main()
