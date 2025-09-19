# @codex-role: architect
# @codex-objective: module contract for drift detection

- @ai-path: core.driftdiff
- @ai-source-file: src/core/driftdiff.py
- @ai-role: drift_detector
- @ai-intent: "Compare AST IO signatures vs .purpose.md contracts and flag mismatches"
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false

### 🎯 Responsibilities
- Parse module AST
- Compare function/class signatures with `.purpose.md`
- Output structured report of drift

### 📥 Inputs
- path: str → Python file to inspect
- contract: dict → expected IO schema from `.purpose.md`

### 📤 Outputs
- report: dict { "matches": [...], "mismatches": [...], "missing": [...] }
