# Trusted Evidence Publication

`evidence-build` gives every Skill its own local run and release store. The store is rooted at the target Skill, so one Skill cannot reuse another Skill's run id, lock, artifacts, or release pointer.

## Build and publish

```bash
python3 scripts/yao.py evidence-build <skill_dir>
python3 scripts/yao.py evidence-build <skill_dir> --run-id <id> --publish
```

The default command is a dry run. It copies current report artifacts into `.yao/runs/<run-id>/artifacts`, writes a run manifest, and creates a SHA-256 artifact index. Publishing requires a clean Git worktree. A successful publish creates `.yao/releases/<run-id>`, refreshes canonical report mirrors, writes `reports/artifact-index.json`, and updates `reports/.current-run.json` last.

Release bundle directories are immutable. Reusing a published run id is an error. Run ids accept letters, numbers, dots, underscores, and hyphens; absolute paths, parent traversal, symlink artifacts, and indexed paths outside the Skill root are rejected.

## Consumer contract

Official report consumers resolve report JSON through `scripts/evidence_resolver.py`. The resolver verifies the current artifact index and the selected artifact hash. A clean source checkout reads the immutable release bundle. A dirty authoring checkout reads its canonical candidate reports until they are committed and published. A packaged installation without `.yao/releases` reads the canonical report mirror and applies the same hash check.

## Crash recovery

Publishing writes `.yao/publish-transaction.json` before canonical mirrors change. If the process stops after creating a release or while refreshing mirrors, the next `evidence-build` restores canonical mirrors from the release named by the previous pointer. The transaction marker is removed after recovery. The incomplete release may remain as an immutable, unreferenced bundle for audit and can never replace the current pointer implicitly.

Recovery failures are terminal. Preserve `.yao`, `reports/.current-run.json`, and `reports/artifact-index.json`, then inspect the error code and hashes before another publish attempt.
