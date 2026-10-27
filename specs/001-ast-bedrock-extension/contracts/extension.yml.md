# Extension manifest contract (Spec Kit v1.2.3 schema 1.0)

```yaml
schema_version: "1.0"
extension: {id: aec, name: "AEC: purpose, authority & change impact", version: 0.2.0, ...}
requires: {speckit_version: ">=1.2.0"}
provides:
  commands:
    - {name: speckit.aec.purpose-link, file: commands/speckit.aec.purpose-link.md}
    - {name: speckit.aec.check,        file: commands/speckit.aec.check.md}
    - {name: speckit.aec.impact,       file: commands/speckit.aec.impact.md}
hooks:
  after_specify:   {command: speckit.aec.purpose-link, optional: true}
  after_tasks:     {command: speckit.aec.check,        optional: true}
  after_implement: {command: speckit.aec.impact,       optional: true}
```
Invariant: no command writes `spec.md`, `plan.md`, `tasks.md` or the constitution. Each one prints a findings report.
