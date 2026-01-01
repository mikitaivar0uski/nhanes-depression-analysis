import config
import numpy as np
import pandas as pd
from imputation import apply_professional_imputation
from loader import load_raw_data

def apply_encodings(df: pd.DataFrame) -> pd.DataFrame:
    """
    Encodes categorical variables based on config.ENCODING_LOGIC.
    Values not present in the mapping (e.g., 7: Refused, 9: Don't Know) 
    are automatically converted to NaN.
    """
    for col, mapping in config.ENCODING_LOGIC.items():
        if col in df.columns:
            df[col] = df[col].map(mapping)
    return df

def clean_numerical_and_categorical_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans data artifacts without deleting rows.
    1. Fixes SAS micro-numbers (precision artifacts).
    2. Replaces impossible biological zeros (BMI, Glucose) with NaN.
    3. Removes garbage codes (7, 9, 77, 99) from specific ordinal scales.
    """
    # Block 1: Fix SAS micro-numbers (e.g., 5.39e-79 -> 0)
    cols_to_fix = [c for c in config.NUMERICAL_COLS if c in df.columns]
    for col in cols_to_fix:
        df[col] = df[col].map(lambda x: 0 if abs(x) < 1e-9 else x)

    # Block 2: Biological impossibilities (Zeros indicating missing values)
    vital_signs = ["Glucose_mgdL", "BMI", "UricAcid_mgdL", "Cholesterol_Total_mgdL"]
    for v in vital_signs:
        if v in df.columns:
            df[v] = df[v].replace(0, np.nan)

    # Block 3: Categorical garbage collection (7: Refused, 9: Don't Know)
    ordinal_garbage_cols = ["General_Health_Cond", "Education_Level", "Marital_Status"]
    garbage_codes = [7, 9, 77, 99]

    for col in ordinal_garbage_cols:
        if col in df.columns:
            df[col] = df[col].replace(garbage_codes, np.nan)
    return df

def create_target(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates the 'Depression' target variable based on PHQ-9 scores.
    IMPORTANT: This function no longer uses dropna(). 
    Insufficient data results in a NaN target, preserving the row for sample structure.
    """
    phq_cols = [c for c in df.columns if c.startswith("DPQ") and c != "DPQ100"]

    if not phq_cols:
        df["Depression"] = np.nan
        return df

    # Replace 'Refused' and 'Don't Know' codes in PHQ-9 items
    df[phq_cols] = df[phq_cols].replace({7: np.nan, 9: np.nan})

    # Calculate score if at least 7 out of 9 questions are answered
    df["PHQ9_Score"] = df[phq_cols].sum(axis=1, min_count=7)

    # Define binary target: 1 = Depressed (Score >= 10), 0 = Healthy
    df["Depression"] = np.nan
    df.loc[df["PHQ9_Score"] < 10, "Depression"] = 0
    df.loc[df["PHQ9_Score"] >= 10, "Depression"] = 1

    # Drop PHQ-9 components and intermediate score
    df = df.drop(columns=phq_cols + ["PHQ9_Score"])
    return df

def clean_pipeline() -> pd.DataFrame:
    """
    Main execution pipeline implementing the professional In-Analysis Flagging approach.
    This preserves PSU and Strata variables for correct variance estimation.
    """
    # 1. Loading
    df = load_raw_data()

    # 2. Renaming (Includes PSU, Strata, and Weights)
    print("--- 1. RENAMING ---")
    df = df.rename(columns=config.RENAME_MAP)

    # 3. Categorical Encoding and Outlier Cleaning
    df = apply_encodings(df)
    df = clean_numerical_and_categorical_outliers(df)

    # 4. Target Generation (Maintains all rows)
    df = create_target(df)

    # 5. SUBPOPULATION FLAGGING (Critical for Survey Data Science)
    # We define the eligible sample for the specific research question.
    print("--- 2. CREATING IN-ANALYSIS FLAG ---")
    
    # Criteria 1: Adults (Age 18+)
    cond_age = (df['Age'] >= 18)
    
    # Criteria 2: Target variable is present (PHQ-9 answered)
    cond_target = (df['Depression'].notna())
    
    # Criteria 3: Valid Examination Weight
    cond_weight = (df['MEC_Weight'] > 0)
    
    # Criteria 4: Medical Filtering (Exclude acute inflammation)
    # Note: Using .isna() allows for imputation later rather than strict exclusion
    cond_no_infection = (
        ((df['CRP_mgL'] <= 10.0) | (df['CRP_mgL'].isna())) & 
        ((df['WBC_1000cells'] <= 11.0) | (df['WBC_1000cells'].isna()))
    )

    # Combine all logic into a single flag
    df['In_Analysis'] = (cond_age & cond_target & cond_weight & cond_no_infection).astype(int)

    # 6. Professional KNN Imputation
    # Performed on the full dataset to utilize cross-group patterns for better accuracy
    df = apply_professional_imputation(df)

    print(f"--- PIPELINE COMPLETE ---")
    print(f"Full Population Rows (Structure Preserved): {len(df)}")
    print(f"Research-Eligible Rows (In_Analysis=1): {df['In_Analysis'].sum()}")
    
    return df

if __name__ == "__main__":
    df = clean_pipeline()
    # Verification: Total weighted population should match US census estimates (~320M)
    print(f"Total Weighted Population Estimate: {df['MEC_Weight'].sum():,.0f}")