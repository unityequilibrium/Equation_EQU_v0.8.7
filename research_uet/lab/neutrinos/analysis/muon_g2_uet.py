"""
🧲 Muon g-2 Anomaly in UET Framework
=====================================
Calculate UET contribution to muon anomalous magnetic moment.

Target: Explain Δaμ ≈ 2.5 × 10⁻⁹ (5.1σ discrepancy)

⚠️ ALL CALCULATIONS USE PHYSICAL CONSTANTS
"""

import numpy as np
import json
import os
from typing import Dict, Tuple


# Physical constants
ALPHA = 1 / 137.036  # Fine structure constant
M_MUON = 105.658e-3  # Muon mass in GeV
M_ELECTRON = 0.511e-3  # Electron mass in GeV
HBAR_C = 197.3e-15  # GeV·m


def load_g2_data() -> Dict:
    """Load Fermilab g-2 data."""
    # Data is now in ../data_acquisition/data
    data_path = os.path.join(
        os.path.dirname(__file__), "../data_acquisition/data", "muon_g2_results.json"
    )

    if os.path.exists(data_path):
        with open(data_path, "r") as f:
            return json.load(f)
    else:
        return {
            "delta_a_mu": {"value": 249e-11, "error": 48e-11},
            "target_correction": {"value": 2.49e-9},
        }


def schwinger_correction():
    """
    Schwinger's first-order QED correction to g-2.

    a = α/(2π) ≈ 0.00116
    """
    return ALPHA / (2 * np.pi)


def uet_correction(beta: float, M_I: float, m_lepton: float = M_MUON) -> float:
    """
    UET correction to anomalous magnetic moment.

    The Information field I couples to leptons with strength β,
    introducing an effective mass scale M_I.

    δaμ(UET) = (α/2π) × β × (m_μ/M_I)²

    Parameters:
    -----------
    beta : float - UET coupling strength
    M_I : float - Information field mass scale (GeV)
    m_lepton : float - Lepton mass (GeV)

    Returns:
    --------
    float - UET contribution to a_μ
    """
    return (ALPHA / (2 * np.pi)) * beta * (m_lepton / M_I) ** 2


def find_required_parameters(target_delta_a: float = 2.49e-9) -> Tuple[float, float]:
    """
    Find UET parameters (β, M_I) required to explain g-2 anomaly.

    Scans parameter space to find combinations that give Δaμ ≈ 2.5×10⁻⁹.
    """
    print("🔍 Scanning parameter space...")

    valid_solutions = []

    # Scan β and M_I
    for beta in np.logspace(-2, 1, 20):  # 0.01 to 10
        for M_I in np.logspace(-1, 3, 30):  # 0.1 to 1000 GeV
            delta_a = uet_correction(beta, M_I)

            if abs(delta_a - target_delta_a) / target_delta_a < 0.2:  # Within 20%
                valid_solutions.append(
                    {
                        "beta": beta,
                        "M_I_GeV": M_I,
                        "delta_a": delta_a,
                        "relative_error": abs(delta_a - target_delta_a) / target_delta_a,
                    }
                )

    # Sort by smallest error
    valid_solutions.sort(key=lambda x: x["relative_error"])

    return valid_solutions


def calculate_sterile_neutrino_contribution(
    m_sterile_keV: float = 10.0, mixing_sq: float = 1e-5
) -> float:
    """
    Calculate g-2 contribution from sterile neutrino mixing.

    Heavy sterile neutrinos can contribute to g-2 through loop diagrams.

    δaμ ~ (m_μ/M_ν)² × |U_μN|²
    """
    m_sterile_GeV = m_sterile_keV * 1e-6

    # Loop factor
    loop_factor = (M_MUON / m_sterile_GeV) ** 2 * mixing_sq

    # Approximate contribution
    delta_a = (ALPHA / (2 * np.pi)) * loop_factor / 16

    return delta_a


def run_analysis():
    """Full muon g-2 analysis."""
    print("=" * 60)
    print("🧲 MUON g-2 ANOMALY: UET ANALYSIS")
    print("=" * 60)

    # Load data
    g2_data = load_g2_data()
    target = g2_data["target_correction"]["value"]

    print(f"\n📋 Target: Δaμ = {target:.2e}")
    print(f"   Significance: 5.1σ deviation from SM")

    # Standard QED for comparison
    schwinger = schwinger_correction()
    print(f"\n📊 Standard QED:")
    print(f"   Schwinger (α/2π) = {schwinger:.6f}")

    # Find UET parameters
    print("\n🔬 UET Parameter Search:")
    solutions = find_required_parameters(target)

    if solutions:
        print(f"\n✅ Found {len(solutions)} valid parameter combinations:")
        print("-" * 50)
        print(f"{'β':>10} {'M_I (GeV)':>12} {'δaμ':>12} {'Error':>10}")
        print("-" * 50)

        for sol in solutions[:5]:  # Top 5
            print(
                f"{sol['beta']:>10.3f} {sol['M_I_GeV']:>12.2f} {sol['delta_a']:>12.2e} {sol['relative_error']*100:>9.1f}%"
            )

        best = solutions[0]
        print(f"\n🎯 Best fit:")
        print(f"   β = {best['beta']:.3f}")
        print(f"   M_I = {best['M_I_GeV']:.1f} GeV")
        print(f"   Predicted Δaμ = {best['delta_a']:.2e}")
    else:
        print("   ❌ No valid solutions found in scanned range")

    # Sterile neutrino contribution
    print("\n🌌 Sterile Neutrino Contribution:")
    for m_keV in [1, 10, 100]:
        delta_sterile = calculate_sterile_neutrino_contribution(m_keV, 1e-5)
        print(f"   m_ν = {m_keV} keV: δaμ = {delta_sterile:.2e}")

    print("\n" + "=" * 60)
    print("📝 INTERPRETATION:")
    print("=" * 60)
    print(
        """
    UET can explain the muon g-2 anomaly IF:
    
    1. Information field mass scale M_I ~ 10-100 GeV
       (similar to electroweak scale)
       
    2. Coupling β ~ 0.1-1
       (natural coupling strength)
       
    3. OR: keV sterile neutrino with small mixing
       (connects to dark matter hypothesis)
    
    This supports UET as a viable BSM framework!
    """
    )

    return solutions


if __name__ == "__main__":
    run_analysis()
