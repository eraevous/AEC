from pathlib import Path

import pandas as pd

from src.viz.report.book import build_book
from src.viz.shared.theme import apply_base_theme  # if present; else remove this line

# ---- edit these two lines ----
DATA_LOC = "/Users/zachrhodes/Documents/Strata/data/cs_data.xlsx"  # <— your dataset
OUT_DIR = Path("artifacts")  # where images & manifest go
# --------------------------------

df = pd.read_excel(DATA_LOC)

# Minimal, safe defaults; tweak as needed
config = {
    "output_dir": OUT_DIR,
    "palette": {0: "#264653", 1: "#e76f51"},  # readmit palette used in A
    "diagnosis_col": "Primary_Diagnosis",
    "readmit_col": "Has_Readmission_30_Days",
    "categoricals": ["Gender", "Discharge_Status"],
    "numerics": [
        "Length_of_Stay",
        "Distance_to_Closest_Hospital",
        "Num_Prior_Admissions_Last_6_Months",
        "Num_Comorbidities",
    ],
    "top_k": 10,  # for Sankey category compression
    "top_k_diag": 6,  # for parallel coords & small multiples
    "bin_specs": {  # coarse, fast defaults
        "Length_of_Stay": {"method": "quantile", "bins": 5},
        "Distance_to_Closest_Hospital": {"method": "quantile", "bins": 5},
        "Num_Prior_Admissions_Last_6_Months": {"method": "edges", "bins": [0, 1, 2, 3]},
        "Num_Comorbidities": {"method": "edges", "bins": [0, 1, 2]},
    },
    "enable": {  # flip to False to save runtime
        "bars_hists": True,
        "boxplots": True,
        "corrgram_3x3": True,  # set False if slow
        "parallel_coords": True,  # set False if plotly issues
        "sankey": True,
        "small_multiples": True,  # heavy; disable if needed
    },
    # Sampling knobs if you’re tight on time
    "sample": 5000,  # or None; modules should accept/ignore safely
}

OUT_DIR.mkdir(parents=True, exist_ok=True)
try:
    apply_base_theme()  # no-op if not present
except Exception:
    pass

manifest = build_book(df, config)  # returns dict of paths/notes
(OUT_DIR / "viz_manifest.json").write_text(__import__("json").dumps(manifest, indent=2))
print(f"✔ Wrote manifest to {OUT_DIR/'viz_manifest.json'}")
