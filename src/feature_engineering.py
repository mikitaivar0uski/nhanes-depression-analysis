# src/feature_engineering.py

import pandas as pd


def calculate_body_composition_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Engineers body composition features, converting raw DXA grams to
    clinically relevant indices (SMI).

    Logic:
    1. Convert grams to kg.
    2. Calculate Skeletal Muscle Index (SMI) = ASM (kg) / Height (m)^2.
    3. Categorize SMI and Body Fat into ordered tiers (Low -> High).
    """
    df_clean = df.copy()

    # 1. Calculate SMI (Skeletal Muscle Index)
    # DXXAGM: Appendicular Skeletal Mass in grams -> convert to kg
    # BMXHT: Standing Height in cm -> convert to m
    df_clean["ASM_kg"] = df_clean["DXXAGM"] / 1000
    df_clean["Height_m"] = df_clean["BMXHT"] / 100

    # Formula: SMI = kg / m^2
    df_clean["SMI"] = df_clean["ASM_kg"] / (df_clean["Height_m"] ** 2)

    # 2. Binning with ORDER
    # We use qcut to divide into 3 classes: Low (33%), Normal (33%), High (33%)
    labels_muscle = ["Low Muscle", "Normal Muscle", "High Muscle"]
    labels_fat = ["Low Fat", "Normal Fat", "High Fat"]

    # Create categorical types with explicit order
    # This fixes the visualization issue where columns are mixed up
    muscle_order = pd.CategoricalDtype(categories=labels_muscle, ordered=True)
    fat_order = pd.CategoricalDtype(categories=labels_fat, ordered=True)

    df_clean["Muscle_Category"] = pd.qcut(
        df_clean["SMI"], q=3, labels=labels_muscle
    ).astype(muscle_order)

    # Assuming DXXTRFAT (Trunk Fat) or total fat for Fat Mass
    # Let's use Total Percent Fat if available (DXXPFT) or similar proxy
    # Here using DXXTRFAT (Trunk Fat grams) as proxy for illustration
    df_clean["Fat_Category"] = pd.qcut(
        df_clean["DXXTRFAT"], q=3, labels=labels_fat
    ).astype(fat_order)

    return df_clean
