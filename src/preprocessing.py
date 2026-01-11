import numpy as np
import pandas as pd
from sklearn.impute import KNNImputer
from sklearn.preprocessing import MinMaxScaler


from src import config


def _filter_population(df: pd.DataFrame) -> pd.DataFrame:
    """
    Restricts dataset to the target population (Adults 18+).
    """
    initial_rows = len(df)

    df_adults = df[df["Age"] >= 18].copy()


    if "Pregnancy" in df_adults.columns:
        initial_adults = len(df_adults)
        df_adults = df_adults[df_adults["Pregnancy"] != 1]
        preg_dropped = initial_adults - len(df_adults)
        if preg_dropped > 0:
            print(f"-> Filter: Dropped {preg_dropped} rows (Pregnancy).")

    dropped = initial_rows - len(df_adults)
    if dropped > 0:
        print(
            f"-> Filter: Dropped {dropped} rows total (Minors < 18 or Pregnant). Remaining: {len(df_adults)}"
        )

    return df_adults


def _clean_and_encode(df: pd.DataFrame) -> pd.DataFrame:
    """
    1. Replaces Refused/Don't Know codes (7/9) with NaN.
    2. Calculates Target (PHQ9 Score AND Binary Depression).
    3. DROPS raw DPQ columns to prevent leakage.
    4. Encodes categorical variables.
    """
    df = df.copy()


    for col, codes in config.categorical_missing_codes.items():
        if col in df.columns:
            df[col] = df[col].replace(codes, np.nan)


    dpq_cols = [c for c in df.columns if c.startswith("DPQ") and c != "DPQ100"]

    if dpq_cols:

        df["PHQ9_Score"] = df[dpq_cols].sum(axis=1, min_count=7)


        df["Depression"] = np.where(
            df["PHQ9_Score"].isna(), np.nan, (df["PHQ9_Score"] >= 10).astype(float)
        )

        df = df.drop(columns=dpq_cols)
        print(f"-> Target Generation: Dropped {len(dpq_cols)} raw DPQ columns.")

    categorical_cols = df.select_dtypes(include=["object", "category"]).columns
    for col in categorical_cols:
        if col == "SEQN":
            continue

        df[col] = df[col].astype("category").cat.codes
        df[col] = df[col].replace(-1, np.nan)

    for v in ["BMI", "Glucose_mgdL", "CRP_mgL"]:
        if v in df.columns:
            df[v] = df[v].replace(0, np.nan)

    return df


def _apply_imputation(df: pd.DataFrame) -> pd.DataFrame:
    """
    Performs KNN Imputation.
    Excludes Targets (Score & Binary), ID, and Weights.
    """

    cols_to_exclude = [
        "SEQN",
        "PHQ9_Score",
        "Depression",
        "MEC_Weight",
        "PSU",
        "Strata",
    ]

    excluded_data = df[[c for c in cols_to_exclude if c in df.columns]].copy()
    impute_cols = [c for c in df.columns if c not in cols_to_exclude]
    df_to_impute = df[impute_cols].copy()

    # 1. Scaling
    scaler = MinMaxScaler()
    df_scaled = pd.DataFrame(scaler.fit_transform(df_to_impute), columns=impute_cols)

    # 2. KNN Imputer
    imputer = KNNImputer(n_neighbors=5)
    df_imputed_array = imputer.fit_transform(df_scaled)
    df_imputed = pd.DataFrame(df_imputed_array, columns=impute_cols)

    # 3. Inverse Scaling
    df_restored = pd.DataFrame(
        scaler.inverse_transform(df_imputed), columns=impute_cols
    )

    # 4. Rounding categorical columns
    for col in df_restored.columns:
        if col not in config.NUMERICAL_COLS:
            df_restored[col] = df_restored[col].round()

    # 5. Reassemble
    df_final = pd.concat(
        [excluded_data.reset_index(drop=True), df_restored.reset_index(drop=True)],
        axis=1,
    )

    print(f"-> Imputation Complete. Final Shape: {df_final.shape}")
    return df_final


def _process_dietary_averaging(df: pd.DataFrame) -> pd.DataFrame:
    """
    Averages Day 1 and Day 2 dietary data to estimate usual intake.
    If Day 2 is missing, Day 1 is used.
    """
    # List of base nutrient names (without _D1/_D2 suffix)
    nutrients = [
        "Energy_kcal", "Protein_g", "Carbs_g", "SaturatedFat_g", 
        "MonounsatFat_g", "PolyunsatFat_g", "DietaryChol_mg", "Fiber_g",
        "VitaminA_ug", "VitaminB1_mg", "VitaminB2_mg", "Niacin_mg",
        "VitaminB6_mg", "Folate_ug", "VitaminB12_ug", "VitaminC_mg", 
        "VitaminE_mg", "Magnesium_mg", "Iron_mg", "Zinc_mg", 
        "Selenium_ug", "Caffeine_mg", "Alcohol_g"
    ]
    
    print("-> Processing Dietary Data: Averaging Day 1 and Day 2...")
    
    for nutrient in nutrients:
        col_d1 = f"{nutrient}_D1"
        col_d2 = f"{nutrient}_D2"
        
        # Select available columns for this nutrient
        available_cols = [c for c in [col_d1, col_d2] if c in df.columns]
        
        if available_cols:
            # Mean skips NaNs by default
            df[nutrient] = df[available_cols].mean(axis=1)
    
    return df


