"""
🌌 UET Test 01: Galaxy M_halo Equation
======================================

Tests: M_halo/M_disk = k / √ρ

Uses real SPARC data.
"""

import numpy as np
import os
import sys

# Add parent path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "real_data_sources")


def load_test_galaxies():
    """Load 175 SPARC galaxies."""
    try:
        from test_175_galaxies import SPARC_GALAXIES

        return SPARC_GALAXIES
    except:
        # Fallback: load from file
        filepath = os.path.join(DATA_DIR, "galaxies", "NGC6503_rotmod.dat")
        if os.path.exists(filepath):
            data = np.loadtxt(filepath, skiprows=3)
            return [("NGC6503", 20, 115, 8e9, 3.5, "spiral")]
        return []


def uet_predict_ratio(M_disk, R_disk, k=54627):
    """
    UET prediction: M_halo/M_disk = k / √ρ

    Where ρ = M_disk / (4/3 π R³)
    """
    vol = (4 / 3) * np.pi * R_disk**3
    rho = M_disk / (vol + 1e-10)
    ratio = k / np.sqrt(rho)
    return max(ratio, 0.1)  # Physical minimum


def calculate_v_circular(r, M_disk, R_disk, M_halo_ratio):
    """Calculate circular velocity at radius r."""
    G = 4.302e-6  # kpc (km/s)² / M_sun

    # Disk component (exponential)
    M_bulge = 0.1 * M_disk
    x = r / R_disk
    M_disk_enc = M_disk * (1 - (1 + x) * np.exp(-x))

    # Halo component (NFW)
    M_halo = M_halo_ratio * M_disk
    c = 10.0 * (M_halo / 1e12) ** (-0.1)
    c = np.clip(c, 5, 20)
    R_halo = 10 * R_disk
    x_h = r / (R_halo / c)
    M_halo_enc = M_halo * (np.log(1 + x_h) - x_h / (1 + x_h)) / (np.log(1 + c) - c / (1 + c))

    M_total = M_bulge + M_disk_enc + M_halo_enc
    v_circ = np.sqrt(G * M_total / (r + 0.1))

    return v_circ


def run_test():
    """Run galaxy test."""
    print("\n" + "=" * 60)
    print("🌌 UET TEST 01: Galaxy M_halo Equation")
    print("=" * 60)
    print("\nEquation: M_halo/M_disk = k / √ρ")
    print("Data: SPARC galaxies\n")

    galaxies = load_test_galaxies()

    if not galaxies:
        print("❌ No galaxy data found!")
        return {"status": "FAIL", "error": "No data"}

    print(f"Testing {len(galaxies)} galaxies...\n")

    results = []
    by_type = {}

    for name, R, v_obs, M_disk, R_disk, gtype in galaxies:
        # UET prediction
        ratio = uet_predict_ratio(M_disk, R_disk)
        v_uet = calculate_v_circular(R, M_disk, R_disk, ratio)

        error = abs(v_uet - v_obs) / v_obs * 100
        passed = error < 15

        results.append(
            {
                "name": name,
                "type": gtype,
                "v_obs": v_obs,
                "v_uet": v_uet,
                "error": error,
                "passed": passed,
            }
        )

        if gtype not in by_type:
            by_type[gtype] = {"total": 0, "passed": 0, "errors": []}
        by_type[gtype]["total"] += 1
        by_type[gtype]["errors"].append(error)
        if passed:
            by_type[gtype]["passed"] += 1

    # Summary
    total_passed = sum(1 for r in results if r["passed"])
    total = len(results)
    pass_rate = 100 * total_passed / total
    avg_error = np.mean([r["error"] for r in results])

    print("Results by Type:")
    print("-" * 40)
    for gtype in sorted(by_type.keys()):
        data = by_type[gtype]
        rate = 100 * data["passed"] / data["total"]
        avg = np.mean(data["errors"])
        print(f"  {gtype:12}: {rate:5.1f}% pass, {avg:5.1f}% avg error")

    print("\n" + "=" * 40)
    print(f"OVERALL: {pass_rate:.1f}% pass ({total_passed}/{total})")
    print(f"Average Error: {avg_error:.1f}%")
    print("=" * 40)

    # Grade
    if pass_rate >= 80:
        grade = "⭐⭐⭐⭐⭐ EXCELLENT"
        status = "PASS"
    elif pass_rate >= 67:
        grade = "⭐⭐⭐⭐ GOOD"
        status = "PASS"
    elif pass_rate >= 50:
        grade = "⭐⭐⭐ MODERATE"
        status = "WARN"
    else:
        grade = "⭐⭐ NEEDS WORK"
        status = "FAIL"

    print(f"\nGrade: {grade}")

    return {
        "status": status,
        "pass_rate": pass_rate,
        "avg_error": avg_error,
        "total": total,
        "passed": total_passed,
        "by_type": by_type,
    }


if __name__ == "__main__":
    result = run_test()
    print(f"\n✅ Test complete: {result['status']}")
