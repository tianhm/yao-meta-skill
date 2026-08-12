#!/usr/bin/env python3
"""Build an isolated evidence run and optionally publish it transactionally."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from evidence_store import EvidenceError, EvidenceStore


def main() -> None:
    parser = argparse.ArgumentParser(description="Build isolated, hash-indexed evidence for an agent skill.")
    parser.add_argument("skill_dir")
    parser.add_argument("--run-id")
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()

    try:
        store = EvidenceStore(Path(args.skill_dir))
        recovered = store.recover()
        run = store.build(args.run_id)
        release = store.publish(run) if args.publish else None
        payload = {
            "ok": True,
            "mode": "published" if release else "dry-run",
            "run_id": run.run_id,
            "skill_name": run.manifest["skill_name"],
            "run_dir": str(run.run_dir),
            "artifact_count": run.manifest["artifact_count"],
            "release_dir": str(release) if release else None,
            "recovered_previous_publish": recovered,
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    except EvidenceError as exc:
        print(
            json.dumps(
                {"ok": False, "error": {"code": exc.code, "message": str(exc)}},
                ensure_ascii=False,
                indent=2,
            )
        )
        raise SystemExit(2)


if __name__ == "__main__":
    main()
