#!/usr/bin/env python3
"""Canonical Skill IR discovery, identity validation, and drift detection."""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


SCRIPT_INTERFACE = "internal-module"
SCRIPT_INTERFACE_REASON = "Imported by compiler, packager, registry, conformance, and report scripts to resolve one canonical Skill IR."

IR_SCHEMA_VERSION = "2.0.0"
REQUIRED_IR_FIELDS = {
    "schema_version",
    "name",
    "job_to_be_done",
    "trigger_surface",
    "workflow",
    "resources",
    "eval_plan",
    "risk",
    "governance",
}


class SkillIRResolutionError(RuntimeError):
    """Stable canonical-IR failure with a machine-readable code."""

    def __init__(self, code: str, message: str, *, path: Path | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.path = path


def display_path(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path.resolve())


def load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SkillIRResolutionError("invalid-json", f"Invalid Skill IR JSON at {path}: {exc}", path=path) from exc
    if not isinstance(payload, dict):
        raise SkillIRResolutionError("invalid-json-root", f"Skill IR root must be an object: {path}", path=path)
    return payload


def load_manifest(skill_dir: Path) -> dict[str, Any]:
    path = skill_dir / "manifest.json"
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SkillIRResolutionError("invalid-manifest", f"Invalid manifest JSON: {exc}", path=path) from exc
    return payload if isinstance(payload, dict) else {}


def read_frontmatter(skill_dir: Path) -> dict[str, Any]:
    path = skill_dir / "SKILL.md"
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8", errors="replace")
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    if yaml is not None:
        payload = yaml.safe_load(parts[1]) or {}
        return payload if isinstance(payload, dict) else {}
    data: dict[str, Any] = {}
    for line in parts[1].splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip().strip('"')
    return data


def normalize_description(value: Any) -> str:
    text = unicodedata.normalize("NFKC", str(value or ""))
    text = text.strip().strip('"').strip("'")
    return re.sub(r"\s+", " ", text).strip()


def _safe_manifest_source(skill_dir: Path, raw_source: str) -> Path:
    relative = Path(raw_source)
    if relative.is_absolute() or ".." in relative.parts:
        raise SkillIRResolutionError(
            "unsafe-manifest-source",
            f"manifest.skill_ir_source must stay inside the Skill root: {raw_source}",
        )
    candidate = skill_dir / relative
    if candidate.is_symlink():
        raise SkillIRResolutionError("unsafe-manifest-source", f"Skill IR source cannot be a symlink: {raw_source}")
    try:
        candidate.resolve().relative_to(skill_dir.resolve())
    except ValueError as exc:
        raise SkillIRResolutionError("unsafe-manifest-source", f"Skill IR source escapes the Skill root: {raw_source}") from exc
    return candidate


def _safe_default_source(skill_dir: Path, candidate: Path) -> Path:
    try:
        relative = candidate.relative_to(skill_dir)
    except ValueError as exc:
        raise SkillIRResolutionError("unsafe-ir-source", f"Skill IR source escapes the Skill root: {candidate}") from exc
    cursor = skill_dir
    for part in relative.parts:
        cursor /= part
        if cursor.is_symlink():
            raise SkillIRResolutionError("unsafe-ir-source", f"Skill IR source cannot traverse a symlink: {candidate}")
    try:
        candidate.resolve().relative_to(skill_dir.resolve())
    except ValueError as exc:
        raise SkillIRResolutionError("unsafe-ir-source", f"Skill IR source escapes the Skill root: {candidate}") from exc
    return candidate


def candidate_paths(skill_dir: Path, name: str) -> list[Path]:
    root = Path(skill_dir).resolve()
    if not name or name in {".", ".."} or Path(name).name != name or "/" in name or "\\" in name:
        raise SkillIRResolutionError("unsafe-skill-name", f"Unsafe Skill IR identity: {name}")
    manifest = load_manifest(root)
    candidates: list[Path] = []
    declared = manifest.get("skill_ir_source")
    if isinstance(declared, str) and declared.strip():
        candidates.append(_safe_manifest_source(root, declared.strip()))
    candidates.extend(
        [
            _safe_default_source(root, root / "reports" / "skill-ir.json"),
            _safe_default_source(root, root / "skill-ir" / "examples" / f"{name}.json"),
        ]
    )
    unique: list[Path] = []
    for path in candidates:
        if path not in unique:
            unique.append(path)
    return unique


def validate_identity(payload: dict[str, Any], skill_dir: Path, name: str, path: Path) -> None:
    missing = sorted(REQUIRED_IR_FIELDS - set(payload))
    if missing:
        raise SkillIRResolutionError(
            "schema-invalid",
            f"Skill IR is missing required fields at {display_path(path, skill_dir)}: {', '.join(missing)}",
            path=path,
        )
    if payload.get("schema_version") != IR_SCHEMA_VERSION:
        raise SkillIRResolutionError(
            "schema-mismatch",
            f"Skill IR schema must be {IR_SCHEMA_VERSION}: {display_path(path, skill_dir)}",
            path=path,
        )
    if str(payload.get("name", "")).strip() != name:
        raise SkillIRResolutionError(
            "name-mismatch",
            f"Skill IR name does not match {name}: {display_path(path, skill_dir)}",
            path=path,
        )
    trigger = payload.get("trigger_surface")
    if not isinstance(trigger, dict) or not normalize_description(trigger.get("description")):
        raise SkillIRResolutionError("schema-invalid", f"Skill IR trigger description is missing: {path}", path=path)
    frontmatter = read_frontmatter(skill_dir)
    frontmatter_description = normalize_description(frontmatter.get("description"))
    ir_description = normalize_description(trigger.get("description"))
    if frontmatter_description and ir_description != frontmatter_description:
        raise SkillIRResolutionError(
            "description-mismatch",
            f"Skill IR description drifted from SKILL.md: {display_path(path, skill_dir)}",
            path=path,
        )


def find_skill_ir_path(
    skill_dir: Path,
    name: str,
    *,
    require_schema: bool = False,
    fallback_source: str = "",
) -> str:
    return find_skill_ir(
        skill_dir,
        name,
        require_schema=require_schema,
        fallback_source=fallback_source,
    )[1]


def find_skill_ir(
    skill_dir: Path,
    name: str,
    *,
    require_schema: bool = False,
    fallback_source: str = "",
) -> tuple[dict[str, Any], str]:
    del require_schema  # Canonical IR always enforces the current schema.
    root = Path(skill_dir).resolve()
    manifest = load_manifest(root)
    declared = manifest.get("skill_ir_source")
    candidates = candidate_paths(root, name)
    for index, path in enumerate(candidates):
        if not path.exists():
            if index == 0 and isinstance(declared, str) and declared.strip():
                raise SkillIRResolutionError(
                    "declared-source-missing",
                    f"manifest.skill_ir_source does not exist: {declared}",
                    path=path,
                )
            continue
        if path.is_symlink():
            raise SkillIRResolutionError("unsafe-ir-source", f"Skill IR source cannot be a symlink: {path}", path=path)
        payload = load_json(path)
        validate_identity(payload, root, name, path)
        return payload, display_path(path, root)
    return {}, fallback_source
