#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path


WORD_RE = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9_-]*")


def words(text: str) -> set[str]:
    return {w.lower() for w in WORD_RE.findall(text)}


def load_cases(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def extract_description(text: str) -> str:
    if not text.startswith("---"):
        return text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return text
    frontmatter = parts[1].splitlines()
    for line in frontmatter:
        if line.strip().startswith("description:"):
            return line.split(":", 1)[1].strip().strip("'\"")
    return text


def score_prompt(description_words: set[str], prompt: str) -> float:
    prompt_words = words(prompt)
    if not prompt_words:
        return 0.0
    overlap = description_words & prompt_words
    return len(overlap) / len(prompt_words)


def evaluate(description: str, cases: dict, threshold: float) -> dict:
    desc_words = words(description)
    results = {"should_trigger": [], "should_not_trigger": []}
    fp = 0
    fn = 0

    for bucket in ("should_trigger", "should_not_trigger"):
        for prompt in cases.get(bucket, []):
            score = score_prompt(desc_words, prompt)
            predicted = score >= threshold
            expected = bucket == "should_trigger"
            passed = predicted == expected
            if not passed and expected:
                fn += 1
            if not passed and not expected:
                fp += 1
            results[bucket].append(
                {
                    "prompt": prompt,
                    "score": round(score, 3),
                    "predicted_trigger": predicted,
                    "passed": passed,
                }
            )

    return {
        "threshold": threshold,
        "false_positives": fp,
        "false_negatives": fn,
        "results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Heuristic trigger quality evaluator.")
    parser.add_argument("--description", help="Description string to evaluate")
    parser.add_argument("--description-file", help="Read description text from file")
    parser.add_argument("--cases", required=True, help="JSON file with should_trigger and should_not_trigger arrays")
    parser.add_argument("--threshold", type=float, default=0.18, help="Token overlap threshold")
    args = parser.parse_args()

    description = args.description
    if args.description_file:
        description = extract_description(Path(args.description_file).read_text(encoding="utf-8"))
    if not description:
        raise SystemExit("Provide --description or --description-file")

    report = evaluate(description, load_cases(Path(args.cases)), args.threshold)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["false_positives"] > 2:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
