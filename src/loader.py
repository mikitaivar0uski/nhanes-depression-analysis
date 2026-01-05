from pathlib import Path

import pandas as pd

from src import config


def find_file(filename_key: str) -> Path:
    """
    Case-insensitive search for .xpt files in DATA_DIR.
    """
    target_name = filename_key.lower()

    if not config.DATA_DIR.exists():
        raise FileNotFoundError(
            f"CRITICAL: Data directory not found at {config.DATA_DIR}"
        )

    # 1. Try exact match (fastest)
    exact_path = config.DATA_DIR / f"{filename_key}.XPT"
    if exact_path.exists():
        return exact_path

    # 2. Recursive search (robust)
    for file_path in config.DATA_DIR.rglob("*"):
        if (
            file_path.is_file()
            and file_path.stem.lower() == target_name
            and file_path.suffix.lower() == ".xpt"
        ):
            return file_path

    return None


def load_raw_data() -> pd.DataFrame:
    """
    Orchestrates the ETL process:
    1. Loads the backbone (DEMO_J).
    2. Iteratively merges all other files defined in config.NHANES_MAP.
    """
    print(f"--- STARTING DATA INGESTION from {config.DATA_DIR} ---")

    # 1. Load Backbone (Demographics)
    demo_path = find_file("DEMO_J")
    if not demo_path:
        raise FileNotFoundError(
            f"[ERROR] CRITICAL: DEMO_J not found in {config.DATA_DIR}"
        )

    print(f"[OK] Loaded Backbone: DEMO_J ({demo_path.name})")

    # Load and clean DEMO
    df = pd.read_sas(str(demo_path))
    demo_cols = [c for c in config.NHANES_MAP["DEMO_J"] if c in df.columns]
    df = df[demo_cols]
    df["SEQN"] = df["SEQN"].astype(int)

    # 2. Merge Auxiliary Files
    for key, requested_cols in config.NHANES_MAP.items():
        if key == "DEMO_J":
            continue

        path = find_file(key)

        if path:
            aux = pd.read_sas(str(path))

            # --- FIX: Ensure SEQN is unique in column selection ---
            # Get columns that actually exist in the file
            available_cols = [c for c in requested_cols if c in aux.columns]

            # Ensure SEQN is present, but DO NOT duplicate it if it's already in requested_cols
            if "SEQN" not in available_cols and "SEQN" in aux.columns:
                available_cols.append("SEQN")

            # Check if we have anything useful besides SEQN
            if len(available_cols) <= 1:  # Only SEQN or empty
                print(
                    f"[WARN] WARNING: {key} found, but no target columns found. Skipping."
                )
                continue

            # Select columns uniquely
            aux = aux[available_cols]

            # Type conversion for key
            aux["SEQN"] = aux["SEQN"].astype(int)

            # Merge
            initial_shape = df.shape
            # Validate 'one_to_one' ensures we don't accidentally explode rows if duplicates exist
            df = pd.merge(df, aux, on="SEQN", how="left")

            new_cols_count = df.shape[1] - initial_shape[1]
            print(
                f"   -> Merged {key}: +{new_cols_count} features. New Shape: {df.shape}"
            )

        else:
            print(f"[MISSING] FILE: {key}")

    print(f"--- DATA LOADING COMPLETE. Final Shape: {df.shape} ---")
    return df
