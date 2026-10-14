"""Statistical Analysis for Active Inference Meta-Pragmatic Framework.

This module provides statistical analysis functions for evaluating Active Inference
algorithms, including descriptive statistics, hypothesis testing, correlation analysis,
and confidence interval calculations.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
from numpy.typing import NDArray
from scipy import stats
from utils.exceptions import ValidationError
from utils.logging import get_logger

logger = get_logger(__name__)


class StatisticalAnalyzer:
    """Statistical analysis toolkit for Active Inference research.

    Provides comprehensive statistical methods for analyzing algorithm performance,
    model comparisons, and theoretical validation.
    """

    def __init__(self, alpha: float = 0.05) -> None:
        """Initialize statistical analyzer.

        Args:
            alpha: Significance level for hypothesis tests
        """
        if not np.isfinite(alpha) or not 0 < alpha < 1:
            raise ValidationError("alpha must be in (0,1)")
        self.alpha = alpha
        logger.info(f"Initialized statistical analyzer with alpha={alpha}")

    @staticmethod
    def _sample(data: NDArray, name: str = "data", minimum: int = 2) -> NDArray:
        """Require independent units in a one-dimensional finite sample."""
        data = np.asarray(data, dtype=float)
        if data.ndim != 1 or data.size < minimum or not np.all(np.isfinite(data)):
            raise ValidationError(
                f"{name} must be a finite 1-D sample with at least {minimum} values"
            )
        return data

    def calculate_descriptive_stats(
        self, data: NDArray
    ) -> Dict[str, Union[float, int]]:
        """Calculate comprehensive descriptive statistics.

        Args:
            data: Input data array

        Returns:
            Dictionary containing descriptive statistics
        """
        try:
            data = self._sample(data)
            if data.size == 0:
                raise ValidationError("Cannot calculate statistics for empty data")

            # Validate minimum sample size for meaningful statistics
            if data.size < 2:
                raise ValidationError(
                    f"Need at least 2 data points for statistical calculations, got {data.size}"
                )

            # Use ddof=1 for sample statistics, but only if we have enough data
            ddof = 1 if data.size > 1 else 0

            stats_dict = {
                "count": int(data.size),
                "mean": float(np.mean(data)),
                "std": float(np.std(data, ddof=ddof)),  # Sample standard deviation
                "var": float(np.var(data, ddof=ddof)),  # Sample variance
                "median": float(np.median(data)),
                "min": float(np.min(data)),
                "max": float(np.max(data)),
                "range": float(np.max(data) - np.min(data)),
                "q25": float(np.percentile(data, 25)),  # 25th percentile
                "q75": float(np.percentile(data, 75)),  # 75th percentile
                "iqr": float(np.subtract(*np.percentile(data, [75, 25]))),  # IQR
            }

            # Only calculate higher-order statistics if we have enough data to be meaningful
            if data.size >= 3 and np.ptp(data) > 0:
                try:
                    stats_dict["skewness"] = float(stats.skew(data))
                    stats_dict["kurtosis"] = float(stats.kurtosis(data))
                except (ValueError, RuntimeWarning):
                    # Handle cases where skewness/kurtosis calculation fails
                    stats_dict["skewness"] = 0.0
                    stats_dict["kurtosis"] = 0.0
            else:
                stats_dict["skewness"] = 0.0
                stats_dict["kurtosis"] = 0.0

            logger.debug(
                f"Calculated descriptive statistics for {data.size} data points"
            )
            return stats_dict

        except Exception as e:
            logger.error(f"Error calculating descriptive statistics: {e}")
            raise ValidationError(
                f"Descriptive statistics calculation failed: {e}"
            ) from e

    def calculate_correlation(
        self, x: NDArray, y: NDArray, method: str = "pearson"
    ) -> Dict[str, Union[float, int]]:
        """Calculate correlation between two variables.

        Args:
            x: First variable data
            y: Second variable data
            method: Correlation method ('pearson', 'spearman', 'kendall')

        Returns:
            Dictionary containing correlation results
        """
        try:
            x, y = self._sample(x, "x"), self._sample(y, "y")
            if np.ptp(x) == 0 or np.ptp(y) == 0:
                raise ValidationError(
                    "Correlation is undefined for a constant variable"
                )

            if len(x) != len(y):
                raise ValidationError("Correlation variables must have same length")

            if method == "pearson":
                corr_coef, p_value = stats.pearsonr(x, y)
            elif method == "spearman":
                corr_coef, p_value = stats.spearmanr(x, y)
            elif method == "kendall":
                corr_coef, p_value = stats.kendalltau(x, y)
            else:
                raise ValidationError(f"Unknown correlation method: {method}")

            correlation = {
                "correlation": float(corr_coef),
                "p_value": float(p_value),
                "method": method,
                "significant": bool(p_value < self.alpha),
                "sample_size": len(x),
                "interpretation": self._interpret_correlation(corr_coef, p_value),
            }

            logger.debug(
                f"Calculated {method} correlation: r={corr_coef:.3f}, p={p_value:.3f}"
            )
            return correlation

        except Exception as e:
            logger.error(f"Error calculating correlation: {e}")
            raise ValidationError(f"Correlation calculation failed: {e}") from e

    def _interpret_correlation(self, coeff: float, p_value: float) -> str:
        """Interpret correlation results."""
        strength = "weak"
        if abs(coeff) >= 0.7:
            strength = "strong"
        elif abs(coeff) >= 0.3:
            strength = "moderate"

        direction = "positive" if coeff > 0 else "negative"

        significance = "significant" if p_value < self.alpha else "not significant"

        return f"{strength} {direction} correlation ({significance})"

    def calculate_confidence_interval(
        self,
        data: NDArray,
        confidence_level: Optional[float] = None,
        confidence: Optional[float] = None,
    ) -> Dict[str, Union[float, List[float]]]:
        """Calculate confidence interval for mean.

        Args:
            data: Input data array
            confidence: Confidence level (0.95 for 95% CI)

        Returns:
            Dictionary containing confidence interval results
        """
        try:
            data = self._sample(data)

            # Validate input data
            if data.size == 0:
                raise ValidationError(
                    "Cannot calculate confidence interval for empty data"
                )

            # Handle parameter name compatibility
            if confidence_level is not None and confidence is not None:
                raise ValidationError(
                    "Cannot specify both 'confidence_level' and 'confidence' parameters"
                )
            elif confidence_level is not None:
                conf_level = confidence_level
            elif confidence is not None:
                conf_level = confidence
            else:
                conf_level = 0.95

            if not np.isfinite(conf_level) or not 0 < conf_level < 1:
                raise ValidationError("Confidence level must be in (0,1)")
            n = len(data)

            mean = np.mean(data)

            std_err = stats.sem(data)  # Standard error of the mean

            # t-distribution critical value
            t_crit = stats.t.ppf((1 + conf_level) / 2, n - 1)

            margin_error = t_crit * std_err
            ci_lower = mean - margin_error
            ci_upper = mean + margin_error

            confidence_interval = {
                "mean": float(mean),
                "confidence_level": conf_level,
                "sample_size": n,
                "standard_error": float(std_err),
                "margin_error": float(margin_error),
                "lower_bound": float(ci_lower),
                "upper_bound": float(ci_upper),
                "ci_range": [float(ci_lower), float(ci_upper)],
                "interpretation": f"{conf_level * 100:.0f}% CI: [{ci_lower:.3f}, {ci_upper:.3f}]",
            }

            logger.debug(
                f"Calculated {conf_level * 100:.0f}% CI: mean={mean:.3f}, range=[{ci_lower:.3f}, {ci_upper:.3f}]"  # noqa: E501
            )
            return confidence_interval

        except Exception as e:
            logger.error(f"Error calculating confidence interval: {e}")
            raise ValidationError(f"Confidence interval calculation failed: {e}") from e

    def anova_test(self, *groups: NDArray) -> Dict[str, Union[float, bool, str]]:
        """Perform one-way ANOVA test.

        Args:
            *groups: Variable number of data arrays (groups to compare)

        Returns:
            Dictionary containing ANOVA test results
        """
        try:
            if len(groups) < 2:
                raise ValidationError("ANOVA requires at least 2 groups")

            # Convert to list and validate
            group_data = [self._sample(g, "ANOVA group") for g in groups]

            # Perform ANOVA
            f_stat, p_value = stats.f_oneway(*group_data)

            anova_result = {
                "test": "One-way ANOVA",
                "f_statistic": float(f_stat),
                "p_value": float(p_value),
                "significant": bool(p_value < self.alpha),
                "n_groups": len(groups),
                "group_sizes": [len(g) for g in group_data],
                "total_sample_size": sum(len(g) for g in group_data),
                "interpretation": self._interpret_anova(p_value),
                "post_hoc_needed": bool(p_value < self.alpha),
            }

            logger.debug(
                f"ANOVA test: F={f_stat:.3f}, p={p_value:.3f}, significant={p_value < self.alpha}"
            )
            return anova_result

        except Exception as e:
            logger.error(f"Error performing ANOVA test: {e}")
            raise ValidationError(f"ANOVA test failed: {e}") from e

    def _interpret_anova(self, p_value: float) -> str:
        """Interpret ANOVA results."""
        if p_value < self.alpha:
            return (
                "Significant differences found between groups (reject null hypothesis)"
            )
        else:
            return "No significant differences found between groups (fail to reject null hypothesis)"

    def perform_t_test(
        self, group1: NDArray, group2: NDArray, test_type: str = "independent"
    ) -> Dict[str, Union[float, bool, str]]:
        """Perform t-test between two groups.

        Args:
            group1: First group data
            group2: Second group data
            paired: Whether to perform paired t-test

        Returns:
            Dictionary containing t-test results
        """
        try:
            if test_type not in ["paired", "independent"]:
                raise ValidationError(
                    f"test_type must be 'paired' or 'independent', got '{test_type}'"
                )

            g1, g2 = self._sample(group1, "Group 1"), self._sample(group2, "Group 2")

            # Validate minimum sample sizes to prevent degrees of freedom issues
            if len(g1) < 2:
                raise ValidationError(
                    f"Group 1 must have at least 2 observations, got {len(g1)}"
                )
            if len(g2) < 2:
                raise ValidationError(
                    f"Group 2 must have at least 2 observations, got {len(g2)}"
                )

            if test_type == "paired":
                if len(g1) != len(g2):
                    raise ValidationError(
                        f"Paired t-test requires equal sample sizes, got {len(g1)} vs {len(g2)}"
                    )
                t_stat, p_value = (
                    stats.ttest_rel(g1, g2)
                    if np.std(g1 - g2, ddof=1) > 0
                    else (float("nan"), float("nan"))
                )
                test_name = "Paired t-test"
            else:  # test_type == "independent"
                t_stat, p_value = (
                    stats.ttest_ind(g1, g2, equal_var=False)
                    if np.var(g1) + np.var(g2) > 0
                    else (float("nan"), float("nan"))
                )  # Welch's t-test
                test_name = "Independent t-test (Welch)"

            # Calculate effect size (Cohen's d) with safe variance calculation
            mean_diff = np.mean(g1) - np.mean(g2)

            # Use ddof=1 for sample variance, but handle edge cases
            var1 = np.var(g1, ddof=1) if len(g1) > 1 else 0
            var2 = np.var(g2, ddof=1) if len(g2) > 1 else 0

            # Calculate pooled standard deviation safely
            pooled_var = ((len(g1) - 1) * var1 + (len(g2) - 1) * var2) / (
                len(g1) + len(g2) - 2
            )
            pooled_std = np.sqrt(pooled_var) if pooled_var > 0 else 0

            cohens_d = abs(mean_diff) / pooled_std if pooled_std > 0 else float("nan")
            signed_d = mean_diff / pooled_std if pooled_std > 0 else None
            df_effect = len(g1) + len(g2) - 2
            paired_std = (
                float(np.std(g1 - g2, ddof=1)) if test_type == "paired" else None
            )
            paired_d_z = (
                float(mean_diff / paired_std)
                if paired_std is not None and paired_std > 0
                else None
            )

            t_test_result = {
                "test": test_name,
                "test_type": test_type,
                "t_statistic": float(t_stat) if np.isfinite(t_stat) else None,
                "p_value": float(p_value) if np.isfinite(p_value) else None,
                "significant": bool(np.isfinite(p_value) and p_value < self.alpha),
                "mean_difference": float(mean_diff),
                "cohens_d": float(cohens_d) if np.isfinite(cohens_d) else None,
                "signed_cohens_d": float(signed_d) if signed_d is not None else None,
                "hedges_g": (
                    float(signed_d * (1 - 3 / (4 * df_effect - 1)))
                    if signed_d is not None
                    else None
                ),
                "paired_d_z": paired_d_z,
                "effect_size_definition": "pooled-SD d; paired_d_z uses SD of within-pair differences",
                "test_defined": bool(np.isfinite(t_stat) and np.isfinite(p_value)),
                "group1_size": len(g1),
                "group2_size": len(g2),
                "effect_size_interpretation": (
                    self._interpret_effect_size(cohens_d)
                    if np.isfinite(cohens_d)
                    else "undefined (zero variance)"
                ),
                "interpretation": (
                    self._interpret_t_test(p_value, cohens_d)
                    if np.isfinite(t_stat) and np.isfinite(p_value)
                    else "Undefined t-test (zero variance of the relevant sampling unit)"
                ),
            }

            logger.debug(
                f"{test_name}: t={t_stat:.3f}, p={p_value:.3f}, d={cohens_d:.3f}"
            )
            return t_test_result

        except Exception as e:
            logger.error(f"Error performing t-test: {e}")
            raise ValidationError(f"t-test failed: {e}") from e

    def _interpret_effect_size(self, cohens_d: float) -> str:
        """Use conventional descriptive labels, not practical-significance claims."""
        magnitude = abs(cohens_d)
        if magnitude >= 0.8:
            return "large effect"
        if magnitude >= 0.5:
            return "medium effect"
        if magnitude >= 0.2:
            return "small effect"
        return "negligible effect"

    def holm_adjust(self, p_values: NDArray) -> List[float]:
        """Family-wise error correction without requiring test independence."""
        p = np.asarray(p_values, dtype=float)
        if (
            p.ndim != 1
            or not p.size
            or np.any(~np.isfinite(p))
            or np.any((p < 0) | (p > 1))
        ):
            raise ValidationError("p-values must be a nonempty vector in [0,1]")
        order = np.argsort(p)
        corrected = np.minimum(
            1, np.maximum.accumulate((p.size - np.arange(p.size)) * p[order])
        )
        result = np.empty_like(p)
        result[order] = corrected
        return result.tolist()

    def bootstrap_mean_interval(
        self,
        data: NDArray,
        confidence: float = 0.95,
        n_resamples: int = 5000,
        seed: int = 42,
    ) -> Dict:
        """Percentile bootstrap CI for the mean over independent replicates.

        For paired differences, pass one difference per independent seed.
        This does not treat episodes within a seed as independent units.
        """
        sample = self._sample(data)
        if not np.isfinite(confidence) or not 0 < confidence < 1:
            raise ValidationError("Confidence must be in (0,1)")
        if not isinstance(n_resamples, (int, np.integer)) or n_resamples < 100:
            raise ValidationError("Use at least 100 bootstrap resamples")
        rng = np.random.default_rng(seed)
        means = np.empty(n_resamples)
        for start in range(0, n_resamples, 256):
            stop = min(start + 256, n_resamples)
            means[start:stop] = rng.choice(
                sample, size=(stop - start, sample.size), replace=True
            ).mean(axis=1)
        lower, upper = np.quantile(means, [(1 - confidence) / 2, (1 + confidence) / 2])
        return {
            "mean": float(sample.mean()),
            "lower_bound": float(lower),
            "upper_bound": float(upper),
            "confidence_level": confidence,
            "sample_size": sample.size,
            "method": "percentile bootstrap",
            "n_resamples": n_resamples,
            "seed": seed,
        }

    def _interpret_t_test(self, p_value: float, cohens_d: float) -> str:
        """Interpret t-test results."""
        significance = "significant" if p_value < self.alpha else "not significant"
        effect = self._interpret_effect_size(cohens_d)

        return f"{significance} difference with {effect} (p={p_value:.3f}, d={cohens_d:.3f})"

    def analyze_algorithm_performance(
        self,
        algorithm_results: Dict[str, List[float]],
        paired: bool = False,
        higher_is_better: bool = True,
    ) -> Dict[str, Union[Dict, List]]:
        """Analyze performance of multiple algorithms.

        Args:
            algorithm_results: Dictionary mapping algorithm names to performance scores

        Returns:
            Dictionary containing comparative performance analysis
        """
        try:
            if not algorithm_results:
                raise ValidationError("No algorithm results provided")

            # Calculate statistics for each algorithm
            algorithm_stats = {}
            performance_data = []

            for name, scores in algorithm_results.items():
                stats_dict = self.calculate_descriptive_stats(scores)
                algorithm_stats[name] = stats_dict
                performance_data.append(scores)

            # Perform statistical comparison if multiple algorithms
            comparison = {}
            if len(algorithm_results) > 1:
                # ANOVA to test if algorithms differ
                anova_result = self.anova_test(*performance_data)
                comparison["anova"] = anova_result

                # Pairwise t-tests
                pairwise_tests = {}
                algorithm_names = list(algorithm_results.keys())

                for i, name1 in enumerate(algorithm_names[:-1]):
                    for name2 in algorithm_names[i + 1 :]:
                        t_test = self.perform_t_test(
                            algorithm_results[name1],
                            algorithm_results[name2],
                            test_type="paired" if paired else "independent",
                        )
                        pairwise_tests[f"{name1}_vs_{name2}"] = t_test

                adjusted = self.holm_adjust(
                    [v["p_value"] for v in pairwise_tests.values()]
                )
                for result, adjusted_p in zip(pairwise_tests.values(), adjusted):
                    result["p_value_holm"] = adjusted_p
                    result["significant_holm"] = adjusted_p < self.alpha
                comparison["pairwise_t_tests"] = pairwise_tests
                comparison["multiplicity_correction"] = "Holm (all pairwise tests)"
                if paired:
                    comparison.pop(
                        "anova", None
                    )  # Independent-groups ANOVA does not fit matched runs.

            analysis = {
                "algorithm_statistics": algorithm_stats,
                "comparison": comparison,
                "best_performing": (max if higher_is_better else min)(
                    algorithm_stats.keys(), key=lambda k: algorithm_stats[k]["mean"]
                ),
                "ranking": sorted(
                    algorithm_stats.keys(),
                    key=lambda k: algorithm_stats[k]["mean"],
                    reverse=higher_is_better,
                ),
                "sample_sizes": {
                    name: len(scores) for name, scores in algorithm_results.items()
                },
            }

            logger.info(f"Analyzed performance of {len(algorithm_results)} algorithms")
            return analysis

        except Exception as e:
            logger.error(f"Error analyzing algorithm performance: {e}")
            raise ValidationError(f"Algorithm performance analysis failed: {e}") from e


# Convenience functions for direct use
def calculate_descriptive_stats(data: NDArray) -> Dict[str, Union[float, int]]:
    """Convenience function for descriptive statistics."""
    analyzer = StatisticalAnalyzer()
    return analyzer.calculate_descriptive_stats(data)


def calculate_correlation(
    x: NDArray, y: NDArray, method: str = "pearson"
) -> Dict[str, Union[float, int]]:
    """Convenience function for correlation analysis."""
    analyzer = StatisticalAnalyzer()
    return analyzer.calculate_correlation(x, y, method)


def calculate_confidence_interval(
    data: NDArray, confidence: float = 0.95
) -> Dict[str, Union[float, List[float]]]:
    """Convenience function for confidence intervals."""
    analyzer = StatisticalAnalyzer()
    return analyzer.calculate_confidence_interval(data, confidence)


def anova_test(*groups: NDArray) -> Dict[str, Union[float, bool, str]]:
    """Convenience function for ANOVA testing."""
    analyzer = StatisticalAnalyzer()
    return analyzer.anova_test(*groups)


def demonstrate_statistical_analysis() -> Dict[str, Union[str, Dict]]:
    """Demonstrate statistical analysis capabilities.

    Returns:
        Dictionary containing statistical analysis demonstrations
    """
    analyzer = StatisticalAnalyzer()

    # Generate sample data
    rng = np.random.default_rng(42)
    data1 = rng.normal(10, 2, 50)
    data2 = rng.normal(12, 2, 50)
    data3 = rng.normal(8, 3, 50)

    # Demonstrate descriptive statistics
    desc_stats = analyzer.calculate_descriptive_stats(data1)

    # Demonstrate correlation
    correlation = analyzer.calculate_correlation(data1, data2)

    # Demonstrate confidence interval
    ci = analyzer.calculate_confidence_interval(data1)

    # Demonstrate ANOVA
    anova = analyzer.anova_test(data1, data2, data3)

    # Demonstrate algorithm comparison
    algorithm_results = {
        "Algorithm_A": rng.normal(0.85, 0.05, 30),
        "Algorithm_B": rng.normal(0.78, 0.08, 30),
        "Algorithm_C": rng.normal(0.92, 0.03, 30),
    }
    performance_analysis = analyzer.analyze_algorithm_performance(algorithm_results)

    demonstration = {
        "descriptive_statistics": desc_stats,
        "correlation_analysis": correlation,
        "confidence_interval": ci,
        "anova_test": anova,
        "algorithm_comparison": performance_analysis,
        "purpose": """
        These statistical analysis functions enable rigorous evaluation of Active Inference
        algorithms, model comparisons, and theoretical validation with proper statistical
        significance testing and effect size calculations.
        """,
    }

    logger.info("Demonstrated statistical analysis capabilities")
    return demonstration
