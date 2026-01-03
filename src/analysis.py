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
