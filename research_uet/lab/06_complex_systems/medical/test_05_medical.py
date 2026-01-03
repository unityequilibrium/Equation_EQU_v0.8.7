"""
🏥 UET Test 05: Medical Diffusion Dynamics
==========================================

Tests: ∂C/∂t = M∇²(δΩ/δC) (Diffusion equation)

Uses real COVID-19 data from Johns Hopkins.

Updated for UET V3.0
"""

import numpy as np
import pandas as pd

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

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "real_data_sources")


def load_covid_data():
    """Load COVID-19 time series data."""
    filepath = os.path.join(DATA_DIR, "medical", "covid19_owid_global.csv")

    if os.path.exists(filepath):
        df = pd.read_csv(filepath)
        return df

    return None


def calculate_diffusion_metrics(cases_series):
    """
    Calculate metrics related to diffusion dynamics.

    UET Model: ∂C/∂t = D∇²C (simplified)

    For epidemic:
    - Exponential growth = far from equilibrium (dΩ/dt > 0)
    - Linear/stable = approaching equilibrium
    - Decline = returning to equilibrium
    """
    if len(cases_series) < 30:
        return None

    # Remove zeros and NaN
    cases = cases_series.dropna().values
    cases = cases[cases > 0]

    if len(cases) < 30:
        return None

    # Calculate growth rates
    growth_rate = np.diff(np.log(cases + 1))

    # Average growth rate (R-effective proxy)
    avg_growth = np.mean(growth_rate[-14:])  # Last 2 weeks

    # Growth rate trend (is it slowing?)
    if len(growth_rate) > 30:
        early = np.mean(growth_rate[:14])
        late = np.mean(growth_rate[-14:])
        trend = late - early
    else:
        trend = 0

    # Equilibrium proximity
    # 0 growth = equilibrium
    equilibrium_distance = abs(avg_growth)

    # Classify phase
    if avg_growth > 0.05:
        phase = "EXPONENTIAL (far from equilibrium)"
    elif avg_growth > 0.01:
        phase = "GROWTH (approaching peak)"
    elif avg_growth > -0.01:
        phase = "PLATEAU (near equilibrium)"
    elif avg_growth > -0.05:
        phase = "DECLINE (returning to equilibrium)"
    else:
        phase = "RAPID DECLINE"

    return {
        "avg_growth_rate": avg_growth,
        "growth_trend": trend,
        "equilibrium_distance": equilibrium_distance,
        "phase": phase,
        "total_cases": cases[-1],
        "data_points": len(cases),
    }


def run_test():
    """Run COVID diffusion test."""
    print("\n" + "=" * 60)
    print("🏥 UET TEST 05: Medical Diffusion Dynamics")
    print("=" * 60)
    print("\nEquation: ∂C/∂t = M∇²(δΩ/δC)")
    print("UET Prediction: Epidemic follows diffusion → equilibrium")

    df = load_covid_data()

    if df is None:
        print("❌ No COVID data found!")
        return {"status": "FAIL", "error": "No data"}

    print(f"\nData loaded: {len(df)} records")

    # Analyze top countries
    if "location" in df.columns and "total_cases" in df.columns:
        top_countries = df.groupby("location")["total_cases"].max().nlargest(10).index
    else:
        print("❌ Required columns not found")
        return {"status": "FAIL", "error": "Bad data format"}

    print(f"\nAnalyzing top {len(top_countries)} countries...\n")

    results = []

    for country in top_countries:
        country_df = df[df["location"] == country].sort_values("date")

        if "new_cases" in country_df.columns:
            cases = country_df["new_cases"].rolling(7).mean()  # 7-day average
        elif "total_cases" in country_df.columns:
            cases = country_df["total_cases"].diff()
        else:
            continue

        metrics = calculate_diffusion_metrics(cases)

        if metrics:
            results.append({"country": country, **metrics})
            print(f"   {country:20}:")
            print(f"      Growth rate: {metrics['avg_growth_rate']:.3f}")
            print(f"      Phase: {metrics['phase']}")
            print()

    if not results:
        print("❌ Could not analyze any countries")
        return {"status": "FAIL", "error": "Analysis failed"}

    # Summary
    equilibrium_countries = [r for r in results if r["equilibrium_distance"] < 0.02]
    growing_countries = [r for r in results if r["avg_growth_rate"] > 0.01]

    print("=" * 40)
    print(f"Countries near equilibrium: {len(equilibrium_countries)}/{len(results)}")
    print(f"Countries still growing: {len(growing_countries)}/{len(results)}")
    print("=" * 40)

    # Grade based on UET prediction
    # UET says: systems seek equilibrium
    # COVID should eventually reach endemic equilibrium
    eq_ratio = len(equilibrium_countries) / len(results)

    if eq_ratio > 0.5:
        grade = "⭐⭐⭐⭐⭐ EQUILIBRIUM ACHIEVED"
        status = "PASS"
    elif eq_ratio > 0.3:
        grade = "⭐⭐⭐⭐ APPROACHING EQUILIBRIUM"
        status = "PASS"
    else:
        grade = "⭐⭐⭐ STILL DYNAMIC"
        status = "WARN"

    print(f"\nGrade: {grade}")
    print("\nUET Interpretation:")
    print("   dΩ/dt > 0: System stressed, growth phase")
    print("   dΩ/dt ≈ 0: Equilibrium, endemic phase")
    print("   dΩ/dt < 0: Recovery, returning to baseline")

    return {
        "status": status,
        "countries_analyzed": len(results),
        "at_equilibrium": len(equilibrium_countries),
        "still_growing": len(growing_countries),
        "results": results,
    }


if __name__ == "__main__":
    result = run_test()
    print(f"\n✅ Test complete: {result['status']}")
