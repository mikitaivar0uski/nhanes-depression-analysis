import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


def plot_weighted_risk_factor(
    df,
    x_col,
    target_col,
    weight_col="MEC_Weight",
    xlabel=None,
    palette=None,
    color=None,
):
    """
    Plots weighted prevalence.
    Now supports custom 'palette' (for ordinal data) or single 'color' (for nominal data).
    """

    # 1. Calculate Weighted Means
    def weighted_mean(x):
        w_sum = x[weight_col].sum()
        if w_sum == 0:
            return 0
        return np.average(x[target_col], weights=x[weight_col]) * 100

    grouped = (
        df[[x_col, target_col, weight_col]]
        .groupby(x_col, observed=False)
        .apply(weighted_mean, include_groups=False)
        .reset_index(name="Depression_Rate")
    )

    # 2. Plot Setup
    plt.figure(figsize=(10, 6))

    # Logic: If palette is given, use it (Gradient). If not, use solid color.
    if palette:
        sns.barplot(
            data=grouped,
            x=x_col,
            y="Depression_Rate",
            hue=x_col,
            palette=palette,
            legend=False,
        )
    else:
        # Default professional color if none provided
        plot_color = color if color else "#4c72b0"  # Deep Professional Blue
        sns.barplot(data=grouped, x=x_col, y="Depression_Rate", color=plot_color)

    plt.title(f"Depression Prevalence by {xlabel if xlabel else x_col}", fontsize=14)
    plt.ylabel("Prevalence (%)", fontsize=12)
    plt.xlabel(xlabel if xlabel else x_col, fontsize=12)
    plt.ylim(0, grouped["Depression_Rate"].max() * 1.25)

    # Labels
    for index, row in grouped.iterrows():
        if pd.isna(row.Depression_Rate) or row.Depression_Rate == 0:
            continue
        plt.text(
            index,
            row.Depression_Rate + 0.2,
            f"{row.Depression_Rate:.1f}%",
            color="black",
            ha="center",
            fontsize=11,
            fontweight="bold",
        )

    plt.tight_layout()
    plt.show()
