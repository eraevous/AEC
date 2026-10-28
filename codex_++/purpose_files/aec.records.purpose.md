# Module: aec.records
@ai-path: aec.records
@ai-source-file: src/aec/records.py
@ai-role: store_and_checker
@ai-intent: "Load versioned reasoning records and run deterministic cross-record checks (references, authority, evidence tiers)"
@ai-version: 0.1.0
@schema-version: 0.3
@ai-generated: true
@ai-verified: false
@ai-dependencies: none

### Risks
- Deterministic structure only. It never judges whether evidence is good or a metric fits the purpose.
- Its output is only as good as the hand-written records; authoring cost is unmeasured.
