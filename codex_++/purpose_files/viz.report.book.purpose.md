@ai-path: viz.report.book
    
- @ai-source-file: src/viz/report/book.py
    
- @ai-role: visualization.orchestrator
    
- @ai-intent: "Orchestrate generation of the EDA visuals set and write an image manifest for panel review."
    
- @ai-version: 0.1.0
    
- @schema-version: 0.3
    
- @ai-risk-pii: none
    
- @ai-risk-performance: "Sequential rendering; offers sampling and subset switches for speed."
    
- @ai-dependencies: viz.readmit.sankey,viz.readmit.corrgram_3x3,viz.readmit.parallel_coords,viz.readmit.bars_hists,viz.readmit.boxplots,viz.readmit.small_multiples,viz.shared.theme
    
- @ai-used-by: cli.viz.readmit
    
- @ai-downstream: artifacts.manifests
    

## Module: viz.report.book

### 🎯 Intent & Responsibility

- Provide a single entrypoint to build all requested plots.

- Emit a JSON manifest mapping plot keys → file paths and brief notes.

- Handle modules emitting multiple artifacts per plot (e.g., grouped parallel coordinates HTML pages).
    

### 📥 Inputs & 📤 Outputs

|Direction|Name|Type|Description|
|---|---|---|---|
|📥 In|df|pandas.DataFrame|Cleaned dataset from user transforms|
|📥 In|config|Dict[str,Any]|Plot toggles, top-K, bin_specs, palette, output dir|
|📤 Out|manifest|Dict[str,Any]|Keys per module → export paths + computed tables/metrics references (values may be nested dicts for multi-artifact modules)|

### 🤝 Integration & Coordination

- Thin CLI wrapper `cli.viz.readmit` calls this orchestrator.
    
- Writes `artifacts/viz_manifest.json` for panel sharing.
    

### 🧪 Test Guarantees

- With a toy df, produces a manifest containing at least the required keys and writes ≥1 artifact per module.