 @ai-path: viz.readmit.sankey
    
- @ai-source-file: src/viz/readmit/sankey.py
    
- @ai-role: visualization.builder
    
- @ai-intent: "Build a Sankey diagram representing patient flows across Prior Admission → Primary Diagnosis → Discharge Status → 30-day Readmission."
    
- @ai-version: 0.1.0
    
- @schema-version: 0.3
    
- @ai-risk-pii: none
    
- @ai-risk-performance: "Aggregations over large frames; uses categorical compression and top-K bucketing to remain readable."
    
- @ai-dependencies: pandas,numpy,plotly,matplotlib,seaborn
    
- @ai-used-by: viz.report.book
    
- @ai-downstream: artifacts.images
    

## Module: viz.readmit.sankey

> Aggregate flows and render an interactive (Plotly) or static (Matplotlib) Sankey of key stages in the patient journey.

### 🎯 Intent & Responsibility

- Validate/standardize column names and category levels.

- Optionally bucket low-frequency categories into "Other" (configurable `min_count` or `top_k`).

- Compute node and link tables across the ordered stages.

- Render Plotly figure (preferred) with tooltips (counts, rates); optionally export static PNG/SVG.

- Tint nodes and ribbons using the readmission palette so flow color mirrors 30-day readmission propensity.
    

### 📥 Inputs & 📤 Outputs

|Direction|Name|Type|Description|
|---|---|---|---|
|📥 In|df|pandas.DataFrame|Must include: `Prior_Admission` (bool/int), `Primary_Diagnosis` (str/cat), `Discharge_Status` (str/cat), `Has_Readmission_30_Days` (bool/int)|
|📥 In|top_k|int|Top categories to keep per stage (default 10)|
|📥 In|min_count|int|Minimum frequency to avoid "Other" bin (default 25)|
|📥 In|palette|dict|Optional mapping `{category: color}`|
|📤 Out|figure|plotly.graph_objs.Figure|Sankey figure object|
|📤 Out|exports|Dict[str,str]|Saved files: `{"html": path?, "png": path?}`|
|📤 Out|data|Dict[str,pandas.DataFrame]|Node and link tables used to render (`nodes` adds `readmit_rate`, `links` adds `readmit_flag`)|

### 🔗 Dependencies

- Plot: Plotly (primary), Matplotlib fallback.
    
- Aggregation: pandas groupby.
    

### 🤝 Integration & Coordination

- Consumed by `viz.report.book` to embed visuals in the EDA deck.
    
- Shares palette with `viz.shared.theme` if available.
    

### ⚠️ Risks & Edge Cases

- High-cardinality diagnoses → enable `top_k`/`min_count` and label consolidation.
    
- Missing columns → raise `ValueError` listing requirements.
    

### 🧪 Test Guarantees

- With a 20-row toy frame, returns non-empty node/link tables and a Figure.
    
- Deterministic counts given fixed `top_k`/`min_count`.