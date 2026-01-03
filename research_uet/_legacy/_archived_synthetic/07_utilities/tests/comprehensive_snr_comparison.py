"""
📊 COMPREHENSIVE SNR COMPARISON STUDY
======================================

Academic-level systematic comparison:
1. Multiple real SNRs (Cas A, Tycho, SN1006, Kepler, Cygnus)
2. Multiple models (Sedov, Blondin, Our UET)
3. Phase comparisons
4. Parameter sensitivity analysis
5. Statistical metrics

References:
- Cas A: Chandra X-ray Observatory, DeLaney et al. 2010
- Tycho: Katsuda et al. 2010, Badenes et al. 2007
- SN1006: Winkler et al. 2003, Acero et al. 2007
- Kepler: Vink et al. 2008, Sankrit et al. 2005
- Cygnus Loop: Fesen et al. 2018, Blair et al. 2005

Updated for UET V3.0
"""

import numpy as np
import matplotlib.pyplot as plt

# Import from UET V3.0 Master Equation
import sys
from pathlib import Path
_root = Path(__file__).parent
while _root.name != "research_uet" and _root.parent != _root:
    _root = _root.parent
sys.path.insert(0, str(_root.parent))
try:
    from research_uet.core.uet_master_equation import (
        UETParameters, SIGMA_CRIT, strategic_boost, potential_V, KAPPA_BEKENSTEIN
    )
except ImportError:
    pass  # Use local definitions if not available

import os

# Physical constants
M_sun = 2e33  # g
pc = 3.086e18  # cm
yr = 3.15e7  # s
m_p = 1.67e-24  # g


# =====================================================
# OBSERVED SNR DATA (from literature)
# =====================================================

OBSERVED_SNRS = {
    "Cas A": {
        "age_yr": 340,  # ~1680 AD explosion
        "age_err": 30,
        "distance_kpc": 3.4,
        "radius_pc": 2.5,  # Current outer radius
        "radius_err_pc": 0.3,
        "velocity_kms": 5500,  # Forward shock
        "velocity_err": 500,
        "phase": "Free Expansion / Early Ejecta",
        "type": "Type IIb",
        "references": ["DeLaney 2010", "Reed 1995"],
    },
    "Tycho": {
        "age_yr": 452,  # SN 1572
        "age_err": 1,
        "distance_kpc": 2.8,
        "radius_pc": 3.7,
        "radius_err_pc": 0.3,
        "velocity_kms": 4500,
        "velocity_err": 500,
        "phase": "Ejecta-Dominated / Early Sedov",
        "type": "Type Ia",
        "references": ["Katsuda 2010", "Badenes 2007"],
    },
    "SN1006": {
        "age_yr": 1018,  # 1006 AD
        "age_err": 1,
        "distance_kpc": 2.2,
        "radius_pc": 10,  # ~20 pc diameter
        "radius_err_pc": 1,
        "velocity_kms": 5000,
        "velocity_err": 1000,
        "phase": "Late Free Expansion / Sedov",
        "type": "Type Ia",
        "references": ["Winkler 2003", "Acero 2007"],
    },
    "Kepler": {
        "age_yr": 420,  # 1604 AD
        "age_err": 3,
        "distance_kpc": 5.0,
        "radius_pc": 4.0,
        "radius_err_pc": 0.5,
        "velocity_kms": 4000,
        "velocity_err": 500,
        "phase": "Ejecta-Dominated",
        "type": "Type Ia (unusual)",
        "references": ["Vink 2008", "Sankrit 2005"],
    },
    "Cygnus Loop": {
        "age_yr": 20000,  # Estimate
        "age_err": 5000,
        "distance_kpc": 0.74,
        "radius_pc": 18.5,  # ~37 pc diameter / 2
        "radius_err_pc": 2,
        "velocity_kms": 180,
        "velocity_err": 40,
        "phase": "Radiative Snowplow",
        "type": "Core Collapse",
        "references": ["Fesen 2018", "Blair 1991"],
    },
}


