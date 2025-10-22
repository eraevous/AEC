@ai-path: viz.readmit.corrgram_3x3
    
- @ai-source-file: src/viz/readmit/corrgram_3x3.py
    
- @ai-role: visualization.builder
    
- @ai-intent: "Produce a 3×3 corrgram: lower-left scatter matrix colored by readmission, diagonal distributions split by readmission, and upper-right cells with pairwise association metrics."
    
- @ai-version: 0.1.0
    
- @schema-version: 0.3
    
- @ai-risk-pii: none
    
- @ai-risk-performance: "Pairwise computations O(p²) on selected variables; sample or blur for very large N."
    
- @ai-dependencies: pandas,numpy,matplotlib,seaborn,scipy,statsmodels,sklearn
    
- @ai-used-by: viz.report.book
    
- @ai-downstream: artifacts.images
    

## Module: viz.readmit.corrgram_3x3

> Flexible grid comparing up to 3 numeric variables at a time across readmission status.

### 🎯 Intent & Responsibility

- Accept a column config (exact 3 numerics) and `readmit_col`.
    
- Lower-left: scatter with optional smoothing contours; hue by readmission.
    
- Diagonal: KDE/Histogram per readmission.
    
- Upper-right: text tiles showing Pearson/Spearman/Kendall for numeric pairs and point-biserial / AUC vs readmission for each numeric.
    

### 📥 Inputs & 📤 Outputs

|Direction|Name|Type|Description|
|---|---|---|---|
|📥 In|df|pandas.DataFrame|Includes the 3 numeric columns and `readmit_col`|
|📥 In|numerics|List[str]|Exactly three numeric column names|
|📥 In|readmit_col|str|Binary/boolean/int indicator|
|📥 In|sample|int\|None|Optional row sample for speed (default None)|
|📤 Out|figure|matplotlib.figure.Figure|3×3 grid figure|
|📤 Out|metrics|pandas.DataFrame|Rows per cell with computed statistics|

### 🤝 Integration & Coordination

- Metrics table can be exported and referenced in the report appendix.
    
- Shares bins & aesthetics with `viz.shared.theme`.
    

### ⚠️ Risks & Edge Cases

- Non-numeric columns in `numerics` → coercion attempt then fail with clear error.
    
- Severe class imbalance → annotate base rate on figure.
    

### 🧪 Test Guarantees

- Deterministic metric values with fixed seed and no sampling.
    
- Handles N<50 without crashing (falls back to hist over KDE).
    