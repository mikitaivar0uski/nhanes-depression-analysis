import numpy as np
import pandas as pd
from sklearn.impute import KNNImputer
from sklearn.preprocessing import MinMaxScaler

from src import config


def _filter_population(df: pd.DataFrame) -> pd.DataFrame:
    """
    Internal helper: Restricts dataset to the target population (Adults 18+).

    Rationale:
    NHANES administers PHQ-9 only to participants aged 18+. Including minors
    inflates the denominator, leading to underestimated depression prevalence.
    """
    initial_rows = len(df)

    # Filter logic
    # Note: Assumes columns have already been renamed to readable format (Age)
    df_adults = df[df["Age"] >= 18].copy()

    dropped_rows = initial_rows - len(df_adults)
    if dropped_rows > 0:
        print(
            f"Population Filter: Dropped {dropped_rows} rows (Minors < 18). Retained: {len(df_adults)}"
        )

    return df_adults


def clean_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    """
    Executes standard cleaning: encoding and target variable generation.
    Note: Renaming must happen BEFORE calling this function.
    """
    # Create a copy to avoid SettingWithCopy warnings
    df = df.copy()

    # 1. Encode Categorical Features
    for col, mapping in config.ENCODING_LOGIC.items():
        if col in df.columns:
            df[col] = df[col].map(mapping)

    # 2. Handle Biological Artifacts (Zero is impossible for these metrics)
    for v in ["BMI", "Glucose_mgdL", "CRP_mgL"]:
        if v in df.columns:
            df[v] = df[v].replace(0, np.nan)

    # 3. Generate Target Variable (PHQ-9)
    phq_cols = [c for c in df.columns if c.startswith("DPQ") and c != "DPQ100"]

    if phq_cols:
        # NHANES codes 7 (Refused) and 9 (Don't Know) as missing for scoring
        df[phq_cols] = df[phq_cols].replace({7: np.nan, 9: np.nan})

        # Require at least 7 valid answers to compute a score
        df["PHQ9_Score"] = df[phq_cols].sum(axis=1, min_count=7)

        # Binary Target
        df["Depression"] = (df["PHQ9_Score"] >= 10).astype(float)

        # Propagate NaNs: If score is NaN, target must be NaN
        df.loc[df["PHQ9_Score"].isna(), "Depression"] = np.nan

    return df


def apply_imputation(df: pd.DataFrame) -> pd.DataFrame:
    """
    Performs KNN Imputation with scaling and post-processing.
    """

    # 1. Feature Engineering: Capture 'Missingness' signal
    if "Poverty_Ratio" in df.columns:
        df["Poverty_Missing"] = df["Poverty_Ratio"].isna().astype(int)

    # 2. Preparation for KNN
    if "SEQN" in df.columns:
        df = df.set_index("SEQN")

    cols = df.columns
    index = df.index

    # 3. Scaling
    scaler = MinMaxScaler()
    df_scaled = pd.DataFrame(scaler.fit_transform(df), columns=cols, index=index)

    # 4. Imputation
    imputer = KNNImputer(n_neighbors=5)
    imputed_data = imputer.fit_transform(df_scaled)

    df_imputed_scaled = pd.DataFrame(imputed_data, columns=cols, index=index)

    # 5. Inverse Scaling
    df_final = pd.DataFrame(
        scaler.inverse_transform(df_imputed_scaled), columns=cols, index=index
    )

    # 6. Post-processing (Rounding categories)
    categorical_cols = [c for c in df_final.columns if c not in config.NUMERICAL_COLS]

    for col in categorical_cols:
        df_final[col] = df_final[col].round().astype(int)

    # Restore SEQN
    df_final = df_final.reset_index()

    print(f"-> Imputation Complete. Final Shape: {df_final.shape}")
    return df_final


def run_full_preprocessing(df: pd.DataFrame) -> pd.DataFrame:
    """
    Orchestration function: Renaming -> Filtering -> Cleaning -> Imputation.
    """
    # Step 1: Rename Columns (Critical: Must be done first to use readable names)
    df = df.rename(columns=config.RENAME_MAP)

    # Step 2: Filter Population (Adults 18+)
    df_adults = _filter_population(df)

    # Step 3: Clean & Engineer Features
    df_clean = clean_pipeline(df_adults)

    # Step 4: Handle Missing Data
    df_processed = apply_imputation(df_clean)

    return df_processed
