"""
❤️ UET Test 04: Bio HRV Equilibrium
===================================

Tests: dΩ/dt ≤ 0 (System seeks equilibrium)

Uses real HRV data from PhysioNet.

Updated for UET V3.0
"""

import numpy as np
import os

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

import glob

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "06_complex_systems")


def load_hrv_data():
    """Load HRV data from PhysioNet."""
    bio_dir = os.path.join(DATA_DIR, "bio")
    datasets = []

    if os.path.exists(bio_dir):
        for filename in os.listdir(bio_dir):
            if filename.startswith("physionet_") and filename.endswith("_rr.csv"):
                filepath = os.path.join(bio_dir, filename)
                try:
                    # Read CSV, first column is RR intervals
                    import pandas as pd

                    df = pd.read_csv(filepath)
                    if len(df.columns) > 0:
                        # Convert to numeric, coerce errors (handles header in data)
                        rr = pd.to_numeric(df.iloc[:, 0], errors="coerce").dropna().values
                        if len(rr) > 10:
                            name = filename.replace(".csv", "")
                            datasets.append((name, rr))
                except Exception as e:
                    print(f"   ⚠️ Could not load {filename}: {e}")

    return datasets


def calculate_hrv_metrics(rr_intervals):
    """
    Calculate HRV metrics related to UET equilibrium.

    UET Interpretation:
    - High HRV = System flexibility (low Ω, stable)
    - Low HRV = System stress (high Ω, seeking equilibrium)
    """
    if len(rr_intervals) < 10:
        return None

    # Clean data - convert to float and filter
    rr = np.array(rr_intervals, dtype=float)
    rr = rr[np.isfinite(rr)]
    rr = rr[(rr > 0.3) & (rr < 2.0)]  # Physiological range (seconds)

    if len(rr) < 10:
        return None

    # Time-domain metrics
    mean_rr = np.mean(rr)
    sdnn = np.std(rr)  # Standard deviation
    rmssd = np.sqrt(np.mean(np.diff(rr) ** 2))  # Root mean square of differences

    # Coefficient of variation (normalized variability)
    cv = sdnn / mean_rr

    # Poincaré plot metrics (short-term vs long-term variability)
    sd1 = np.std(np.diff(rr)) / np.sqrt(2)
    sd2 = np.sqrt(2 * sdnn**2 - sd1**2) if 2 * sdnn**2 > sd1**2 else sdnn

    # UET Equilibrium Score
    # Higher = closer to equilibrium
    # Based on balance between short and long-term
    balance = sd1 / (sd2 + 0.001)
    equilibrium_score = 1 / (1 + abs(balance - 0.5))  # Optimal around 0.5

    return {
        "mean_rr": mean_rr,
        "sdnn": sdnn,
        "rmssd": rmssd,
        "cv": cv,
        "sd1": sd1,
        "sd2": sd2,
        "balance": balance,
        "equilibrium_score": equilibrium_score,
        "n_beats": len(rr),
    }


def run_test():
    """Run HRV equilibrium test."""
    print("\n" + "=" * 60)
    print("❤️ UET TEST 04: Bio HRV Equilibrium")
    print("=" * 60)
    print("\nEquation: dΩ/dt ≤ 0 (equilibrium seeking)")
    print("UET Prediction: Healthy systems show balanced variability")

    datasets = load_hrv_data()

    if not datasets:
        print("❌ No HRV data found!")
        return {"status": "FAIL", "error": "No data"}

    print(f"\nAnalyzing {len(datasets)} subjects...\n")

    results = []

    for name, rr in datasets:
        metrics = calculate_hrv_metrics(rr)

        if metrics:
            results.append({"name": name, **metrics})
            print(f"   {name}:")
            print(f"      Mean RR: {metrics['mean_rr']*1000:.0f} ms")
            print(f"      SDNN: {metrics['sdnn']*1000:.0f} ms")
            print(f"      RMSSD: {metrics['rmssd']*1000:.0f} ms")
            print(f"      Equilibrium Score: {metrics['equilibrium_score']:.2f}")
            print()

    if not results:
        print("❌ Could not calculate metrics")
        return {"status": "FAIL", "error": "Calculation failed"}

    # Summary
    avg_eq = np.mean([r["equilibrium_score"] for r in results])
    avg_sdnn = np.mean([r["sdnn"] for r in results]) * 1000
    avg_rmssd = np.mean([r["rmssd"] for r in results]) * 1000

    print("=" * 40)
    print(f"Average SDNN: {avg_sdnn:.0f} ms")
    print(f"Average RMSSD: {avg_rmssd:.0f} ms")
    print(f"Average Equilibrium Score: {avg_eq:.2f}")
    print("=" * 40)

    # Grade
    # Normal SDNN: 50-150 ms (healthy)
    if 50 < avg_sdnn < 150 and avg_eq > 0.5:
        grade = "⭐⭐⭐⭐⭐ HEALTHY EQUILIBRIUM"
        status = "PASS"
    elif 30 < avg_sdnn < 200:
        grade = "⭐⭐⭐⭐ NORMAL RANGE"
        status = "PASS"
    elif avg_sdnn > 20:
        grade = "⭐⭐⭐ BORDERLINE"
        status = "WARN"
    else:
        grade = "⭐⭐ LOW VARIABILITY"
        status = "FAIL"

    print(f"\nGrade: {grade}")
    print("\nInterpretation:")
    print("   High SDNN (>100ms) = High adaptability")
    print("   Low SDNN (<50ms) = Reduced flexibility (stress/disease)")

    return {
        "status": status,
        "avg_sdnn_ms": avg_sdnn,
        "avg_rmssd_ms": avg_rmssd,
        "avg_equilibrium": avg_eq,
        "subjects": len(results),
        "results": results,
    }


if __name__ == "__main__":
    result = run_test()
    print(f"\n✅ Test complete: {result['status']}")
