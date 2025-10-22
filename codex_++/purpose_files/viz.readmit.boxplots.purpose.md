@ai-path: viz.readmit.boxplots
    
- @ai-source-file: src/viz/readmit/boxplots.py
    
- @ai-role: visualization.builder
    
- @ai-intent: "Boxplots and violin plots of numeric features vs readmission with robust stats overlays."
    
- @ai-version: 0.1.0
    
- @schema-version: 0.3
    
- @ai-risk-pii: none
    
- @ai-risk-performance: "Fast; seaborn-based."
    
- @ai-dependencies: pandas,seaborn,matplotlib,numpy,scipy
    
- @ai-used-by: viz.report.book
    
- @ai-downstream: artifacts.images
    

## Module: viz.readmit.boxplots

### 🎯 Intent & Responsibility

- For each numeric: draw box/violin split by readmission.
    
- Overlay median, IQR whiskers, and annotate effect size (Cliff’s delta or Cohen’s d) and p-value.
    

### 📥 Inputs & 📤 Outputs

|Direction|Name|Type|Description|
|---|---|---|---|
|📥 In|df|pandas.DataFrame|Must include numerics + `Has_Readmission_30_Days`|
|📥 In|numerics|List[str]|Numeric columns|
|📤 Out|figure|matplotlib.figure.Figure|Grid of boxes/violins|
|📤 Out|stats|pandas.DataFrame|Per-feature effect size + significance|
