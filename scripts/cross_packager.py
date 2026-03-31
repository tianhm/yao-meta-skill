#!/usr/bin/env python3
import argparse
import json
import shutil
import zipfile
from pathlib import Path


def read_simple_yaml(path: Path) -> dict:
    lines = path.read_text(encoding="utf-8").splitlines()
    data: dict = {}
    stack: list[tuple[int, dict]] = [(0, data)]
    for raw_line in lines:
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()
        while len(stack) > 1 and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        if line.startswith("- "):
            item = line[2:].strip().strip("'\"")
            existing = parent.setdefault("__list__", [])
            existing.append(item)
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value == "":
            child: dict = {}
            parent[key] = child
            stack.append((indent, child))
        else:
            parent[key] = value.strip("'\"")
    return data


def read_frontmatter(skill_md: Path) -> dict:
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    data = {}
    for line in parts[1].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip("'\"")
    return data


def read_interface(skill_dir: Path) -> dict:
    path = skill_dir / "agents" / "interface.yaml"
    if not path.exists():
        return {}
    raw = read_simple_yaml(path)
    compatibility = raw.get("compatibility", {})
    targets = compatibility.get("adapter_targets", {})
    if isinstance(targets, dict) and "__list__" in targets:
        compatibility["adapter_targets"] = targets["__list__"]
    raw["compatibility"] = compatibility
    return raw


def build_manifest(skill_dir: Path, platform: str) -> dict:
    frontmatter = read_frontmatter(skill_dir / "SKILL.md")
    interface = read_interface(skill_dir).get("interface", {})
    compatibility = read_interface(skill_dir).get("compatibility", {})
    return {
        "name": frontmatter.get("name", skill_dir.name),
        "description": frontmatter.get("description", ""),
        "version": frontmatter.get("version", "1.0.0"),
        "platform": platform,
        "skill_root": skill_dir.name,
        "display_name": interface.get("display_name", skill_dir.name),
        "short_description": interface.get("short_description", ""),
        "default_prompt": interface.get("default_prompt", ""),
        "canonical_metadata": "agents/interface.yaml",
        "adapter_targets": compatibility.get("adapter_targets", []),
    }


def write_yaml_like(path: Path, payload: dict) -> None:
    interface = payload.get("interface", {})
    lines = ["interface:"]
    for key in ("display_name", "short_description", "default_prompt"):
        value = interface.get(key, "")
        lines.append(f'  {key}: "{value}"')
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_adapter(skill_dir: Path, out_dir: Path, platform: str) -> Path:
    target_dir = out_dir / "targets" / platform
    target_dir.mkdir(parents=True, exist_ok=True)
    payload = build_manifest(skill_dir, platform)
    if platform == "openai":
        meta_dir = target_dir / "agents"
        meta_dir.mkdir(parents=True, exist_ok=True)
        write_yaml_like(
            meta_dir / "openai.yaml",
            {
                "interface": {
                    "display_name": payload["display_name"],
                    "short_description": payload["short_description"],
                    "default_prompt": payload["default_prompt"],
                }
            },
        )
        payload["install_hint"] = f"Use the packaged skill and include targets/openai/agents/openai.yaml when the client expects OpenAI-style interface metadata."
    elif platform == "claude":
        notes = target_dir / "README.md"
        notes.write_text(
            f"# Claude-Compatible Package\n\nUse `{skill_dir.name}` with its neutral source files. This target does not require vendor metadata by default.\n",
            encoding="utf-8",
        )
        payload["install_hint"] = f"Use the packaged skill directly; this target relies on SKILL.md and optional neutral metadata."
    else:
        payload["install_hint"] = f"Use {skill_dir.name} as an Agent Skills compatible package."
    path = target_dir / "adapter.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def make_zip(skill_dir: Path, out_dir: Path) -> Path:
    zip_path = out_dir / f"{skill_dir.name}.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in skill_dir.rglob("*"):
            if path.is_file():
                zf.write(path, arcname=str(path.relative_to(skill_dir.parent)))
    return zip_path


def copy_manifest(skill_dir: Path, out_dir: Path) -> Path:
    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(build_manifest(skill_dir, "generic"), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return manifest_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate lightweight cross-platform packaging artifacts.")
    parser.add_argument("skill_dir", help="Path to the skill directory")
    parser.add_argument("--platform", action="append", default=[], help="Target platform: openai, claude, generic")
    parser.add_argument("--output-dir", default="dist", help="Output directory")
    parser.add_argument("--zip", action="store_true", help="Create a zip package")
    args = parser.parse_args()

    skill_dir = Path(args.skill_dir).resolve()
    out_dir = Path(args.output_dir).resolve()
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    manifest = copy_manifest(skill_dir, out_dir)
    generated = [str(manifest)]
    for platform in (args.platform or ["generic"]):
        generated.append(str(write_adapter(skill_dir, out_dir, platform)))
    if args.zip:
        generated.append(str(make_zip(skill_dir, out_dir)))

    print(json.dumps({"output_dir": str(out_dir), "generated": generated}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
