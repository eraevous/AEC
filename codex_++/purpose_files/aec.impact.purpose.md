# Module: aec.impact
@ai-path: aec.impact
@ai-source-file: src/aec/impact.py
@ai-role: analysis
@ai-intent: "Given change events, classify which conclusions are unjustified, weakened, stale, to rebaseline, exploratory or needing review"
@ai-version: 0.1.0
@schema-version: 0.3
@ai-generated: true
@ai-verified: false
@ai-dependencies: records

### Risks
- Deterministic structure only. It never judges whether evidence is good or a metric fits the purpose.
- Its output is only as good as the hand-written records; authoring cost is unmeasured.
