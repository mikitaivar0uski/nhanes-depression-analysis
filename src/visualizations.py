import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


def plot_phq9_distribution(df, weight_col="MEC_Weight"):
    """
    Plots the Population-Representative (Weighted) distribution of PHQ-9 scores.
    """
    plt.figure(figsize=(10, 6))

    # Weighted Histogram using standard weights parameter
    sns.histplot(
        data=df,
        x="PHQ9_Score",
        weights=weight_col,
        binwidth=1,
        color="#2b7bba",  # Professional medical blue
        alpha=0.7,
        label="US Adult Population (Weighted)",
        stat="probability",
    )

    plt.axvline(
        10,
        color="red",
        linestyle="--",
        linewidth=2,
        label="Clinical Depression Cutoff (>=10)",
    )

    plt.title(
        "Distribution of Depression Scores (US Adult Population)", fontsize=14, pad=15
    )
    plt.xlabel("PHQ-9 Score", fontsize=12)
    plt.ylabel("Prevalence (Probability)", fontsize=12)
    plt.legend(loc="upper right")
    plt.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.show()


def plot_weighted_risk_factor(
    df, x_col, target_col, weight_col="MEC_Weight", xlabel=None
):
    """
    Plots the weighted mean probability of the target (Depression) by category.
    Used for Socioeconomic analysis (Income, Education).
    """
    # 1. Calculate Weighted Means per Group
    # We can't use standard groupby().mean() directly with weights.
    # We calculate: Sum(Target * Weight) / Sum(Weight) for each group.

    def weighted_mean(x):
        return np.average(x[target_col], weights=x[weight_col]) * 100  # In percent

    # Group by the factor and apply custom weighted mean
    grouped = df.groupby(x_col).apply(weighted_mean).reset_index(name="Depression_Rate")

    # 2. Plot
    plt.figure(figsize=(10, 6))
    sns.barplot(
        data=grouped,
        x=x_col,
        y="Depression_Rate",
        hue=x_col,
        palette="Blues_d",
        legend=False,
    )

    plt.title(f"Depression Prevalence by {xlabel if xlabel else x_col}", fontsize=14)
    plt.ylabel("Prevalence (%)", fontsize=12)
    plt.xlabel(xlabel if xlabel else x_col, fontsize=12)
    plt.ylim(0, grouped["Depression_Rate"].max() * 1.2)  # Add breathing room on top

    # Add value labels on bars
    for index, row in grouped.iterrows():
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


def plot_correlation_heatmap(corr_matrix):
    """
    Plots a professional triangular heatmap for the weighted correlation matrix.
    """
    plt.figure(figsize=(14, 12))

    # Create a mask to hide the upper triangle (redundant information)
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))

    # Custom diverging palette (Blue = Negative, Red = Positive)
    cmap = sns.diverging_palette(230, 20, as_cmap=True)

    sns.heatmap(
        corr_matrix,
        mask=mask,
        cmap=cmap,
        vmax=1.0,
        vmin=-1.0,
        center=0,
        square=True,
        linewidths=0.5,
        cbar_kws={"shrink": 0.5},
        annot=True,  # Show numbers
        fmt=".2f",  # 2 decimal places
        annot_kws={"size": 9},
    )

    plt.title("Weighted Correlation Matrix (Risk Factors)", fontsize=16, pad=20)
    plt.tight_layout()
    plt.show()


def plot_biological_distributions(df, cols, log_scale=False):
    """
    Uses Boxenplots to better handle heavy-tailed distributions in medical data.
    Optionally applies log-scale to x-axis for biomarkers like CRP/Lead.
    """
    valid_cols = [c for c in cols if c in df.columns]
    n = len(valid_cols)

    fig, axes = plt.subplots(nrows=n, ncols=1, figsize=(12, 5 * n))

    for i, col in enumerate(valid_cols):
        # Boxenplot (Letter-value plot) is superior for large datasets with outliers
        sns.boxenplot(
            data=df,
            x=col,
            ax=axes[i],
            color="#4c72b0",
            k_depth="trustworthy",  # Optimizes detail based on sample size
        )

        # Overlay a Strip Plot (jittered points) to show ACTUAL data density
        # We sample only 2000 points if dataset is huge to avoid rendering lag
        plot_data = df if len(df) < 2000 else df.sample(2000, random_state=42)
        sns.stripplot(
            data=plot_data,
            x=col,
            ax=axes[i],
            color="black",
            alpha=0.3,
            size=2,
            jitter=True,
        )

        title = f"Distribution of {col}"
        if log_scale:
            axes[i].set_xscale("log")
            title += " (Log Scale)"

        axes[i].set_title(title, fontsize=14)
        axes[i].set_xlabel("")

    plt.tight_layout()
    plt.show()
