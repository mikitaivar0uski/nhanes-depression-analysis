from pathlib import Path

# ==============================================================================
# 1. PATHS
# ==============================================================================
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data" / "raw"

# ==============================================================================
# 2. FILE MAPPING (NHANES 2011-2018)
# ==============================================================================
# Suffixes: 2011-12 (_G), 2013-14 (_H), 2015-16 (_I), 2017-18 (_J)
CYCLES = ["_G", "_H", "_I", "_J"]

NHANES_MAP = {
    # --- Demographics ---
    "DEMO": [
        "SEQN",
        "RIAGENDR",
        "RIDAGEYR",
        "RIDEXPRG",  
        "INDFMPIR",
        "DMDEDUC2",
        "DMDMARTL",
        "WTMEC2YR",
        "SDMVPSU",
        "SDMVSTRA",
        "RIDRETH3",
    ],
    # --- Questionnaire ---
    "DPQ": ["SEQN"]
    + [f"DPQ0{i}0" for i in range(1, 10)],  # Generates DPQ010...DPQ090
    "HSQ": ["SEQN", "HSD010"],
    "SMQ": ["SEQN", "SMQ020"],
    "ALQ": ["SEQN", "ALQ111"],
    "PAQ": ["SEQN", "PAQ650"],
    "SLQ": ["SEQN", "SLQ050"],
    # --- Exams & Lab ---
    "BMX": [
        "SEQN",
        "BMXBMI",
        "BMXWAIST",
    ],  # Added BMXWT (Weight)
    "BPX": ["SEQN", "BPXSY1", "BPXDI1"],
    "BIOPRO": [
        "SEQN",
        "LBXSGL",
        "LBXSCH",
        "LBXSTR",
        "LBXSUA",
        "LBXSIR",
        "LBXSCR",
        "LBXSATSI",
    ],
    "CBC": ["SEQN", "LBXWBCSI", "LBXHGB"],
    "HSCRP": ["SEQN", "LBXHSCRP"],
    "PBCD": ["SEQN", "LBXBCD", "LBXBPB", "LBXTHG"],
    "ALB_CR": ["SEQN", "URDACT"],
    "VID": ["SEQN", "LBXVIDMS"],
    # --- Dietary Data (Day 1) ---
    "DR1TOT": [
        "SEQN",
        "DR1TKCAL",  # Energy
        "DR1TPROT",  # Protein
        "DR1TCARB",  # Carbohydrates
        "DR1TSFAT",  # Total Saturated Fatty Acids
        "DR1TMFAT",  # Total Monounsaturated Fatty Acids
        "DR1TPFAT",  # Total Polyunsaturated Fatty Acids
        "DR1TCHOL",  # Cholesterol
        "DR1TFIBE",  # Dietary Fiber
        "DR1TVARA",  # Vitamin A (RAE)
        "DR1TVB1",   # Thiamin (B1)
        "DR1TVB2",   # Riboflavin (B2)
        "DR1TNIAC",  # Niacin
        "DR1TVB6",   # Vitamin B6
        "DR1TFOLA",  # Total Folate
        "DR1TVB12",  # Vitamin B12
        "DR1TVC",    # Vitamin C
        "DR1TVE",    # Vitamin E
        "DR1TMAGN",  # Magnesium
        "DR1TIRON",  # Iron
        "DR1TZINC",  # Zinc
        "DR1TSELE",  # Selenium
        "DR1TCAFF",  # Caffeine
        "DR1TALCO",  # Alcohol
        "DR1TBCAR",  # Beta-carotene
        "DR1TTFAT",  # Total Fat
        "DR1TFA",    # Folic Acid
        "DR1TVD",    # Vitamin D (Dietary)
    ],
    # --- Dietary Data (Day 2) ---
    "DR2TOT": [
        "SEQN",
        "DR2TKCAL",
        "DR2TPROT",
        "DR2TCARB",
        "DR2TSFAT",
        "DR2TMFAT",
        "DR2TPFAT",
        "DR2TCHOL",
        "DR2TFIBE",
        "DR2TVARA",
        "DR2TVB1",
        "DR2TVB2",
        "DR2TNIAC",
        "DR2TVB6",
        "DR2TFOLA",
        "DR2TVB12",
        "DR2TVC",
        "DR2TVE",
        "DR2TMAGN",
        "DR2TIRON",
        "DR2TZINC",
        "DR2TSELE",
        "DR2TCAFF",
        "DR2TALCO",
        "DR2TBCAR",
        "DR2TTFAT",
        "DR2TFA",
        "DR2TVD",
    ],
    # --- DXA Body Composition (Simplified) ---
    "DXX": [
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
    "RIDEXPRG": "Pregnancy", # Pregnancy
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
    "LBXCOT": "Cotinine_ngmL", # Serum Cotinine (if available in BIOPRO or special lab)
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
    # --- Dietary (Day 1) ---
    "DR1TKCAL": "Energy_kcal_D1",
    "DR1TPROT": "Protein_g_D1",
    "DR1TCARB": "Carbs_g_D1",
    "DR1TSFAT": "SaturatedFat_g_D1",
    "DR1TMFAT": "MonounsatFat_g_D1",
    "DR1TPFAT": "PolyunsatFat_g_D1",
    "DR1TCHOL": "DietaryChol_mg_D1",
    "DR1TFIBE": "Fiber_g_D1",
    "DR1TVARA": "VitaminA_ug_D1",
    "DR1TVB1": "VitaminB1_mg_D1",
    "DR1TVB2": "VitaminB2_mg_D1",
    "DR1TNIAC": "Niacin_mg_D1",
    "DR1TVB6": "VitaminB6_mg_D1",
    "DR1TFOLA": "Folate_ug_D1",
    "DR1TVB12": "VitaminB12_ug_D1",
    "DR1TVC": "VitaminC_mg_D1",
    "DR1TVE": "VitaminE_mg_D1",
    "DR1TMAGN": "Magnesium_mg_D1",
    "DR1TIRON": "Iron_mg_D1",
    "DR1TZINC": "Zinc_mg_D1",
    "DR1TSELE": "Selenium_ug_D1",
    "DR1TCAFF": "Caffeine_mg_D1",
    "DR1TALCO": "Alcohol_g_D1",
    # --- Dietary (Day 2) ---
    "DR2TKCAL": "Energy_kcal_D2",
    "DR2TPROT": "Protein_g_D2",
    "DR2TCARB": "Carbs_g_D2",
    "DR2TSFAT": "SaturatedFat_g_D2",
    "DR2TMFAT": "MonounsatFat_g_D2",
    "DR2TPFAT": "PolyunsatFat_g_D2",
    "DR2TCHOL": "DietaryChol_mg_D2",
    "DR2TFIBE": "Fiber_g_D2",
    "DR2TVARA": "VitaminA_ug_D2",
    "DR2TVB1": "VitaminB1_mg_D2",
    "DR2TVB2": "VitaminB2_mg_D2",
    "DR2TNIAC": "Niacin_mg_D2",
    "DR2TVB6": "VitaminB6_mg_D2",
    "DR2TFOLA": "Folate_ug_D2",
    "DR2TVB12": "VitaminB12_ug_D2",
    "DR2TVC": "VitaminC_mg_D2",
    "DR2TVE": "VitaminE_mg_D2",
    "DR2TMAGN": "Magnesium_mg_D2",
    "DR2TIRON": "Iron_mg_D2",
    "DR2TZINC": "Zinc_mg_D2",
    "DR2TSELE": "Selenium_ug_D2",
    "DR2TCAFF": "Caffeine_mg_D2",
    "DR2TALCO": "Alcohol_g_D2",
    # --- Additional DII Components ---
    "DR1TBCAR": "BetaCarotene_ug_D1",
    "DR2TBCAR": "BetaCarotene_ug_D2",
    "DR1TTFAT": "TotalFat_g_D1",
    "DR2TTFAT": "TotalFat_g_D2",
    "DR1TFA": "FolicAcid_ug_D1",
    "DR2TFA": "FolicAcid_ug_D2",
    "DR1TVD": "VitaminD_ug_D1",
    "DR2TVD": "VitaminD_ug_D2",
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
    "Energy_kcal",
    "Protein_g",
    "Carbs_g",
    "SaturatedFat_g",
    "MonounsatFat_g",
    "PolyunsatFat_g",
    "DietaryChol_mg",
    "Fiber_g",
    "VitaminA_ug",
    "VitaminB1_mg",
    "VitaminB2_mg",
    "Niacin_mg",
    "VitaminB6_mg",
    "Folate_ug",
    "VitaminB12_ug",
    "VitaminC_mg",
    "VitaminE_mg",
    "Magnesium_mg",
    "Iron_mg",
    "Zinc_mg",
    "Selenium_ug",
    "Caffeine_mg",
    "Alcohol_g",
    "BetaCarotene_ug",
    "TotalFat_g",
    "FolicAcid_ug",
    "VitaminD_ug",
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
