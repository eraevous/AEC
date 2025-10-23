# @codex-role: architect
# @codex-objective: generate or upgrade `.purpose.md` with:
# - output schema
# - coordination logic
# - integration points
# - ecosystem anchoring
# Follow AGENTS.md G-10 and Section 9 enrichment instructions.

@ai-path: viz.readmit.bars_hists
    
- @ai-source-file: src/viz/readmit/bars_hists.py
    
- @ai-role: visualization.builder
    
- @ai-intent: "Generate bar charts and histograms grouped by readmission status with class-rate annotations."
    
- @ai-version: 0.1.0
    
- @schema-version: 0.3
    
- @ai-risk-pii: none
    
- @ai-risk-performance: "Fast; pure pandas/seaborn."
    
- @ai-dependencies: pandas,matplotlib,seaborn
    
- @ai-used-by: viz.report.book
    
- @ai-downstream: artifacts.images
    

## Module: viz.readmit.bars_hists

### 🎯 Intent & Responsibility

- For categorical columns, render paired clustered and stacked bar charts split by readmission status.

- For numeric columns, render paired overlaid density histograms and stacked count histograms split by readmission status.

- Annotate every panel with cohort base-rate context and align palette ordering across variants.

- Auto-layout one row per feature with two panels (clustered vs. stacked) so comparisons stay localized.
    

### 📥 Inputs & 📤 Outputs

|Direction|Name|Type|Description|
|---|---|---|---|
|📥 In|df|pandas.DataFrame|Mixed types + `Has_Readmission_30_Days`|
|📥 In|categoricals|List[str]|Categorical columns to plot|
|📥 In|numerics|List[str]|Numeric columns to plot|
|📤 Out|figure|matplotlib.figure.Figure|Grid of panels|
|📤 Out|summary|pandas.DataFrame|Rates per bin/category with `viz_type` column (`bar_clustered`, `bar_stacked`, `hist_overlaid`, `hist_stacked`)|
