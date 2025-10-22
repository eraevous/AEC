@ai-path: viz.readmit.parallel_coords
    
- @ai-source-file: src/viz/readmit/parallel_coords.py
    
- @ai-role: visualization.builder
    
- @ai-intent: "Render multiple parallel-coordinates views (raw, z-scored, rank-normalized) highlighting readmission patterns with optional faceting by diagnosis."
    
- @ai-version: 0.1.0
    
- @schema-version: 0.3
    
- @ai-risk-pii: none
    
- @ai-risk-performance: "Dense overplotting; uses opacity throttles and sampling."
    
- @ai-dependencies: pandas,numpy,matplotlib,plotly.express,sklearn
    
- @ai-used-by: viz.report.book
    
- @ai-downstream: artifacts.images
    

## Module: viz.readmit.parallel_coords

### 🎯 Intent & Responsibility

- Support numeric sets: LOS, Distance, Prior Admissions, # Comorbidities.
    
- Options for scaling: `raw|zscore|rank`.
    
- Color by readmission; facet by `Primary_Diagnosis` (top-K) if requested.
    

### 📥 Inputs & 📤 Outputs

|Direction|Name|Type|Description|
|---|---|---|---|
|📥 In|df|pandas.DataFrame|Numeric columns + `Has_Readmission_30_Days` + optional `Primary_Diagnosis`|
|📥 In|cols|List[str]|Numeric columns to include|
|📥 In|diagnosis_col|str|Default `Primary_Diagnosis`|
|📥 In|top_k_diag|int|Top diagnoses to facet (default 6)|
|📥 In|scaling|Literal["raw","zscore","rank"]|Axis transform|
|📤 Out|figure|plotly.graph_objs.Figure|Interactive parallel-coordinates|

### 🧪 Test Guarantees

- When `cols` has ≥3 numerics, returns a valid Figure with expected dimensions.