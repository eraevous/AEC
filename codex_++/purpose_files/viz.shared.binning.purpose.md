@ai-path: viz.shared.binning
    
- @ai-source-file: src/viz/shared/binning.py
    
- @ai-role: analysis.utility
    
- @ai-intent: "Provide consistent binning utilities (equal-width, quantile, custom edges) and schemas for 2D aggregations."
    
- @ai-version: 0.1.0
    
- @schema-version: 0.3
    
- @ai-risk-pii: none
    
- @ai-risk-performance: "Fast; numpy/pandas only."
    
- @ai-dependencies: pandas,numpy
    
- @ai-used-by: viz.readmit.small_multiples,viz.readmit.bars_hists,viz.readmit.corrgram_3x3
    
- @ai-downstream: viz.report.book
    

## Module: viz.shared.binning

### 🎯 Intent & Responsibility

- Implement `bin_series(series, method, bins)` with methods: `equal`, `quantile`, `edges`.
    
- Implement `cross_agg(df, xbin, ybin, value, agg)` to build pivot-friendly tables.
    
- Define shared `bin_specs` schema for LOS, Distance, Prior Admissions, Comorbidities.
    

### 📥 Inputs & 📤 Outputs

|Direction|Name|Type|Description|
|---|---|---|---|
|📥 In|series|pandas.Series|Numeric series to bin|
|📥 In|method|Literal["equal","quantile","edges"]|Binning strategy|
|📥 In|bins|int|number of bins for `equal`/`quantile` or list[float] for `edges`|
|📤 Out|binned|pandas.Categorical|Categorical with ordered intervals|
|📤 Out|info|Dict[str,Any]|Metadata: edges, labels, counts|

### 🧪 Test Guarantees

- Deterministic intervals; labels strictly ordered; no NA expansion unless specified.