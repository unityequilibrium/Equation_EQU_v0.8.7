"""
Baseline comparison template for UET tests.

This module provides standard baseline models for comparison:
- Newtonian gravity
- ΛCDM cosmology
- Standard Model predictions

Usage:
    from research_uet.core.baselines import NewtonianBaseline, compare_to_baseline
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, Tuple

# Physical constants
G = 6.67430e-11  # m^3 kg^-1 s^-2
c = 299792458  # m/s
HBAR = 1.054571817e-34  # J s


@dataclass
class BaselineResult:
    """Result from baseline comparison."""

    model_name: str
    prediction: np.ndarray
    error: float


class NewtonianBaseline:
    """Standard Newtonian gravity baseline."""

    @staticmethod
    def rotation_velocity(r: np.ndarray, M: float) -> np.ndarray:
        """
        Newtonian prediction for rotation velocity.

        v = sqrt(GM/r)

        Args:
            r: Radial distances (m)
            M: Enclosed mass (kg)

        Returns:
            Predicted velocities (m/s)
        """
        return np.sqrt(G * M / r)

    @staticmethod
    def orbital_period(a: float, M: float) -> float:
        """
        Kepler's third law period.

        Args:
            a: Semi-major axis (m)
            M: Central mass (kg)

        Returns:
            Period (s)
        """
        return 2 * np.pi * np.sqrt(a**3 / (G * M))


class LCDMBaseline:
    """Standard ΛCDM cosmology baseline."""

    def __init__(
        self, H0: float = 67.4, Omega_m: float = 0.315, Omega_L: float = 0.685
    ):
        self.H0 = H0  # km/s/Mpc
        self.Omega_m = Omega_m
        self.Omega_L = Omega_L

    def hubble_parameter(self, z: float) -> float:
        """
        Hubble parameter at redshift z.

        H(z) = H0 * sqrt(Omega_m(1+z)^3 + Omega_L)
        """
        return self.H0 * np.sqrt(self.Omega_m * (1 + z) ** 3 + self.Omega_L)

    def luminosity_distance(self, z: float) -> float:
        """
        Luminosity distance in Mpc (simplified flat universe).
        """
        # Numerical integration would be needed for accuracy
        # This is a first-order approximation
        c_km = c / 1000  # km/s
        return c_km * z / self.H0 * (1 + 0.5 * z * (1 - self.Omega_m + self.Omega_L))


class StandardModelBaseline:
    """Standard Model predictions for particle physics."""

    # PDG 2024 values
    WEAK_MIXING_ANGLE = 0.23122  # sin^2(theta_W)
    MUON_G2_SM = 116591810e-11  # (g-2)/2

    @staticmethod
    def weak_mixing_angle() -> float:
        """Standard Model weak mixing angle."""
        return StandardModelBaseline.WEAK_MIXING_ANGLE

    @staticmethod
    def muon_magnetic_moment() -> float:
        """Standard Model muon (g-2)/2."""
        return StandardModelBaseline.MUON_G2_SM


def compare_to_baseline(
    observed: np.ndarray,
    uet_prediction: np.ndarray,
    baseline_prediction: np.ndarray,
    baseline_name: str = "Baseline",
) -> Dict[str, float]:
    """
    Compare UET to baseline model.

    Args:
        observed: Observed data
        uet_prediction: UET model prediction
        baseline_prediction: Standard model prediction
        baseline_name: Name of baseline model

    Returns:
        Dictionary with error metrics for both models
    """
    # Calculate errors
    uet_error = np.mean(np.abs(observed - uet_prediction) / np.abs(observed)) * 100
    baseline_error = (
        np.mean(np.abs(observed - baseline_prediction) / np.abs(observed)) * 100
    )

    improvement = baseline_error / uet_error if uet_error > 0 else float("inf")

    return {
        "uet_error_percent": uet_error,
        f"{baseline_name.lower()}_error_percent": baseline_error,
        "improvement_factor": improvement,
        "uet_is_better": uet_error < baseline_error,
    }


def sanity_check_wrong_kappa(
    test_function,
    correct_kappa: float = 0.1,
    wrong_kappa: float = 1000.0,
    expected_failure_threshold: float = 0.5,
) -> bool:
    """
    Sanity check: verify that wrong κ causes failure.

    Args:
        test_function: Function that returns error given kappa
        correct_kappa: The correct kappa value
        wrong_kappa: Intentionally wrong kappa
        expected_failure_threshold: Error threshold for "failure"

    Returns:
        True if sanity check passes (wrong kappa causes failure)
    """
    correct_error = test_function(correct_kappa)
    wrong_error = test_function(wrong_kappa)

    # Sanity: wrong kappa should give much worse error
    if wrong_error > expected_failure_threshold and wrong_error > correct_error * 5:
        print(f"✅ Sanity check passed: κ={wrong_kappa} gives error={wrong_error:.1%}")
        return True
    else:
        print(f"❌ Sanity check FAILED: wrong κ should produce higher error")
        return False


def format_comparison_table(topics: Dict[str, Dict[str, float]]) -> str:
    """
    Format comparison results as markdown table.

    Args:
        topics: Dict of topic -> {uet_error, baseline_error, improvement}

    Returns:
        Markdown table string
    """
    lines = [
        "| Topic | UET Error | Baseline Error | Improvement |",
        "|:------|----------:|---------------:|------------:|",
    ]

    for topic, results in topics.items():
        uet = results.get("uet_error_percent", 0)
        baseline = results.get("baseline_error_percent", 0)
        improvement = results.get("improvement_factor", 1)

        lines.append(f"| {topic} | {uet:.1f}% | {baseline:.1f}% | {improvement:.1f}x |")

    return "\n".join(lines)