def _engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Creates derived features (Log transformation, Binning).
    """
    # 1. Log Transformations
    vars_to_log = {
        "Lead_ugdL": "Log_Lead",
        "Cadmium_ugL": "Log_Cadmium",
        "Mercury_Total_ugL": "Log_Mercury",
        "CRP_mgL": "Log_CRP",
    }

    for original, new_col in vars_to_log.items():
        if original in df.columns:
            df[new_col] = np.log10(df[original] + 0.01)

    # 2. Acute Inflammation Flag
    if "CRP_mgL" in df.columns:
        df["is_acute_inflammation"] = (df["CRP_mgL"] >= 10).astype(int)

    # 3. BMI Binning
    if "BMI" in df.columns:
        df["BMI_Category"] = pd.cut(
            df["BMI"], bins=[0, 18.5, 25, 30, 100], labels=[0, 1, 2, 3]
        ).astype(float)

    # 4. Composite Dietary Antioxidant Index (CDAI)
    # Using Vitamin A, C, E, Zinc, Selenium, Magnesium
    antioxidants = [
        "VitaminA_ug",
        "VitaminC_mg",
        "VitaminE_mg",
        "Zinc_mg",
        "Selenium_ug",
        "Magnesium_mg",
    ]
    if all(col in df.columns for col in antioxidants):
        cdai_components = []
        for col in antioxidants:
            # Check for zero variance to avoid division by zero
            if df[col].std() == 0:
                z_score = df[col] - df[col].mean()
            else:
                z_score = (df[col] - df[col].mean()) / df[col].std()
            cdai_components.append(z_score)
        df["CDAI"] = pd.concat(cdai_components, axis=1).sum(axis=1)
        print("-> Feature Engineering: Calculated CDAI")
    else:
        missing = [c for c in antioxidants if c not in df.columns]
        print(f"-> Feature Engineering: SKIPPED CDAI. Missing columns: {missing}")

    # 5. Dietary Inflammatory Index (DII) - Simplified version based on available data
    dii_plus = ["DietaryChol_mg", "SaturatedFat_g"]  # Pro-inflammatory
    dii_minus = [
        "Alcohol_g",
        "VitaminE_mg",
        "VitaminA_ug",
        "Fiber_g",
        "VitaminC_mg",
        "Magnesium_mg",
        "Niacin_mg",
        "VitaminB6_mg",
        "VitaminB12_ug",
        "Zinc_mg",
        "Selenium_ug",
    ]  # Anti-inflammatory
    
    if all(col in df.columns for col in dii_plus + dii_minus):
        # We calculate z-scores relative to standard global means if we had them, 
        # but here we use cohort means as a proxy.
        dii_score = 0
        for col in dii_plus:
            std = df[col].std()
            if std != 0 and not np.isnan(std):
                dii_score += (df[col] - df[col].mean()) / std
        for col in dii_minus:
            std = df[col].std()
            if std != 0 and not np.isnan(std):
                dii_score -= (df[col] - df[col].mean()) / std
        df["DII"] = dii_score
        print("-> Feature Engineering: Calculated DII")
    else:
        missing = [c for c in dii_plus + dii_minus if c not in df.columns]
        print(f"-> Feature Engineering: SKIPPED DII. Missing columns: {missing}")

    # 6. Metabolic Dysfunction Indicators
    if all(col in df.columns for col in ["BP_Systolic", "BP_Diastolic"]):
        # Mean Arterial Pressure (MAP)
        df["MAP"] = df["BP_Diastolic"] + (1 / 3) * (df["BP_Systolic"] - df["BP_Diastolic"])
        
    if all(col in df.columns for col in ["Triglycerides_mgdL", "Glucose_mgdL"]):
        # Triglyceride-Glucose (TyG) Index
        df["TyG_Index"] = np.log(df["Triglycerides_mgdL"] * df["Glucose_mgdL"] / 2)
        
    metabolic_cols = ["Cholesterol_Total_mgdL", "UricAcid_mgdL", "MAP", "TyG_Index"]
    if all(col in df.columns for col in metabolic_cols):
        # Metabolic Score (Sum of z-scores)
        ms_score = 0
        for col in metabolic_cols:
            ms_score += (df[col] - df[col].mean()) / df[col].std()
        df["Metabolic_Score"] = ms_score
        print("-> Feature Engineering: Calculated Metabolic Score indices")

    # 7. eGFR (Estimated Glomerular Filtration Rate) - CKD-EPI 2021 Formula
    if all(col in df.columns for col in ["Age", "Gender", "Creatinine_mgdL"]):
        
        # Vectorized calculation
        scr = df["Creatinine_mgdL"]
        age = df["Age"]
        is_female = (df["Gender"] == 1)
        
        k = np.where(is_female, 0.7, 0.9)
        a = np.where(is_female, -0.241, -0.302)
        f = np.where(is_female, 1.012, 1)
        
        # Handle 0 or NaN creatinine to avoid errors
        scr = scr.replace(0, np.nan)
        
        df["eGFR"] = 142 * (np.minimum(scr/k, 1)**a) * (np.maximum(scr/k, 1)**-1.200) * (0.9938**age) * f
        print("-> Feature Engineering: Calculated eGFR")

    return df


def run_full_preprocessing(df: pd.DataFrame) -> pd.DataFrame:
    """
    Main orchestration function.
    """
    print("Starting Preprocessing Pipeline...")

    df = df.rename(columns=config.RENAME_MAP)
    df = _filter_population(df)
    df = _clean_and_encode(df)
    df = _process_dietary_averaging(df)
    df = _apply_imputation(df)
    df = _engineer_features(df)

    # Drop rows where Target is missing (using PHQ9_Score as primary check)
    before_drop = len(df)
    df = df.dropna(subset=["PHQ9_Score"])
    if len(df) < before_drop:
        print(f"-> Dropped {before_drop - len(df)} rows where Target was missing.")

    return df
