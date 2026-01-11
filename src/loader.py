from pathlib import Path

import pandas as pd

from src import config
# Lazy import to avoid circular dependency if possible, or just import here
from src import preprocessing


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


def load_cycle(suffix: str) -> pd.DataFrame:
    """
    Loads one specific NHANES cycle (e.g., 2017-2018 with suffix '_J').
    """
    print(f"   -> Loading Cycle {suffix}...")
    
    # 1. Load Backbone (Demographics)
    demo_key = f"DEMO{suffix}"
    demo_path = find_file(demo_key)
    
    if not demo_path:
        print(f"      [SKIP] Backbone {demo_key} not found.")
        return pd.DataFrame() # Empty DF if no backbone

    # Load and clean DEMO
    df = pd.read_sas(str(demo_path))
    
    # Select cols based on GENERIC key "DEMO"
    target_cols = config.NHANES_MAP["DEMO"]
    available_demo = [c for c in target_cols if c in df.columns]
    df = df[available_demo]
    df["SEQN"] = df["SEQN"].astype(int)

    # 2. Merge Auxiliary Files
    for key, requested_cols in config.NHANES_MAP.items():
        if key == "DEMO":
            continue

        file_key = f"{key}{suffix}"
        path = find_file(file_key)

        if path:
            aux = pd.read_sas(str(path))

            # Get columns that actually exist in the file
            available_cols = [c for c in requested_cols if c in aux.columns]

            # Ensure SEQN is present for merging
            if "SEQN" not in available_cols and "SEQN" in aux.columns:
                available_cols.append("SEQN")

            if len(available_cols) <= 1: 
                # Only SEQN or empty
                continue

            aux = aux[available_cols]
            aux["SEQN"] = aux["SEQN"].astype(int)

            # Merge
            df = pd.merge(df, aux, on="SEQN", how="left")
        
        # We don't print missing files per cycle to avoid spam, 
        # unless it's a critical debugging session.
        
    if not df.columns.is_unique:
        dupes = df.columns[df.columns.duplicated()].tolist()
        print(f"      [ERROR] DUPLICATE COLUMNS in Cycle {suffix}: {dupes}")
        # Attempt to deduplicate by keeping first
        df = df.loc[:, ~df.columns.duplicated()]
        
    return df


def load_raw_data() -> pd.DataFrame:
    """
    Orchestrates the ETL process:
    1. Iterates through all cycles in config.CYCLES.
    2. Loads and merges data for each cycle.
    3. Concatenates all cycles into one big DataFrame.
    """
    print(f"--- STARTING DATA INGESTION from {config.DATA_DIR} ---")
    
    all_cycles_dfs = []
    
    for suffix in config.CYCLES:
        cycle_df = load_cycle(suffix)
        if not cycle_df.empty:
            print(f"      -> Cycle {suffix} loaded. Shape: {cycle_df.shape}")
            all_cycles_dfs.append(cycle_df)
    
    if not all_cycles_dfs:
        raise ValueError("No data loaded from any cycle!")
        
    final_df = pd.concat(all_cycles_dfs, axis=0, ignore_index=True)
    
    print(f"--- DATA LOADING COMPLETE. Final Shape: {final_df.shape} (Unique SEQN: {final_df['SEQN'].nunique()}) ---")
    return final_df


def load_processed_data(force_reload: bool = False) -> pd.DataFrame:
    """
    Loads the fully processed dataframe from cache if available.
    If not, it runs the full raw load + preprocessing pipeline and saves the result.
    
    Args:
        force_reload: If True, ignores cache and rebuilds from scratch.
    """
    cache_path = config.ROOT_DIR / "data" / "processed" / "nhanes_final_2011_2018.pkl"
    
    # Create processed directory if it doesn't exist
    if not cache_path.parent.exists():
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        
    if cache_path.exists() and not force_reload:
        print(f"🚀 Loading Cached Data from {cache_path}...")
        try:
            df = pd.read_pickle(cache_path)
            print(f"   -> Success! Loaded {len(df)} rows. (Time saved: ~4 mins)")
            return df
        except Exception as e:
            print(f"   [WARNING] Cache load failed ({e}). Rebuilding...")
            
    # Rebuild Pipeline
    print("⚙️  Cache miss or force reload. Running Full Data Pipeline...")
    df_raw = load_raw_data()
    df = preprocessing.run_full_preprocessing(df_raw)
    
    # Save to Cache
    try:
        print(f"💾 Saving processed data to {cache_path}...")
        df.to_pickle(cache_path)
    except Exception as e:
        print(f"   [WARNING] Could not save cache: {e}")
        
    return df
