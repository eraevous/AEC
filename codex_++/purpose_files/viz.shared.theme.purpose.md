@ai-path: viz.shared.theme
    
- @ai-source-file: src/viz/shared/theme.py
    
- @ai-role: analysis.utility
    
- @ai-intent: "Centralize plot styles, palettes, annotations, and saving/export helpers."
    
- @ai-version: 0.1.0
    
- @schema-version: 0.3
    
- @ai-risk-pii: none
    
- @ai-risk-performance: "Negligible."
    
- @ai-dependencies: matplotlib,seaborn,typing
    
- @ai-used-by: viz.readmit.*
    
- @ai-downstream: viz.report.book
    

## Module: viz.shared.theme

### 🎯 Intent & Responsibility

- Provide hospital-safe palettes and color for readmission (`0/1`).
    
- Title/subtitle/caption helpers with base-rate annotation.
    
- `save_figure(fig, name, formats=["png","svg"], dpi=300)` to standardize exports.
    

### 📥 Inputs & 📤 Outputs

|Direction|Name|Type|Description|
|---|---|---|---|
|📥 In|fig|matplotlib.figure.Figure|Target figure to style/save|
|📥 In|name|str|Basename for export|
|📤 Out|paths|Dict[str,str]|Written artifact paths per format|
