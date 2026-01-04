import numpy as np
import pandas as pd


class SurveyAnalyzer:
    """
    A utility class for performing statistical analysis on survey data
    accounting for complex sampling weights.
    """

    @staticmethod
    def get_weighted_mean(df, column, weight_col="WTMEC2YR"):
        """
        Calculate the population-representative mean.
        """
        weights = df[weight_col]
        values = df[column]
        return np.average(values, weights=weights)

    @staticmethod
    def get_weighted_prevalence(df, target_col, threshold, weight_col="WTMEC2YR"):
        """
        Calculate the prevalence (percentage) of a condition based on a threshold.
        Example: PHQ-9 score >= 10.
        """
        binary_condition = (df[target_col] >= threshold).astype(int)
        weights = df[weight_col]
        return (np.sum(binary_condition * weights) / np.sum(weights)) * 100

    @staticmethod
    def get_weighted_stats(df, column, weight_col="WTMEC2YR"):
        """
        Compute a summary of weighted statistics for a continuous variable.
        """
        # Simplified implementation of weighted quantiles could be added here
        mean = SurveyAnalyzer.get_weighted_mean(df, column, weight_col)
        return {"weighted_mean": mean}

    @staticmethod
    def get_weighted_correlation_matrix(df, cols, weight_col="MEC_Weight"):
        """
        Computes the Pearson correlation coefficient matrix accounting for survey weights.
        Standard df.corr() ignores weights, leading to biased estimates in NHANES.
        """
        # Ensure we work with available columns only
        valid_cols = [c for c in cols if c in df.columns]
        mat = df[valid_cols].values
        weights = df[weight_col].values

        # Weighted Covariance Function
        def weighted_cov(x, y, w):
            mean_x = np.average(x, weights=w)
            mean_y = np.average(y, weights=w)
            return np.sum(w * (x - mean_x) * (y - mean_y)) / np.sum(w)

        n_cols = len(valid_cols)
        corr_matrix = np.eye(n_cols)  # Diagonal is always 1.0

        for i in range(n_cols):
            for j in range(i + 1, n_cols):
                c1 = mat[:, i]
                c2 = mat[:, j]

                # Weighted Correlation Formula: Cov(X,Y,w) / sqrt(Var(X,w) * Var(Y,w))
                cov_xy = weighted_cov(c1, c2, weights)
                cov_xx = weighted_cov(c1, c1, weights)
                cov_yy = weighted_cov(c2, c2, weights)

                rho = cov_xy / np.sqrt(cov_xx * cov_yy)

                # Fill symmetric matrix
                corr_matrix[i, j] = rho
                corr_matrix[j, i] = rho

        return pd.DataFrame(corr_matrix, index=valid_cols, columns=valid_cols)


# src/analysis.py


def weighted_correlation_matrix(
    df: pd.DataFrame, weight_col: str, features: list
) -> pd.DataFrame:
    """
    Calculates the weighted Pearson correlation matrix for specific features.

    Why: Standard pandas .corr() does not support survey weights.
    In NHANES, ignoring weights biases the result towards the sample,
    not the US population.

    Args:
        df: Dataframe containing features and weights.
        weight_col: Name of the weight column (e.g., 'WTMEC2YR').
        features: List of numerical columns to correlate.

    Returns:
        pd.DataFrame: Weighted correlation matrix.
    """
    # Filter valid data (drop NaNs in relevant columns)
    valid_data = df[features + [weight_col]].dropna()

    data = valid_data[features].values
    weights = valid_data[weight_col].values

    # Calculate weighted covariance matrix
    # Note: cov(X, Y, w) = sum(w * (x - mean_x) * (y - mean_y)) / sum(w)
    mean = np.average(data, axis=0, weights=weights)
    xm = data - mean

    # Weighted covariance
    cov = np.dot(weights * xm.T, xm) / np.sum(weights)

    # Calculate standard deviations (sqrt of diagonal of covariance)
    sqr_weights = np.sqrt(np.diag(cov))

    # Convert covariance to correlation: corr = cov / (std_x * std_y)
    corr_matrix = cov / np.outer(sqr_weights, sqr_weights)

    # Return as DataFrame for readability
    return pd.DataFrame(corr_matrix, index=features, columns=features)


# src/analysis.py


def check_sample_sufficiency(
    df: pd.DataFrame, group_col: str, min_obs: int = 30
) -> None:
    """
    Validates if the sample size for each subgroup is sufficient for analysis.

    According to NHANES analytic guidelines, estimates should not be reported
    if the unweighted sample size is < 30 or the relative standard error is > 30%.

    Args:
        df (pd.DataFrame): The dataset.
        group_col (str): The column used for grouping (e.g., 'Gender', 'SMI_Category').
        min_obs (int): Minimum required observations per group (default 30).

    Raises:
        ValueError: If any group has fewer observations than min_obs.
    """
    counts = df[group_col].value_counts()
    print(f"--- Sample Size Check for '{group_col}' ---")
    print(counts)

    if (counts < min_obs).any():
        insufficient_groups = counts[counts < min_obs].index.tolist()
        raise ValueError(
            f"❌ STOP: Insufficient sample size for groups {insufficient_groups}. "
            f"Analysis cannot proceed as results will be statistically insignificant."
        )
    print("✅ Sample size is sufficient. Proceeding with analysis.\n")


def get_weighted_depression_rate(
    df: pd.DataFrame,
    group_col: str,
    target_col: str = "Depression_Flag",
    weight_col: str = "MEC_Weight",
) -> pd.DataFrame:
    """
    Calculates the weighted prevalence of depression for given groups
    with 95% Confidence Intervals (CI).

    Why this matters:
    A simple mean() is biased because NHANES oversamples certain demographics.
    We must use weights to represent the true US population.

    Args:
        df (pd.DataFrame): Dataframe containing the data.
        group_col (str): Variable to group by (e.g., 'Gender').
        target_col (str): Binary target (1=Depressed, 0=Normal).
        weight_col (str): Survey weight column name.

    Returns:
        pd.DataFrame: Summary table with Mean, Standard Error, and 95% CI.
    """
    results = []

    # Drop rows where target or group is NaN to avoid errors
    clean_df = df.dropna(subset=[group_col, target_col, weight_col])

    for group in clean_df[group_col].unique():
        sub_df = clean_df[clean_df[group_col] == group]

        # Using statsmodels for weighted statistics
        weighted_stats = DescrStatsW(sub_df[target_col], weights=sub_df[weight_col])

        mean = weighted_stats.mean
        std_err = weighted_stats.std_mean

        # Calculate 95% Confidence Interval
        # formula: mean ± 1.96 * standard_error
        ci_lower = mean - (1.96 * std_err)
        ci_upper = mean + (1.96 * std_err)

        results.append(
            {
                group_col: group,
                "Weighted_Mean": mean,
                "Standard_Error": std_err,
                "CI_Lower": ci_lower,
                "CI_Upper": ci_upper,
                "N_Unweighted": len(sub_df),
            }
        )

    return pd.DataFrame(results).sort_values("Weighted_Mean", ascending=False)
