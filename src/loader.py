from pathlib import Path

import pandas as pd

from src import config


def find_file(filename_key: str) -> Path:
    """Recursively searches for .xpt files in the configured DATA_DIR."""
    target_name = filename_key.lower()

    if not config.DATA_DIR.exists():
        print(f"Error: Directory {config.DATA_DIR} does not exist.")
        return None

    for file_path in config.DATA_DIR.rglob("*"):
        if (
            file_path.is_file()
            and file_path.stem.lower() == target_name
            and file_path.suffix.lower() == ".xpt"
        ):
            return file_path
    return None


def load_raw_data() -> pd.DataFrame:
    """Loads Demographics and merges all other files defined in NHANES_MAP."""
    print("--- DATA INGESTION ---")

    # Load Backbone (Demographics)
    demo_path = find_file("DEMO_J")
    if not demo_path:
        raise FileNotFoundError(f"CRITICAL: DEMO_J not found in {config.DATA_DIR}")

    df = pd.read_sas(str(demo_path))[config.NHANES_MAP["DEMO_J"]]

    # Merge Auxiliary Files
    for key, cols in config.NHANES_MAP.items():
        if key == "DEMO_J":
            continue

        path = find_file(key)
        if path:
            print(f"Merging: {key}...")
            aux = pd.read_sas(str(path))

            # Find intersection of requested columns and existing columns
            valid_cols = list(set(cols) & set(aux.columns))

            # Ensure SEQN is present for merging
            if "SEQN" not in valid_cols and "SEQN" in aux.columns:
                valid_cols.append("SEQN")

            if "SEQN" in valid_cols:
                df = pd.merge(df, aux[valid_cols], on="SEQN", how="left")
        else:
            print(f"Warning: {key} not found. Features will be missing.")

    print(f"Data Loaded. Shape: {df.shape}")
    return df
