"""
Test: Weak Equivalence Principle
================================
Data Source: Eöt-Wash Group, Schlamminger et al. 2008
DOI: 10.1103/PhysRevLett.100.041101

Reference:
    Schlamminger, S., Choi, K.-Y., Wagner, T.A., Gundlach, J.H. & Adelberger, E.G.
    "Test of the equivalence principle using a rotating torsion balance"
    Phys. Rev. Lett. 100, 041101 (2008)

Measurement:
    Eötvös parameter η(Earth) = (0.3 ± 1.8) × 10⁻¹³
    Test bodies: Beryllium vs Titanium

UET Prediction:
    η = 0 (unified inertial/gravitational mass in UET framework)
    UET predicts exact equivalence as information processing is mass-independent
"""

import numpy as np

# === REPRODUCIBILITY: Lock all seeds for deterministic results ===
try:
    import sys
    from pathlib import Path

    _root = Path(__file__).parent
    while _root.name != "research_uet" and _root.parent != _root:
        _root = _root.parent
    sys.path.insert(0, str(_root.parent))
    from research_uet.core.reproducibility import lock_all_seeds

    lock_all_seeds(42)
except ImportError:
    np.random.seed(42)  # Fallback

# ============================================================
# REAL DATA: Eöt-Wash Torsion Balance Experiment
# DOI: 10.1103/PhysRevLett.100.041101
# ============================================================

# Eötvös parameter measurements (from paper)
EOTWASH_DATA = {
    "source": "Earth gravity",
    "test_bodies": ["Beryllium", "Titanium"],
    "eta_measured": 0.3e-13,  # Central value
    "eta_uncertainty": 1.8e-13,  # 1σ uncertainty
    "doi": "10.1103/PhysRevLett.100.041101",
    "year": 2008,
    "precision": "10^-13",
}

# MICROSCOPE space mission (backup verification)
MICROSCOPE_DATA = {
    "source": "Earth orbit (space)",
    "test_bodies": ["Platinum", "Titanium"],
    "eta_measured": 0.0,  # Null result
    "eta_uncertainty": 1.5e-15,  # 1σ uncertainty
    "doi": "10.1103/PhysRevLett.129.121102",
    "year": 2022,
    "precision": "10^-15",
}


def uet_predict_equivalence_parameter():
    """
    UET Prediction for Eötvös parameter η.

    In UET framework:
    - Mass = Information latency (I)
    - Gravity = Information density gradient
    - Inertial response and gravitational response
      are BOTH determined by I

    Therefore: η_UET = 0 (exact equivalence)
    """
    return 0.0


def test_equivalence_principle_eotwash():
    """
    Test 1: Eöt-Wash Data
    Check if UET prediction (η=0) is within experimental bounds.
    """
    print("=" * 60)
    print("Test: Weak Equivalence Principle (Eöt-Wash)")
    print("DOI: 10.1103/PhysRevLett.100.041101")
    print("=" * 60)

    # UET prediction
    eta_uet = uet_predict_equivalence_parameter()

    # Measured value
    eta_exp = EOTWASH_DATA["eta_measured"]
    eta_err = EOTWASH_DATA["eta_uncertainty"]

    # Calculate tension
    tension_sigma = abs(eta_uet - eta_exp) / eta_err

    print(f"\nUET Prediction:  η = {eta_uet}")
    print(f"Eöt-Wash Result: η = ({eta_exp/1e-13:.1f} ± {eta_err/1e-13:.1f}) × 10⁻¹³")
    print(f"Tension: {tension_sigma:.2f}σ")

    # Pass if within 2σ
    passed = tension_sigma < 2.0
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"\nResult: {status}")

    return passed


def test_equivalence_principle_microscope():
    """
    Test 2: MICROSCOPE Space Mission
    Even higher precision test.
    """
    print("\n" + "=" * 60)
    print("Test: Weak Equivalence Principle (MICROSCOPE)")
    print("DOI: 10.1103/PhysRevLett.129.121102")
    print("=" * 60)

    # UET prediction
    eta_uet = uet_predict_equivalence_parameter()

    # Measured value
    eta_exp = MICROSCOPE_DATA["eta_measured"]
    eta_err = MICROSCOPE_DATA["eta_uncertainty"]

    # MICROSCOPE found null result (η consistent with 0)
    # Check if UET=0 is within bounds
    in_bounds = abs(eta_uet - eta_exp) <= 2 * eta_err

    print(f"\nUET Prediction:    η = {eta_uet}")
    print(f"MICROSCOPE Result: η = (0 ± {eta_err/1e-15:.1f}) × 10⁻¹⁵")
    print(f"Precision: 10⁻¹⁵ level")

    status = "✅ PASS" if in_bounds else "❌ FAIL"
    print(f"\nResult: {status}")

    return in_bounds


def main():
    """Run all equivalence principle tests."""
    print("\n" + "=" * 70)
    print("UET EQUIVALENCE PRINCIPLE VALIDATION")
    print("Using REAL Experimental Data")
    print("=" * 70)

    results = []

    # Test 1: Eöt-Wash
    results.append(test_equivalence_principle_eotwash())

    # Test 2: MICROSCOPE
    results.append(test_equivalence_principle_microscope())

    # Summary
    passed = sum(results)
    total = len(results)

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Tests Passed: {passed}/{total}")

    if passed == total:
        print("Grade: ✅ ALL PASS")
        print("\nConclusion: UET's unified mass framework")
        print("correctly predicts equivalence principle!")
    else:
        print(f"Grade: ⚠️ {total - passed} test(s) failed")

    print("=" * 70)

    return passed == total


if __name__ == "__main__":
    import sys

    success = main()
    sys.exit(0 if success else 1)
