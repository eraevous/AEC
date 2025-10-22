@ai-path: viz.readmit.small_multiples
    
- @ai-source-file: src/viz/readmit/small_multiples.py
    
- @ai-role: visualization.builder
    
- @ai-intent: "Create small-multiple panels by diagnosis for bubbles, heatmaps, and mosaic plots colored by average or total readmissions."
    
- @ai-version: 0.1.0
    
- @schema-version: 0.3
    
- @ai-risk-pii: none
    
- @ai-risk-performance: "Can be heavy with many diagnoses; uses top-K and facet pagination."
    
- @ai-dependencies: pandas,numpy,seaborn,matplotlib,statsmodels
    
- @ai-used-by: viz.report.book
    
- @ai-downstream: artifacts.images
    

## Module: viz.readmit.small_multiples

### 🎯 Intent & Responsibility

- Produce per-diagnosis panels for:
    
    - Bubble charts: `LOS × Distance (binned)` sized/colored by readmission rate or count.
        
    - Heatmaps: `Prior Admissions × Discharge` with fill by rate/count.
        
    - Mosaic: `# Comorbidities × Discharge` with readmission fill.
        
- Consistent binning via `viz.shared.binning`.
    

### 📥 Inputs & 📤 Outputs

|Direction|Name|Type|Description|
|---|---|---|---|
|📥 In|df|pandas.DataFrame|Columns: `Primary_Diagnosis`, `Length_of_Stay`, `Distance_to_Closest_Hospital`, `Num_Prior_Admissions_Last_6_Months`, `Num_Comorbidities`, `Discharge_Status`, `Has_Readmission_30_Days`|
|📥 In|top_k_diag|int|Top diagnoses to include (default 9)|
|📥 In|bin_specs|Dict[str,Any]|See `viz.shared.binning` for schema|
|📤 Out|figures|Dict[str,matplotlib.figure.Figure]|Keys: `bubble`, `heatmap`, `mosaic` (each a small-multiple grid)|
|📤 Out|tables|Dict[str,pandas.DataFrame]|Aggregated per-panel tables used for plotting|

### ⚠️ Risks & Edge Cases

- Sparse cells → add minimal-count threshold and annotate N.
    
- Very skewed distances/LOS → recommend quantile bins.