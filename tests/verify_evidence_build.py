#!/usr/bin/env python3
"""Behavior tests for isolated evidence runs and immutable publishing."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from evidence_resolver import resolve_evidence_path  # noqa: E402
from evidence_store import EvidenceError, EvidenceStore  # noqa: E402


def write_skill(root: Path, name: str, marker: str) -> None:
    (root / "reports").mkdir(parents=True)
    (root / "agents").mkdir()
    (root / "SKILL.md").write_text(
        f'---\nname: {name}\ndescription: "Generate {name} evidence."\n---\n\n# {name}\n',
        encoding="utf-8",
    )
    (root / "agents" / "interface.yaml").write_text("interface:\n  display_name: Demo\n", encoding="utf-8")
    (root / "manifest.json").write_text(
        json.dumps({"name": name, "version": "1.0.0", "updated_at": "2026-08-12"}),
        encoding="utf-8",
    )
    (root / "reports" / "quality.json").write_text(json.dumps({"marker": marker}), encoding="utf-8")
    (root / ".gitignore").write_text(".yao/\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "Evidence Test"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "evidence@example.test"], cwd=root, check=True)
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(["git", "commit", "-qm", "fixture"], cwd=root, check=True)


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="yao-evidence-") as temp:
        temp_root = Path(temp)
        alpha = temp_root / "alpha-skill"
        beta = temp_root / "beta-skill"
        alpha.mkdir()
        beta.mkdir()
        write_skill(alpha, "alpha-skill", "alpha-v1")
        write_skill(beta, "beta-skill", "beta-v1")

        alpha_store = EvidenceStore(alpha)
        beta_store = EvidenceStore(beta)
        alpha_run = alpha_store.build("alpha-run")
        beta_run = beta_store.build("beta-run")
        assert alpha_run.run_dir.parent == (alpha / ".yao" / "runs").resolve(), alpha_run
        assert beta_run.run_dir.parent == (beta / ".yao" / "runs").resolve(), beta_run
        assert alpha_run.manifest["skill_name"] == "alpha-skill", alpha_run.manifest
        assert beta_run.manifest["skill_name"] == "beta-skill", beta_run.manifest

        try:
            alpha_store.build("../escape")
        except EvidenceError as exc:
            assert exc.code == "invalid-run-id", exc
        else:
            raise AssertionError("path traversal run id was accepted")

        outside = temp_root / "outside.json"
        outside.write_text("{}", encoding="utf-8")
        (alpha / "reports" / "escape.json").symlink_to(outside)
        try:
            alpha_store.build("symlink-run")
        except EvidenceError as exc:
            assert exc.code == "unsafe-artifact", exc
        else:
            raise AssertionError("symlink artifact was accepted")
        (alpha / "reports" / "escape.json").unlink()

        first_release = alpha_store.publish(alpha_run)
        pointer = json.loads((alpha / "reports" / ".current-run.json").read_text(encoding="utf-8"))
        assert pointer["run_id"] == "alpha-run", pointer
        assert first_release == (alpha / ".yao" / "releases" / "alpha-run").resolve(), first_release
        assert json.loads((alpha / "reports" / "quality.json").read_text(encoding="utf-8"))["marker"] == "alpha-v1"
        subprocess.run(["git", "add", "reports/.current-run.json", "reports/artifact-index.json"], cwd=alpha, check=True)
        subprocess.run(["git", "commit", "-qm", "publish pointer"], cwd=alpha, check=True)
        try:
            alpha_store.publish(alpha_run)
        except EvidenceError as exc:
            assert exc.code == "immutable-release-exists", exc
        else:
            raise AssertionError("immutable release was overwritten")

        tampered = alpha_run.run_dir / "artifacts" / "reports" / "quality.json"
        tampered.write_text(json.dumps({"marker": "tampered"}), encoding="utf-8")
        try:
            alpha_store.verify_run(alpha_run.run_dir)
        except EvidenceError as exc:
            assert exc.code == "artifact-hash-mismatch", exc
        else:
            raise AssertionError("tampered run passed verification")

        (alpha / "reports" / "quality.json").write_text(json.dumps({"marker": "alpha-v2"}), encoding="utf-8")
        subprocess.run(["git", "add", "reports/quality.json"], cwd=alpha, check=True)
        subprocess.run(["git", "commit", "-qm", "new evidence"], cwd=alpha, check=True)
        second_run = alpha_store.build("alpha-run-2")
        try:
            alpha_store.publish(second_run, crash_at="after-mirrors")
        except RuntimeError as exc:
            assert "simulated publish crash" in str(exc), exc
        else:
            raise AssertionError("publish crash point did not fire")
        assert (alpha / ".yao" / "publish-transaction.json").exists()
        alpha_store.recover()
        restored = json.loads((alpha / "reports" / "quality.json").read_text(encoding="utf-8"))
        assert restored["marker"] == "alpha-v1", restored
        assert not (alpha / ".yao" / "publish-transaction.json").exists()

        for crash_point in ("after-release", "before-pointer"):
            crash_skill = temp_root / f"crash-{crash_point}"
            crash_skill.mkdir()
            write_skill(crash_skill, crash_skill.name, "stable")
            crash_store = EvidenceStore(crash_skill)
            stable_run = crash_store.build("stable-run")
            crash_store.publish(stable_run)
            subprocess.run(
                ["git", "add", "reports/.current-run.json", "reports/artifact-index.json"],
                cwd=crash_skill,
                check=True,
            )
            subprocess.run(["git", "commit", "-qm", "publish pointer"], cwd=crash_skill, check=True)
            (crash_skill / "reports" / "quality.json").write_text(json.dumps({"marker": "candidate"}), encoding="utf-8")
            subprocess.run(["git", "add", "reports/quality.json"], cwd=crash_skill, check=True)
            subprocess.run(["git", "commit", "-qm", "candidate evidence"], cwd=crash_skill, check=True)
            candidate_run = crash_store.build("candidate-run")
            try:
                crash_store.publish(candidate_run, crash_at=crash_point)
            except RuntimeError:
                pass
            else:
                raise AssertionError(f"{crash_point} crash point did not fire")
            assert crash_store.recover() is True
            restored_payload = json.loads((crash_skill / "reports" / "quality.json").read_text(encoding="utf-8"))
            assert restored_payload["marker"] == "stable", (crash_point, restored_payload)

        with beta_store.publish_lock():
            try:
                with beta_store.publish_lock():
                    raise AssertionError("second publisher acquired an active lock")
            except EvidenceError as exc:
                assert exc.code == "publish-locked", exc

        dry = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "yao.py"), "evidence-build", str(beta), "--run-id", "cli-dry"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        assert dry.returncode == 0, dry.stderr or dry.stdout
        dry_payload = json.loads(dry.stdout)
        assert dry_payload["mode"] == "dry-run", dry_payload
        assert not (beta / "reports" / ".current-run.json").exists()
        publish = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "yao.py"),
                "evidence-build",
                str(beta),
                "--run-id",
                "cli-publish",
                "--publish",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        assert publish.returncode == 0, publish.stderr or publish.stdout
        assert json.loads(publish.stdout)["mode"] == "published", publish.stdout
        subprocess.run(["git", "add", "reports/.current-run.json", "reports/artifact-index.json"], cwd=beta, check=True)
        subprocess.run(["git", "commit", "-qm", "publish cli pointer"], cwd=beta, check=True)
        resolved_quality = resolve_evidence_path(beta, "reports/quality.json")
        assert ".yao/releases/cli-publish/" in resolved_quality.as_posix(), resolved_quality
        assert json.loads(resolved_quality.read_text(encoding="utf-8"))["marker"] == "beta-v1"
        (beta / "SKILL.md").write_text((beta / "SKILL.md").read_text(encoding="utf-8") + "\nDirty.\n", encoding="utf-8")
        rejected = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "yao.py"),
                "evidence-build",
                str(beta),
                "--run-id",
                "dirty-publish",
                "--publish",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        assert rejected.returncode == 2, rejected.stdout
        assert json.loads(rejected.stdout)["error"]["code"] == "dirty-worktree", rejected.stdout

    print(json.dumps({"ok": True}, indent=2))


if __name__ == "__main__":
    main()