# =====================================================
# THEORETICAL MODELS
# =====================================================


class SedovModel:
    """Classic Sedov-Taylor self-similar solution."""

    def __init__(self, E51=1.0, n0=0.1, M_ej=3.0):
        self.E51 = E51
        self.n0 = n0
        self.M_ej = M_ej
        self.name = "Sedov-Taylor"

        self.rho = n0 * m_p

    def radius(self, t_yr):
        """R = 1.15 × (E/ρ)^0.2 × t^0.4"""
        t = t_yr * yr
        R = 1.15 * (self.E51 * 1e51 / self.rho) ** 0.2 * t**0.4
        return R / pc

    def velocity(self, t_yr):
        """v = 0.4 × R/t"""
        t = t_yr * yr
        R = self.radius(t_yr) * pc
        return 0.4 * R / t / 1e5  # km/s


class BlondinModel:
    """Blondin et al. 1998 formulas."""

    def __init__(self, E51=1.0, n0=0.1):
        self.E51 = E51
        self.n0 = n0
        self.name = "Blondin 1998"

    def transition_time(self):
        """t_tr ≈ 4.4×10^4 × E^0.22 × n^-0.55 years"""
        return 4.4e4 * (self.E51**0.22) * (self.n0**-0.55)

    def radius_at_transition(self):
        """R_tr ≈ 22 × E^0.29 × n^-0.42 pc"""
        return 22 * (self.E51**0.29) * (self.n0**-0.42)

    def velocity_at_transition(self):
        """v_tr ≈ 200 × E^0.07 × n^0.13 km/s"""
        return 200 * (self.E51**0.07) * (self.n0**0.13)


class UETModel:
    """Our UET-based model."""

    def __init__(self, E51=1.0, n0=1.0, M_ej=5.0):
        self.E51 = E51
        self.n0 = n0
        self.M_ej = M_ej
        self.name = "UET"

        self.rho = n0 * m_p
        self.v_ej = np.sqrt(2 * E51 * 1e51 / (M_ej * M_sun))

    def free_expansion_end(self):
        """When swept mass = ejecta mass"""
        R_free = (3 * self.M_ej * M_sun / (4 * np.pi * self.rho)) ** (1 / 3)
        t_free = R_free / self.v_ej
        return t_free / yr, R_free / pc

    def radius(self, t_yr):
        """Combined free expansion + Sedov"""
        t_fe, R_fe = self.free_expansion_end()

        if t_yr < t_fe:
            # Free expansion: R = v * t
            return self.v_ej * t_yr * yr / pc
        else:
            # Sedov: R ∝ t^0.4
            return 1.15 * (self.E51 * 1e51 / self.rho) ** 0.2 * (t_yr * yr) ** 0.4 / pc

    def velocity(self, t_yr):
        """dR/dt"""
        t_fe, _ = self.free_expansion_end()

        if t_yr < t_fe:
            return self.v_ej / 1e5
        else:
            R = self.radius(t_yr) * pc
            return 0.4 * R / (t_yr * yr) / 1e5


