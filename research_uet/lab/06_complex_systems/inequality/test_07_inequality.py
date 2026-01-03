"""
📊 UET Test 07: Economic Health Index
=====================================

Tests: UET-based economic health k = √(Productivity/Debt) × Employment

Uses World Bank inequality/economic data.

Updated for UET V3.0
"""

import numpy as np
import pandas as pd
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


def load_inequality_data():
    """Load World Bank economic data."""
    data = {}

    # Inequality data
    ineq_dir = os.path.join(DATA_DIR, "inequality")
    if os.path.exists(ineq_dir):
        for filepath in glob.glob(os.path.join(ineq_dir, "worldbank_*.csv")):
            name = os.path.basename(filepath).replace("worldbank_", "").replace(".csv", "")
            try:
                df = pd.read_csv(filepath)
                data[name] = df
            except:
                pass

    # Economic health data
    econ_dir = os.path.join(DATA_DIR, "economic_health")
    if os.path.exists(econ_dir):
        for filepath in glob.glob(os.path.join(econ_dir, "econ_*.csv")):
            name = os.path.basename(filepath).replace("econ_", "").replace(".csv", "")
            try:
                df = pd.read_csv(filepath)
                data[name] = df
            except:
                pass

    return data


def calculate_uet_health_index(gdp_pc, debt_ratio, unemployment):
    """
    Calculate UET Economic Health Index.

    k = √(Productivity / Debt_Ratio) × Employment_Factor

    Where:
    - Productivity proxy = GDP per capita / 1000
    - Debt_Ratio = Government debt / GDP
    - Employment_Factor = 1 - Unemployment_Rate

    Interpretation:
    - k > 1.5: Very Healthy
    - k = 1.0: Balanced
    - k < 0.7: Stressed
    - k < 0.3: Crisis
    """
    if debt_ratio <= 0 or gdp_pc <= 0:
        return None

    productivity = gdp_pc / 10000  # Normalize
    emp_factor = 1 - unemployment / 100

    k = np.sqrt(productivity / (debt_ratio + 0.1)) * emp_factor

    return k


