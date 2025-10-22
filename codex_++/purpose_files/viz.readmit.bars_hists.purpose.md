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

- For categorical cols: countplot normalized within readmission with CI bands.
    
- For numeric cols: histogram/KDE split by readmission.
    
- Auto-layout small multiples across selected columns.
    

### 📥 Inputs & 📤 Outputs

|Direction|Name|Type|Description|
|---|---|---|---|
|📥 In|df|pandas.DataFrame|Mixed types + `Has_Readmission_30_Days`|
|📥 In|categoricals|List[str]|Categorical columns to plot|
|📥 In|numerics|List[str]|Numeric columns to plot|
|📤 Out|figure|matplotlib.figure.Figure|Grid of panels|
|📤 Out|summary|pandas.DataFrame|Rates per bin/category|
