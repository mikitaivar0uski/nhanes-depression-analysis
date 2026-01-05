from pathlib import Path

# ==============================================================================
# 1. PATHS
# ==============================================================================
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data" / "raw"
OUTPUT_DIR = ROOT_DIR / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ==============================================================================
# 2. FILE MAPPING (NHANES 2017-2018)
# ==============================================================================
NHANES_MAP = {
    # --- Demographics ---
    "DEMO_J": [
        "SEQN",
        "RIAGENDR",
        "RIDAGEYR",
        "INDFMPIR",
        "DMDEDUC2",
        "DMDMARTL",
        "WTMEC2YR",
        "SDMVPSU",
        "SDMVSTRA",
        "RIDRETH3",
    ],
    # --- Questionnaire ---
    "DPQ_J": ["SEQN"]
    + [f"DPQ0{i}0" for i in range(1, 10)],  # Generates DPQ010...DPQ090
    "HSQ_J": ["SEQN", "HSD010"],
    "SMQ_J": ["SEQN", "SMQ020"],
    "ALQ_J": ["SEQN", "ALQ111"],
    "PAQ_J": ["SEQN", "PAQ650"],
    "SLQ_J": ["SEQN", "SLQ050"],
    # --- Exams & Lab ---
    "BMX_J": [
        "SEQN",
        "BMXBMI",
        "BMXWAIST",
    ],  # Added BMXWT (Weight)
    "BPX_J": ["SEQN", "BPXSY1", "BPXDI1"],
    "BIOPRO_J": [
        "SEQN",
        "LBXSGL",
        "LBXSCH",
        "LBXSTR",
        "LBXSUA",
        "LBXSIR",
        "LBXSCR",
        "LBXSATSI",
    ],
    "CBC_J": ["SEQN", "LBXWBCSI", "LBXHGB"],
    "HSCRP_J": ["SEQN", "LBXHSCRP"],
    "PBCD_J": ["SEQN", "LBXBCD", "LBXBPB", "LBXTHG"],
    "ALB_CR_J": ["SEQN", "URDACT"],
    "VID_J": ["SEQN", "LBXVIDMS"],
    # --- DXA Body Composition (Simplified) ---
    "DXX_J": [
        "SEQN",
        "DXXTRFAT",  # Trunk Fat (grams)
        "DXDTOPF",  # Body Fat Percentage
        "DXDTOLE",  # Total Lean Mass (grams)
        # Limb specific data removed as requested
    ],
}

# ==============================================================================
# 3. RENAME MAPPING (Human Readable Names)
# ==============================================================================
RENAME_MAP = {
    # --- Demographics ---
    "RIAGENDR": "Gender",  # Gender
    "RIDAGEYR": "Age",  # Age
    "RIDRETH3": "Race",
    "INDFMPIR": "Poverty_Ratio",  # Ratio of family income to poverty threshold
    "DMDEDUC2": "Education_Level",  # Education level (adults 20+)
    "DMDMARTL": "Marital_Status",  # Marital status
    "SDMVPSU": "PSU",
    "SDMVSTRA": "Strata",
    "WTMEC2YR": "MEC_Weight",
    # --- Habits & History ---
    "HSD010": "General_Health_Cond",  # General health condition (1-5 scale)
    "SLQ050": "Trouble_Sleeping_Doc",  # Ever told by doctor about sleep problems?
    "SMQ020": "100_Cigs_Lifetime",  # Smoked at least 100 cigarettes in life?
    "ALQ111": "Alcohol_Tried",  # Ever had at least one drink of alcohol?
    "PAQ650": "Vigorous_Activity",  # Vigorous intensity physical activity
    # --- Body Measures ---
    "BMXBMI": "BMI",  # Body Mass Index (kg/m^2)
    "BMXWAIST": "Waist_cm",  # Waist circumference in centimeters
    # --- DXA Body Composition ---
    "DXDTOPF": "Body_Fat_Pct",
    "DXDTOLE": "Lean_Mass_g",
    "DXXTRFAT": "Trunk_Fat_g",
    # --- Cardiovascular ---
    "BPXSY1": "BP_Systolic",  # Systolic blood pressure (mmHg)
    "BPXDI1": "BP_Diastolic",  # Diastolic blood pressure (mmHg)
    "LBXSCH": "Cholesterol_Total_mgdL",  # Total cholesterol (mg/dL)
    # --- Biochemistry ---
    "LBXSGL": "Glucose_mgdL",  # Serum glucose (mg/dL)
    "LBXSUA": "UricAcid_mgdL",  # Uric acid (mg/dL)
    "LBXSTR": "Triglycerides_mgdL",  # Triglycerides (mg/dL)
    "LBXSIR": "Iron_ugdL",  # Refrigerated serum iron (ug/dL)
    "LBXSCR": "Creatinine_mgdL",  # Creatinine (kidney function marker) (mg/dL)
    "LBXSATSI": "Transferrin_Sat_Pct",  # Transferrin saturation percentage
    # --- Inflammation & Immunity ---
    "LBXHSCRP": "CRP_mgL",  # C-reactive protein (inflammation marker) (mg/L)
    "LBXWBCSI": "WBC_1000cells",  # White blood cell count (1000 cells/uL)
    "LBXHGB": "Hemoglobin_g_dL",  # Hemoglobin (g/dL)
    # --- Heavy Metals ---
    "LBXBCD": "Cadmium_ugL",  # Blood cadmium (ug/L)
    "LBXBPB": "Lead_ugdL",  # Blood lead (ug/dL)
    "LBXTHG": "Mercury_Total_ugL",  # Total blood mercury (ug/L)
    # --- Kidney & Vitamins ---
    "URDACT": "Albumin_Creatinine_Ratio",  # Albumin/creatinine ratio (renal health)
    "LBXVIDMS": "VitaminD_nmolL",  # Vitamin D (nmol/L)
}