def run_comparison():
    """Run comprehensive comparison."""

    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE SNR COMPARISON STUDY")
    print("=" * 80)

    # =========================================
    # TABLE 1: Observed SNR Properties
    # =========================================

    print("\n" + "=" * 80)
    print("TABLE 1: OBSERVED SNR PROPERTIES")
    print("=" * 80)

    print("\n| SNR | Age (yr) | R (pc) | v (km/s) | Phase | Type |")
    print("|:----|:---------|:-------|:---------|:------|:-----|")

    for name, obs in OBSERVED_SNRS.items():
        print(
            f"| {name:12} | {obs['age_yr']:>8} | {obs['radius_pc']:>6.1f} | "
            f"{obs['velocity_kms']:>8.0f} | {obs['phase'][:20]} | {obs['type']} |"
        )

    # =========================================
    # TABLE 2: Model Predictions vs Observations
    # =========================================

    print("\n" + "=" * 80)
    print("TABLE 2: MODEL PREDICTIONS vs OBSERVATIONS")
    print("=" * 80)

    # Use standard parameters
    sedov = SedovModel(E51=1.0, n0=1.0)
    blondin = BlondinModel(E51=1.0, n0=1.0)
    uet = UETModel(E51=1.0, n0=1.0, M_ej=5.0)

    print("\nUsing standard parameters: E=10^51 erg, n₀=1 cm⁻³, M_ej=5 M☉")
    print("\n| SNR | Age | Observed R | Sedov R | UET R | Obs v | Sedov v | UET v |")
    print("|:----|----:|-----------:|--------:|------:|------:|--------:|------:|")

    results = []
    for name, obs in OBSERVED_SNRS.items():
        age = obs["age_yr"]
        R_obs = obs["radius_pc"]
        v_obs = obs["velocity_kms"]

        R_sed = sedov.radius(age)
        v_sed = sedov.velocity(age)
        R_uet = uet.radius(age)
        v_uet = uet.velocity(age)

        print(
            f"| {name:12} | {age:5} | {R_obs:10.1f} | {R_sed:7.1f} | {R_uet:5.1f} | "
            f"{v_obs:5.0f} | {v_sed:7.0f} | {v_uet:5.0f} |"
        )

        results.append(
            {
                "name": name,
                "age": age,
                "R_obs": R_obs,
                "R_sed": R_sed,
                "R_uet": R_uet,
                "v_obs": v_obs,
                "v_sed": v_sed,
                "v_uet": v_uet,
                "phase": obs["phase"],
            }
        )

    # =========================================
    # TABLE 3: Error Analysis
    # =========================================

    print("\n" + "=" * 80)
    print("TABLE 3: RELATIVE ERRORS (%)")
    print("=" * 80)

    print("\n| SNR | Sedov R err | UET R err | Sedov v err | UET v err |")
    print("|:----|------------:|----------:|------------:|----------:|")

    for r in results:
        R_sed_err = abs(r["R_sed"] - r["R_obs"]) / r["R_obs"] * 100
        R_uet_err = abs(r["R_uet"] - r["R_obs"]) / r["R_obs"] * 100
        v_sed_err = abs(r["v_sed"] - r["v_obs"]) / r["v_obs"] * 100
        v_uet_err = abs(r["v_uet"] - r["v_obs"]) / r["v_obs"] * 100

        R_sed_sym = "✅" if R_sed_err < 30 else "⚠️" if R_sed_err < 50 else "❌"
        R_uet_sym = "✅" if R_uet_err < 30 else "⚠️" if R_uet_err < 50 else "❌"

        print(
            f"| {r['name']:12} | {R_sed_err:10.0f}% {R_sed_sym} | {R_uet_err:8.0f}% {R_uet_sym} | "
            f"{v_sed_err:10.0f}% | {v_uet_err:8.0f}% |"
        )

        r["R_sed_err"] = R_sed_err
        r["R_uet_err"] = R_uet_err
        r["v_sed_err"] = v_sed_err
        r["v_uet_err"] = v_uet_err

    # =========================================
    # TABLE 4: Parameter Sensitivity Analysis
    # =========================================

    print("\n" + "=" * 80)
    print("TABLE 4: PARAMETER SENSITIVITY (Cas A example)")
    print("=" * 80)

    cas_a = OBSERVED_SNRS["Cas A"]

    print("\n| n₀ (cm⁻³) | Model R (pc) | Observed R | Error (%) |")
    print("|:----------|-------------:|-----------:|----------:|")

    for n0 in [0.01, 0.1, 0.5, 1.0, 2.0, 5.0]:
        model = UETModel(E51=1.0, n0=n0, M_ej=5.0)
        R_model = model.radius(cas_a["age_yr"])
        err = abs(R_model - cas_a["radius_pc"]) / cas_a["radius_pc"] * 100
        mark = "✅ BEST" if err < 30 else ""
        print(f"| {n0:9.2f} | {R_model:12.1f} | {cas_a['radius_pc']:10.1f} | {err:8.0f}% {mark} |")

    # =========================================
    # TABLE 5: Best-Fit Parameters
    # =========================================

    print("\n" + "=" * 80)
    print("TABLE 5: BEST-FIT PARAMETERS PER SNR")
    print("=" * 80)

    print("\n| SNR | Observed R | Best n₀ | Model R | Error |")
    print("|:----|:-----------|--------:|--------:|------:|")

    for name, obs in OBSERVED_SNRS.items():
        # Find n0 that gives best R match
        best_n0 = None
        best_err = float("inf")
        best_R = None

        for n0 in np.logspace(-2, 1, 50):
            model = UETModel(E51=1.0, n0=n0, M_ej=5.0)
            R_model = model.radius(obs["age_yr"])
            err = abs(R_model - obs["radius_pc"]) / obs["radius_pc"] * 100
            if err < best_err:
                best_err = err
                best_n0 = n0
                best_R = R_model

        print(
            f"| {name:12} | {obs['radius_pc']:10.1f} | {best_n0:7.2f} | {best_R:7.1f} | {best_err:5.0f}% |"
        )

    # =========================================
    # TABLE 6: Phase Comparison
    # =========================================

    print("\n" + "=" * 80)
    print("TABLE 6: PHASE COMPARISON")
    print("=" * 80)

    print("\n| SNR | Age (yr) | Observed Phase | Predicted Phase | Match |")
    print("|:----|:---------|:---------------|:----------------|:------|")

    for name, obs in OBSERVED_SNRS.items():
        age = obs["age_yr"]
        obs_phase = obs["phase"]

        # Predict phase based on age
        if age < 500:
            pred_phase = "Free Expansion / Ejecta"
        elif age < 10000:
            pred_phase = "Sedov-Taylor (Adiabatic)"
        elif age < 50000:
            pred_phase = "Late Sedov / Early Snowplow"
        else:
            pred_phase = "Radiative Snowplow"

        # Check match
        match = "✅" if any(p in pred_phase.lower() for p in obs_phase.lower().split()) else "⚠️"

        print(f"| {name:12} | {age:8} | {obs_phase[:25]:25} | {pred_phase[:20]:20} | {match} |")

    # =========================================
    # SUMMARY STATISTICS
    # =========================================

    print("\n" + "=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)

    avg_R_sed = np.mean([r["R_sed_err"] for r in results])
    avg_R_uet = np.mean([r["R_uet_err"] for r in results])
    avg_v_sed = np.mean([r["v_sed_err"] for r in results])
    avg_v_uet = np.mean([r["v_uet_err"] for r in results])

    print(f"\n   Average Radius Error:")
    print(f"     Sedov Model: {avg_R_sed:.0f}%")
    print(f"     UET Model:   {avg_R_uet:.0f}%")

    print(f"\n   Average Velocity Error:")
    print(f"     Sedov Model: {avg_v_sed:.0f}%")
    print(f"     UET Model:   {avg_v_uet:.0f}%")

    print("\n   Note: High errors with n₀=1 indicate real SNRs")
    print("   are in diverse ISM densities (0.01 - 5 cm⁻³)")

    # =========================================
    # CONCLUSIONS
    # =========================================

    print("\n" + "=" * 80)
    print("CONCLUSIONS")
    print("=" * 80)

    print(
        """
    1. MODELS vs OBSERVATIONS:
       - Standard n₀=1 gives ~50% error for young SNRs
       - Each SNR needs individual n₀ fitting
       
    2. UET vs SEDOV:
       - Similar accuracy when using same parameters
       - Both are approximations of complex physics
       
    3. PHASE PREDICTION:
       - Age-based phase prediction generally matches
       - Young SNRs (< 500 yr) in Free Expansion ✅
       - Old SNRs (> 10 kyr) in Snowplow ✅
       
    4. PARAMETER SENSITIVITY:
       - n₀ is most critical parameter
       - Factor of 10 in n₀ → Factor of ~2 in R
       
    5. WHAT'S NEEDED:
       - Individual SNR fitting
       - Better n₀ estimates from observations
       - Account for ISM inhomogeneity
    """
    )

    return results


def create_plots(output_dir="comparison_output"):
    """Generate comparison plots."""
    os.makedirs(output_dir, exist_ok=True)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Data
    ages = [obs["age_yr"] for obs in OBSERVED_SNRS.values()]
    radii = [obs["radius_pc"] for obs in OBSERVED_SNRS.values()]
    velocities = [obs["velocity_kms"] for obs in OBSERVED_SNRS.values()]
    names = list(OBSERVED_SNRS.keys())

    # Models
    t_range = np.logspace(2, 5, 100)
    sedov = SedovModel(E51=1.0, n0=0.1)
    uet = UETModel(E51=1.0, n0=0.1, M_ej=3.0)

    R_sedov = [sedov.radius(t) for t in t_range]
    R_uet = [uet.radius(t) for t in t_range]

    # Plot 1: R vs Age
    ax = axes[0, 0]
    ax.scatter(ages, radii, s=100, c="red", marker="o", label="Observations", zorder=5)
    ax.plot(t_range, R_sedov, "b-", label="Sedov (n₀=0.1)")
    ax.plot(t_range, R_uet, "g--", label="UET (n₀=0.1)")
    for i, name in enumerate(names):
        ax.annotate(name, (ages[i], radii[i]), fontsize=8, ha="left")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Age (years)")
    ax.set_ylabel("Radius (pc)")
    ax.set_title("Radius vs Age")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Plot 2: v vs Age
    ax = axes[0, 1]
    v_sedov = [sedov.velocity(t) for t in t_range]
    v_uet = [uet.velocity(t) for t in t_range]
    ax.scatter(ages, velocities, s=100, c="red", marker="o", label="Observations", zorder=5)
    ax.plot(t_range, v_sedov, "b-", label="Sedov")
    ax.plot(t_range, v_uet, "g--", label="UET")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Age (years)")
    ax.set_ylabel("Velocity (km/s)")
    ax.set_title("Velocity vs Age")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Plot 3: Parameter sensitivity
    ax = axes[1, 0]
    n0_values = [0.01, 0.1, 0.5, 1.0, 2.0]
    for n0 in n0_values:
        model = UETModel(E51=1.0, n0=n0, M_ej=3.0)
        R_n0 = [model.radius(t) for t in t_range]
        ax.plot(t_range, R_n0, label=f"n₀={n0}")
    ax.scatter(ages, radii, s=100, c="red", marker="o", label="Observations", zorder=5)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Age (years)")
    ax.set_ylabel("Radius (pc)")
    ax.set_title("Parameter Sensitivity: n₀")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # Plot 4: Model comparison bar chart
    ax = axes[1, 1]
    errors_sedov = []
    errors_uet = []
    for name, obs in OBSERVED_SNRS.items():
        age = obs["age_yr"]
        R_obs = obs["radius_pc"]
        R_s = SedovModel(E51=1.0, n0=1.0).radius(age)
        R_u = UETModel(E51=1.0, n0=1.0, M_ej=5.0).radius(age)
        errors_sedov.append(abs(R_s - R_obs) / R_obs * 100)
        errors_uet.append(abs(R_u - R_obs) / R_obs * 100)

    x = np.arange(len(names))
    width = 0.35
    ax.bar(x - width / 2, errors_sedov, width, label="Sedov")
    ax.bar(x + width / 2, errors_uet, width, label="UET")
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=45, ha="right")
    ax.set_ylabel("Radius Error (%)")
    ax.set_title("Model Errors (n₀=1)")
    ax.legend()
    ax.axhline(50, color="r", linestyle="--", alpha=0.5)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    filepath = os.path.join(output_dir, "snr_comparison.png")
    plt.savefig(filepath, dpi=150)
    print(f"\n📊 Plot saved: {filepath}")

    return fig


if __name__ == "__main__":
    results = run_comparison()

    output_dir = os.path.join(os.path.dirname(__file__), "comparison_output")
    create_plots(output_dir)
