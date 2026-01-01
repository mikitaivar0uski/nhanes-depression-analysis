import config  # Importing your config to know which columns are numerical
import pandas as pd
from sklearn.impute import KNNImputer
from sklearn.preprocessing import MinMaxScaler


def apply_professional_imputation(df: pd.DataFrame) -> pd.DataFrame:
    """
    Performs advanced missing value imputation using k-Nearest Neighbors (KNN).

    Steps:
    1. Feature Engineering: Creates a flag column for missing Poverty_Ratio.
    2. Preprocessing: Scales data to [0, 1] (crucial for KNN distance calculation).
    3. Imputation: Uses KNN to find 'twin' patients and fill gaps.
    4. Post-processing: Rounds categorical variables back to integers.
    """
    print("--- STARTING PROFESSIONAL IMPUTATION (KNN) ---")

    # 1. CREATE FLAGGING COLUMN (Hypothesis: Missing Income = Hidden Risk)
    # We do this BEFORE imputation to capture the "missingness" pattern.
    if "Poverty_Ratio" in df.columns:
        df["Poverty_Missing"] = df["Poverty_Ratio"].isna().astype(int)

    # 2. PREPARE DATA FOR KNN
    # KNN cannot handle strings or generic objects. Ensure everything is numeric.
    # We temporarily set SEQN as index so it doesn't affect distance calculation.
    if "SEQN" in df.columns:
        df = df.set_index("SEQN")

    # Save column order and names
    cols = df.columns
    index = df.index

    # 3. SCALING (MinMax)
    # KNN uses Euclidean distance. Large values (e.g., BP=120) dominate small ones (e.g., Gender=1).
    # We must scale everything to [0, 1].
    scaler = MinMaxScaler()
    df_scaled = pd.DataFrame(scaler.fit_transform(df), columns=cols, index=index)

    # 4. KNN IMPUTATION
    # n_neighbors=5 is standard. It looks at 5 most similar patients.
    imputer = KNNImputer(n_neighbors=5)

    # This returns a numpy array
    imputed_data = imputer.fit_transform(df_scaled)

    # Convert back to DataFrame
    df_imputed_scaled = pd.DataFrame(imputed_data, columns=cols, index=index)

    # 5. INVERSE SCALING
    # Return values to their original units (e.g., Age back to 60, not 0.75)
    df_final = pd.DataFrame(
        scaler.inverse_transform(df_imputed_scaled), columns=cols, index=index
    )

    # 6. POST-PROCESSING (Rounding Categories)
    # KNN outputs continuous values (e.g., Gender = 0.7). We need 0 or 1.
    # Logic: If it's NOT in NUMERICAL_COLS, it's categorical -> round it.

    # Add 'Poverty_Missing' and 'Depression' to categorical list implicitly
    categorical_cols = [c for c in df_final.columns if c not in config.NUMERICAL_COLS]

    for col in categorical_cols:
        # Round to nearest integer (0.7 -> 1.0)
        df_final[col] = df_final[col].round().astype(int)

    # 7. FINAL CLEANUP
    # Reset index to bring SEQN back as a column
    df_final = df_final.reset_index()

    print(f"-> Imputation Complete. Shape: {df_final.shape}")
    return df_final