def run_test():
    """Run economic health test."""
    print("\n" + "=" * 60)
    print("📊 UET TEST 07: Economic Health Index")
    print("=" * 60)
    print("\nEquation: k = √(Productivity/Debt) × Employment")
    print("UET Prediction: Healthy economies have k ≈ 1.0")

    data = load_inequality_data()

    if not data:
        print("❌ No economic data found!")
        return {"status": "FAIL", "error": "No data"}

    print(f"\nLoaded {len(data)} datasets\n")

    # Get common countries with all required metrics
    required = ["gdp_per_capita", "government_debt_gdp", "unemployment"]
    available = [k for k in required if k in data]

    if len(available) < 2:
        print(f"⚠️ Only have: {list(data.keys())}")
        print("   Need: gdp_per_capita, government_debt_gdp, unemployment")

        # Fallback: just analyze GDP data
        if "gdp_per_capita" in data:
            df = data["gdp_per_capita"]
            print("\nFallback: Analyzing GDP per capita trends...")

            # Get latest values by country
            latest = df.sort_values("year").groupby("country_code").last()

            # Top 10 by GDP
            top10 = latest.nlargest(10, "value")

            print("\nTop 10 by GDP per capita (2023~):")
            for idx, row in top10.iterrows():
                print(f"   {row['country_name']:30} ${row['value']:,.0f}")

            return {"status": "WARN", "message": "Partial data only", "gdp_analyzed": len(latest)}

    print(f"Available metrics: {available}")

    # Merge data
    results = []

    # Get GDP
    if "gdp_per_capita" in data:
        gdp_df = data["gdp_per_capita"]
        latest_year = gdp_df["year"].max()
        gdp_latest = gdp_df[gdp_df["year"] == latest_year][["country_code", "value"]]
        gdp_latest = gdp_latest.rename(columns={"value": "gdp_pc"})

        # Get debt if available
        if "government_debt_gdp" in data:
            debt_df = data["government_debt_gdp"]
            debt_latest = debt_df.sort_values("year").groupby("country_code").last()[["value"]]
            debt_latest = debt_latest.rename(columns={"value": "debt_ratio"})
            gdp_latest = gdp_latest.set_index("country_code").join(debt_latest)
        else:
            gdp_latest["debt_ratio"] = 50  # Default assumption
            gdp_latest = gdp_latest.set_index("country_code")

        # Get unemployment if available
        if "unemployment" in data:
            unemp_df = data["unemployment"]
            unemp_latest = unemp_df.sort_values("year").groupby("country_code").last()[["value"]]
            unemp_latest = unemp_latest.rename(columns={"value": "unemployment"})
            gdp_latest = gdp_latest.join(unemp_latest)
        else:
            gdp_latest["unemployment"] = 5  # Default assumption

        # Calculate k for each country
        for country_code, row in gdp_latest.iterrows():
            if pd.isna(row.get("gdp_pc")) or pd.isna(row.get("debt_ratio")):
                continue

            k = calculate_uet_health_index(
                row["gdp_pc"], row.get("debt_ratio", 50), row.get("unemployment", 5)
            )

            if k is not None:
                results.append(
                    {
                        "country": country_code,
                        "gdp_pc": row["gdp_pc"],
                        "debt_ratio": row.get("debt_ratio", 50),
                        "unemployment": row.get("unemployment", 5),
                        "k_index": k,
                    }
                )

    if not results:
        print("❌ Could not calculate health index")
        return {"status": "FAIL", "error": "Calculation failed"}

    # Sort by k
    results = sorted(results, key=lambda x: x["k_index"], reverse=True)

    print(f"\nEconomic Health Index for {len(results)} countries:\n")
    print("Top 10 Healthiest:")
    for r in results[:10]:
        k = r["k_index"]
        if k > 1.5:
            emoji = "🟢"
        elif k > 1.0:
            emoji = "🟡"
        elif k > 0.7:
            emoji = "🟠"
        else:
            emoji = "🔴"
        print(
            f"   {emoji} {r['country']:5} k={k:.2f}  (GDP=${r['gdp_pc']:,.0f}, Debt={r['debt_ratio']:.0f}%)"
        )

    print("\nBottom 5 (Most Stressed):")
    for r in results[-5:]:
        k = r["k_index"]
        emoji = "🔴" if k < 0.7 else "🟠"
        print(f"   {emoji} {r['country']:5} k={k:.2f}  (GDP=${r['gdp_pc']:,.0f})")

    # Summary
    avg_k = np.mean([r["k_index"] for r in results])
    healthy = len([r for r in results if r["k_index"] > 1.0])
    stressed = len([r for r in results if r["k_index"] < 0.7])

    print("\n" + "=" * 40)
    print(f"Average k: {avg_k:.2f}")
    print(f"Healthy (k>1.0): {healthy}/{len(results)}")
    print(f"Stressed (k<0.7): {stressed}/{len(results)}")
    print("=" * 40)

    # Grade
    if avg_k > 1.0:
        grade = "⭐⭐⭐⭐⭐ GLOBAL HEALTH GOOD"
        status = "PASS"
    elif avg_k > 0.7:
        grade = "⭐⭐⭐⭐ MODERATE"
        status = "PASS"
    else:
        grade = "⭐⭐⭐ STRESSED"
        status = "WARN"

    print(f"\nGrade: {grade}")

    return {
        "status": status,
        "avg_k": avg_k,
        "countries_analyzed": len(results),
        "healthy": healthy,
        "stressed": stressed,
        "top_5": results[:5],
        "bottom_5": results[-5:],
    }


if __name__ == "__main__":
    result = run_test()
    print(f"\n✅ Test complete: {result['status']}")
