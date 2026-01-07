import numpy as np
import pandas as pd
from sklearn.impute import KNNImputer
from sklearn.preprocessing import MinMaxScaler

# Import your configuration module
from src import config


def _filter_population(df: pd.DataFrame) -> pd.DataFrame:
    """
    Restricts dataset to the target population (Adults 18+).
    """
    initial_rows = len(df)
    # Using readable name 'Age'
    df_adults = df[df["Age"] >= 18].copy()

    dropped = initial_rows - len(df_adults)
    if dropped > 0:
        print(
            f"-> Filter: Dropped {dropped} rows (Minors < 18). Remaining: {len(df_adults)}"
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

    # 1. Handle NHANES "Refused" (7/77) and "Don't Know" (9/99) codes
    for col, codes in config.categorical_missing_codes.items():
        if col in df.columns:
            df[col] = df[col].replace(codes, np.nan)

    # 2. Generate Target Variables (Score and Binary)
    dpq_cols = [c for c in df.columns if c.startswith("DPQ") and c != "DPQ100"]

    if dpq_cols:
        # Require at least 7 valid answers to compute a score
        df["PHQ9_Score"] = df[dpq_cols].sum(axis=1, min_count=7)

        # Create Binary Target: 1 if Score >= 10 (Clinical Depression), else 0
        # Only calculate this where PHQ9_Score is not NaN
        df["Depression"] = np.where(
            df["PHQ9_Score"].isna(), np.nan, (df["PHQ9_Score"] >= 10).astype(float)
        )

        # --- CRITICAL: DROP RAW DPQ COLUMNS ---
        # Removing individual questions so the model doesn't "cheat".
        df = df.drop(columns=dpq_cols)
        print(f"-> Target Generation: Dropped {len(dpq_cols)} raw DPQ columns.")

    # 3. Label Encoding for Categorical Features
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns
    for col in categorical_cols:
        if col == "SEQN":
            continue

        # Encode strings to numbers, preserving NaNs
        df[col] = df[col].astype("category").cat.codes
        df[col] = df[col].replace(-1, np.nan)

    # 4. Handle Biological Artifacts
    for v in ["BMI", "Glucose_mgdL", "CRP_mgL"]:
        if v in df.columns:
            df[v] = df[v].replace(0, np.nan)

    return df


def _apply_imputation(df: pd.DataFrame) -> pd.DataFrame:
    """
    Performs KNN Imputation.
    Excludes Targets (Score & Binary), ID, and Weights.
    """
    # Columns to EXCLUDE from imputation
    # Added "Depression" to exclusion list
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

    print(f"-> Imputation Complete. Features: {df_final.shape[1]}")
    return df_final


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

    return df


def run_full_preprocessing(df: pd.DataFrame) -> pd.DataFrame:
    """
    Main orchestration function.
    """
    print("Starting Preprocessing Pipeline...")

    df = df.rename(columns=config.RENAME_MAP)
    df = _filter_population(df)
    df = _clean_and_encode(df)
    df = _apply_imputation(df)
    df = _engineer_features(df)

    # Drop rows where Target is missing (using PHQ9_Score as primary check)
    before_drop = len(df)
    df = df.dropna(subset=["PHQ9_Score"])
    if len(df) < before_drop:
        print(f"-> Dropped {before_drop - len(df)} rows where Target was missing.")

    return df
