#!/usr/bin/env python3
"""Isolated evidence runs, immutable bundles, and recoverable publishing."""

from __future__ import annotations

import contextlib
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator


SCRIPT_INTERFACE = "internal-module"
SCRIPT_INTERFACE_REASON = "Imported by evidence-build and evidence consumers for transactional local evidence publishing."

RUN_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
POINTER_PATH = Path("reports/.current-run.json")
CANONICAL_INDEX_PATH = Path("reports/artifact-index.json")
TRANSACTION_NAME = "publish-transaction.json"


class EvidenceError(RuntimeError):
    """Stable evidence failure with a machine-readable code."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class EvidenceRun:
    run_id: str
    run_dir: Path
    manifest: dict[str, Any]
    artifact_index: dict[str, Any]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
        temporary = Path(handle.name)
    os.replace(temporary, path)


def read_json(path: Path, *, code: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EvidenceError(code, f"Cannot read JSON artifact {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise EvidenceError(code, f"Expected a JSON object at {path}")
    return payload


class EvidenceStore:
    """Per-skill local evidence workspace and publication store."""

    def __init__(self, skill_dir: Path | str) -> None:
        self.skill_dir = Path(skill_dir).resolve()
        if not (self.skill_dir / "SKILL.md").is_file():
            raise EvidenceError("invalid-skill-dir", f"Missing SKILL.md in {self.skill_dir}")
        self.state_dir = self.skill_dir / ".yao"
        self.runs_dir = self.state_dir / "runs"
        self.releases_dir = self.state_dir / "releases"
        self.transaction_path = self.state_dir / TRANSACTION_NAME

    def _validate_run_id(self, run_id: str) -> str:
        if not RUN_ID_PATTERN.fullmatch(run_id):
            raise EvidenceError("invalid-run-id", "run id must match [A-Za-z0-9][A-Za-z0-9._-]{0,63}")
        return run_id

    def _default_run_id(self) -> str:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        return f"{stamp}-{uuid.uuid4().hex[:10]}"

    def _skill_name(self) -> str:
        manifest_path = self.skill_dir / "manifest.json"
        if manifest_path.exists():
            payload = read_json(manifest_path, code="invalid-manifest")
            if isinstance(payload.get("name"), str) and payload["name"].strip():
                return payload["name"].strip()
        return self.skill_dir.name

    def _git_state(self) -> dict[str, Any]:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=self.skill_dir,
            capture_output=True,
            text=True,
        )
        status = subprocess.run(
            ["git", "status", "--porcelain=v1", "--untracked-files=all"],
            cwd=self.skill_dir,
            capture_output=True,
            text=True,
        )
        return {
            "commit": commit.stdout.strip() if commit.returncode == 0 else None,
            "dirty": status.returncode != 0 or bool(status.stdout.strip()),
        }

    def assert_clean(self) -> None:
        state = self._git_state()
        if state["commit"] is None:
            raise EvidenceError("git-required", "publishing requires a Git worktree")
        if state["dirty"]:
            raise EvidenceError("dirty-worktree", "publishing requires a clean Git worktree")

    def _report_sources(self) -> list[Path]:
        reports_dir = self.skill_dir / "reports"
        if not reports_dir.is_dir():
            raise EvidenceError("missing-reports", f"Missing reports directory in {self.skill_dir}")
        sources: list[Path] = []
        excluded = {POINTER_PATH.name, CANONICAL_INDEX_PATH.name}
        for path in sorted(reports_dir.rglob("*")):
            if path.is_symlink():
                raise EvidenceError("unsafe-artifact", f"Symlink evidence artifacts are forbidden: {path}")
            if not path.is_file() or path.parent == reports_dir and path.name in excluded:
                continue
            try:
                path.resolve().relative_to(self.skill_dir)
            except ValueError as exc:
                raise EvidenceError("unsafe-artifact", f"Evidence artifact escapes the skill root: {path}") from exc
            sources.append(path)
        if not sources:
            raise EvidenceError("missing-artifacts", "No report artifacts are available to publish")
        return sources

    def build(self, run_id: str | None = None) -> EvidenceRun:
        selected_id = self._validate_run_id(run_id or self._default_run_id())
        self.runs_dir.mkdir(parents=True, exist_ok=True)
        run_dir = self.runs_dir / selected_id
        try:
            run_dir.mkdir()
        except FileExistsError as exc:
            raise EvidenceError("run-exists", f"Run already exists: {selected_id}") from exc
        artifacts_dir = run_dir / "artifacts"
        artifacts_dir.mkdir()
        entries: list[dict[str, Any]] = []
        for source in self._report_sources():
            relative = source.relative_to(self.skill_dir)
            destination = artifacts_dir / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            entries.append(
                {
                    "path": relative.as_posix(),
                    "sha256": sha256_file(destination),
                    "size": destination.stat().st_size,
                }
            )
        git_state = self._git_state()
        artifact_index = {
            "schema_version": "1.0",
            "run_id": selected_id,
            "skill_name": self._skill_name(),
            "artifacts": entries,
        }
        atomic_write_json(run_dir / "artifact-index.json", artifact_index)
        manifest = {
            "schema_version": "1.0",
            "run_id": selected_id,
            "skill_name": self._skill_name(),
            "created_at": utc_now(),
            "source": git_state,
            "artifact_count": len(entries),
            "artifact_index_sha256": sha256_file(run_dir / "artifact-index.json"),
            "status": "built",
        }
        atomic_write_json(run_dir / "run-manifest.json", manifest)
        return EvidenceRun(selected_id, run_dir, manifest, artifact_index)

    def add_json_artifact(self, run: EvidenceRun, relative_path: str | Path, payload: dict[str, Any]) -> EvidenceRun:
        verified = self.verify_run(run.run_dir)
        relative = Path(relative_path)
        if relative.is_absolute() or ".." in relative.parts or not relative.parts or relative.parts[0] != "reports":
            raise EvidenceError("unsafe-artifact", f"Run artifacts must stay under reports/: {relative}")
        destination = verified.run_dir / "artifacts" / relative
        atomic_write_json(destination, payload)
        entries = [item for item in verified.artifact_index["artifacts"] if item.get("path") != relative.as_posix()]
        entries.append(
            {
                "path": relative.as_posix(),
                "sha256": sha256_file(destination),
                "size": destination.stat().st_size,
            }
        )
        entries.sort(key=lambda item: str(item["path"]))
        artifact_index = dict(verified.artifact_index)
        artifact_index["artifacts"] = entries
        index_path = verified.run_dir / "artifact-index.json"
        atomic_write_json(index_path, artifact_index)
        manifest = dict(verified.manifest)
        manifest["artifact_count"] = len(entries)
        manifest["artifact_index_sha256"] = sha256_file(index_path)
        atomic_write_json(verified.run_dir / "run-manifest.json", manifest)
        return EvidenceRun(verified.run_id, verified.run_dir, manifest, artifact_index)

    def verify_run(self, run_dir: Path | str) -> EvidenceRun:
        resolved = Path(run_dir).resolve()
        try:
            resolved.relative_to(self.runs_dir.resolve())
        except ValueError as exc:
            raise EvidenceError("unsafe-run-path", f"Run is outside this skill: {resolved}") from exc
        manifest = read_json(resolved / "run-manifest.json", code="invalid-run-manifest")
        index_path = resolved / "artifact-index.json"
        artifact_index = read_json(index_path, code="invalid-artifact-index")
        if manifest.get("artifact_index_sha256") != sha256_file(index_path):
            raise EvidenceError("artifact-index-hash-mismatch", f"Artifact index was modified: {index_path}")
        run_id = str(manifest.get("run_id", ""))
        self._validate_run_id(run_id)
        if artifact_index.get("run_id") != run_id or manifest.get("skill_name") != self._skill_name():
            raise EvidenceError("run-identity-mismatch", "Run identity does not match the target skill")
        artifacts_root = resolved / "artifacts"
        for entry in artifact_index.get("artifacts", []):
            relative = Path(str(entry.get("path", "")))
            if relative.is_absolute() or ".." in relative.parts:
                raise EvidenceError("unsafe-artifact", f"Unsafe artifact path in index: {relative}")
            path = artifacts_root / relative
            if path.is_symlink() or not path.is_file():
                raise EvidenceError("unsafe-artifact", f"Missing or unsafe artifact: {relative}")
            if sha256_file(path) != entry.get("sha256"):
                raise EvidenceError("artifact-hash-mismatch", f"Artifact hash mismatch: {relative}")
        return EvidenceRun(run_id, resolved, manifest, artifact_index)

    @contextlib.contextmanager
    def publish_lock(self) -> Iterator[None]:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        lock_path = self.state_dir / "publish.lock"
        try:
            descriptor = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError as exc:
            raise EvidenceError("publish-locked", f"Another evidence publish holds {lock_path}") from exc
        try:
            os.write(descriptor, f"pid={os.getpid()}\n".encode())
            os.close(descriptor)
            yield
        finally:
            with contextlib.suppress(FileNotFoundError):
                lock_path.unlink()

    def _restore_bundle(self, bundle_dir: Path, *, expected_index_sha256: str | None = None) -> None:
        index_path = bundle_dir / "artifact-index.json"
        if expected_index_sha256 and sha256_file(index_path) != expected_index_sha256:
            raise EvidenceError("release-hash-mismatch", "Immutable release artifact index was modified")
        index = read_json(index_path, code="invalid-artifact-index")
        artifacts_root = (bundle_dir / "artifacts").resolve()
        for entry in index.get("artifacts", []):
            relative = Path(str(entry["path"]))
            if relative.is_absolute() or ".." in relative.parts or not relative.parts or relative.parts[0] != "reports":
                raise EvidenceError("unsafe-artifact", f"Unsafe release artifact path: {relative}")
            source = bundle_dir / "artifacts" / relative
            try:
                source.resolve().relative_to(artifacts_root)
            except ValueError as exc:
                raise EvidenceError("unsafe-artifact", f"Release artifact escapes its bundle: {relative}") from exc
            if source.is_symlink() or not source.is_file() or sha256_file(source) != entry.get("sha256"):
                raise EvidenceError("release-hash-mismatch", f"Immutable release is invalid: {relative}")
            destination = self.skill_dir / relative
            cursor = self.skill_dir
            for part in relative.parts:
                cursor /= part
                if cursor.is_symlink():
                    raise EvidenceError("unsafe-artifact", f"Canonical artifact path contains a symlink: {relative}")
            try:
                destination.resolve(strict=False).relative_to(self.skill_dir)
            except ValueError as exc:
                raise EvidenceError("unsafe-artifact", f"Canonical artifact escapes the skill root: {relative}") from exc
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        atomic_write_json(self.skill_dir / CANONICAL_INDEX_PATH, index)

    def recover(self) -> bool:
        if not self.transaction_path.exists():
            return False
        pointer_path = self.skill_dir / POINTER_PATH
        if not pointer_path.exists():
            raise EvidenceError("recovery-pointer-missing", "Cannot recover publish without the previous release pointer")
        pointer = read_json(pointer_path, code="invalid-current-run")
        previous = self.skill_dir / str(pointer.get("release_dir", ""))
        try:
            previous.resolve().relative_to(self.releases_dir.resolve())
        except ValueError as exc:
            raise EvidenceError("unsafe-release-path", "Current release pointer escapes .yao/releases") from exc
        self._restore_bundle(previous, expected_index_sha256=str(pointer.get("artifact_index_sha256", "")) or None)
        self.transaction_path.unlink()
        return True

    def _simulate_crash(self, crash_at: str | None, point: str) -> None:
        if crash_at == point:
            raise RuntimeError(f"simulated publish crash at {point}")

    def publish(self, run: EvidenceRun, *, crash_at: str | None = None) -> Path:
        verified = self.verify_run(run.run_dir)
        self.assert_clean()
        with self.publish_lock():
            self.assert_clean()
            self.recover()
            release_dir = self.releases_dir / verified.run_id
            if release_dir.exists():
                raise EvidenceError("immutable-release-exists", f"Immutable release already exists: {verified.run_id}")
            self.releases_dir.mkdir(parents=True, exist_ok=True)
            transaction = {
                "schema_version": "1.0",
                "run_id": verified.run_id,
                "started_at": utc_now(),
                "previous_pointer": POINTER_PATH.as_posix() if (self.skill_dir / POINTER_PATH).exists() else None,
            }
            atomic_write_json(self.transaction_path, transaction)
            release_dir.mkdir()
            shutil.copy2(verified.run_dir / "run-manifest.json", release_dir / "run-manifest.json")
            shutil.copy2(verified.run_dir / "artifact-index.json", release_dir / "artifact-index.json")
            shutil.copytree(verified.run_dir / "artifacts", release_dir / "artifacts")
            self._simulate_crash(crash_at, "after-release")
            self._restore_bundle(release_dir)
            self._simulate_crash(crash_at, "after-mirrors")
            self._simulate_crash(crash_at, "before-pointer")
            pointer = {
                "schema_version": "1.0",
                "run_id": verified.run_id,
                "skill_name": verified.manifest["skill_name"],
                "release_dir": release_dir.relative_to(self.skill_dir).as_posix(),
                "artifact_index": CANONICAL_INDEX_PATH.as_posix(),
                "artifact_index_sha256": sha256_file(release_dir / "artifact-index.json"),
                "published_at": utc_now(),
            }
            atomic_write_json(self.skill_dir / POINTER_PATH, pointer)
            self.transaction_path.unlink()
            return release_dir
