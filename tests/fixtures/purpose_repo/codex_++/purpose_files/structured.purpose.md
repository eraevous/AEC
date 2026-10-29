@ai-source-file: pkg/core.py
@ai-intent: Preserve contracts
@ai-role: parser
@ai-version: 1.2.0
@ai-risk-pii: low
@ai-dependencies: pkg.util
@ai-coordination: sequential
@ai-cadence: run
@ai-downstream: cli
@ai-unknown: keep this
@ai-role: reviewer

### 🎯 Intent & Responsibility
- Preserve this responsibility.
### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Brief Description | Extra |
| --- | --- | --- | --- | --- |
| 📥 In | data | `str` | raw data | retained |
| 📤 Out | result | `dict` | parsed result | also kept |
### 🗣 Dialogic Notes & Risks
- Unverified declarations.
### Dependencies & Coordination
- pkg.util
### 9. Pipeline Integration
- Called by cli.
#### Coordination Mechanics
- Sequential stages.
#### Integration Points
- Downstream report.
### Test Guarantees
- Keep records append-only.