# ==============================================================================
# 4. ENCODING MAPPING (Categories -> Numbers)
# ==============================================================================
ENCODING_LOGIC = {
    "Gender": {1: 0, 2: 1},  # 0=Male, 1=Female
    "Vigorous_Activity": {1: 1, 2: 0},  # 1=Active, 0=Not Active
    # Smoking logic applies during processing
}

# ==============================================================================
# 5. FEATURE GROUPS (Domain-based)
# ==============================================================================
# Organized for Analysis.
# Keep Height/Weight here to test their correlation vs BMI.

FEATURE_GROUPS = {
    "Target": ["PHQ9_Score"],
    "Demographics": [
        "Age",
        "Gender",
        "Race",
        "Education_Level",
        "Marital_Status",
        "Poverty_Ratio",
    ],
    "Lifestyle": [
        "Trouble_Sleeping_Doc",
        "100_Cigs_Lifetime",
        "Alcohol_Tried",
        "Vigorous_Activity",
        "General_Health_Cond",
    ],
    "Anthropometry_Basic": [
        "BMI",
        "Height_cm",  # Kept for comparison
        "Weight_kg",  # Kept for comparison
        "Waist_cm",
    ],
    "Body_Composition_DXA": ["Body_Fat_Pct", "Trunk_Fat_g", "Lean_Mass_g"],
    "Cardio_Metabolic": [
        "BP_Systolic",
        "BP_Diastolic",
        "Glucose_mgdL",
        "Cholesterol_Total_mgdL",
        "Triglycerides_mgdL",
        "UricAcid_mgdL",
    ],
    "Biomarkers_Internal": [
        "CRP_mgL",
        "WBC_1000cells",
        "VitaminD_nmolL",
        "Creatinine_mgdL",
        "Albumin_Creatinine_Ratio",
        "Hemoglobin_g_dL",
        "Iron_ugdL",
        "Transferrin_Sat_Pct",
    ],
    "Toxins": ["Lead_ugdL", "Cadmium_ugL", "Mercury_Total_ugL"],
}

# List of strictly numerical columns (for imputation logic)
NUMERICAL_COLS = [
    "Age",
    "Poverty_Ratio",
    "MEC_Weight",
    "BMI",
    "Height_cm",
    "Weight_kg",
    "Waist_cm",
    "Body_Fat_Pct",
    "Lean_Mass_g",
    "Trunk_Fat_g",
    "BP_Systolic",
    "BP_Diastolic",
    "Cholesterol_Total_mgdL",
    "Glucose_mgdL",
    "UricAcid_mgdL",
    "Triglycerides_mgdL",
    "Iron_ugdL",
    "Creatinine_mgdL",
    "Transferrin_Sat_Pct",
    "CRP_mgL",
    "WBC_1000cells",
    "Hemoglobin_g_dL",
    "Cadmium_ugL",
    "Lead_ugdL",
    "Mercury_Total_ugL",
    "Albumin_Creatinine_Ratio",
    "VitaminD_nmolL",
    "PHQ9_Score",
]


categorical_missing_codes = {
    # --- Demographics ---
    "Education_Level": [7, 9],  # Scale 1-5
    "Marital_Status": [77, 99],  # Note: Double-digit codes here
    # --- Lifestyle & History ---
    "General_Health_Cond": [7, 9],  # Scale 1-5
    "Vigorous_Activity": [7, 9],  # 1=Yes, 2=No
    "100_Cigs_Lifetime": [7, 9],  # 1=Yes, 2=No
    "Alcohol_Tried": [7, 9],  # 1=Yes, 2=No
    "Trouble_Sleeping_Doc": [7, 9],  # 1=Yes, 2=No
}

# --- Append Depression Screener Questions (DPQ) ---
# These are 0-3 scales. Codes 7 and 9 must be removed to prevent
# calculating an artificially high depression score.
for i in range(1, 10):
    col_name = f"DPQ0{i}0"  # Generates DPQ010, DPQ020...
    categorical_missing_codes[col_name] = [7, 9]
