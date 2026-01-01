import sys
from pathlib import Path

import config
import pandas as pd


def find_file(filename_key: str) -> Path:
    target_name = filename_key.lower()

    # 1. Validate data directory existence
    if not config.DATA_DIR.exists():
        print(f"CRITICAL ERROR: Data directory not found at: {config.DATA_DIR}")
        print("Please verify ROOT_DIR in config.py")
        sys.exit(1)

    # 2. Recursive search for files (rglob)
    # This handles nested folder structures and case-insensitive matching
    for file_path in config.DATA_DIR.rglob("*"):
        if file_path.is_file():
            # Match filename stem (name without extension)
            if file_path.stem.lower() == target_name:
                # Strictly ensure we are picking the SAS Transport (.xpt) file
                if file_path.suffix.lower() == ".xpt":
                    return file_path

    return None


def load_raw_data():
    """
    Main pipeline to load and merge NHANES datasets based on the configuration map.
    """
    print("--- 1. STARTING DATA INGESTION ---")

    # 1. Initialize the Backbone: Demographics
    # NHANES uses SEQN (Sequence Number) as the unique respondent identifier.
    demo_key = "DEMO_J"
    demo_path = find_file(demo_key)

    if not demo_path:
        raise FileNotFoundError(
            f"CRITICAL: {demo_key} file not found in {config.DATA_DIR}"
        )

    print(f"Loading Primary Backbone: {demo_path.name}")

    # Read SAS Transport file
    df = pd.read_sas(str(demo_path))

    # Subset demographics to relevant columns defined in config
    target_cols = config.NHANES_MAP[demo_key]
    available_cols = [c for c in target_cols if c in df.columns]
    df = df[available_cols]

    # 2. Iterative Merge of Auxiliary Files
    for file_key, columns_to_keep in config.NHANES_MAP.items():
        # Skip demographics as it's already the base dataframe
        if file_key == demo_key:
            continue

        file_path = find_file(file_key)

        if not file_path:
            print(f"WARNING: File {file_key} not found. Skipping associated features.")
            continue

        print(f"Merging features from: {file_path.name}...")

        # Load auxiliary dataset
        aux_df = pd.read_sas(str(file_path))

        # Filter for requested columns that actually exist in the file
        # Intersection ensures robustness against minor NHANES version differences
        valid_cols = list(set(columns_to_keep) & set(aux_df.columns))

        # Ensure SEQN is present for the merge operation
        if "SEQN" not in valid_cols:
            valid_cols.append("SEQN")

        aux_df = aux_df[valid_cols]

        # 3. Left Join Operation
        # We use 'left' join to preserve all subjects from the demographic backbone.
        # Missing values in auxiliary files are filled with NaN.
        df = pd.merge(df, aux_df, on="SEQN", how="left")

    print(f"--- DATA LOAD COMPLETE. Final Shape: {df.shape} ---")
    return df


if __name__ == "__main__":
    # Test execution
    data = load_raw_data()
    print(data.head())
    print(data.info())
    print(data.isnull().sum())
    print(data["WTMEC2YR"].sum())
