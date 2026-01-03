"""
🔍 Universal Pattern Detection with REAL DATA
==============================================

Uses ONLY existing real data from workspace:

DATA SOURCES (all pre-existing):
├── Galaxy: NGC6503_rotmod.dat (SPARC)
├── Brain: eeg_data/Real_EEG_Sample.npy (MNE)
├── Economy: sp500_bubble.csv
├── Bio: hrv_stress.csv (HRV)
├── AI: llm_training.csv
└── Social: social_polarization.csv

NO synthetic data. Pattern detection from real measurements only.

Updated for UET V3.0
"""

import numpy as np
import matplotlib.pyplot as plt
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

import pandas as pd
from typing import Dict, Tuple, Optional
from scipy.stats import pearsonr

# Paths relative to workspace root
WORKSPACE = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "real_pattern_output")


# =============================================================================
# REAL DATA LOADERS
# =============================================================================


def load_galaxy_real() -> Tuple[Optional[np.ndarray], str]:
    """Load NGC6503 rotation curve from SPARC."""
    paths = [
        os.path.join(WORKSPACE, "research_v3", "01_data", "NGC6503_rotmod.dat"),
        os.path.join(os.path.dirname(__file__), "NGC6503_rotmod.dat"),
    ]

    for path in paths:
        if os.path.exists(path):
            try:
                data = np.loadtxt(path, skiprows=3)
                v_obs = data[:, 3]  # Observed velocity column
                print(f"   ✅ Galaxy: {path} ({len(v_obs)} points)")
                return v_obs, "Galaxy (NGC6503)"
            except Exception as e:
                print(f"   ❌ Galaxy load error: {e}")

    print("   ❌ Galaxy: NGC6503_rotmod.dat not found")
    return None, "Galaxy"


def load_brain_real() -> Tuple[Optional[np.ndarray], str]:
    """Load real EEG data from MNE download."""
    paths = [
        os.path.join(os.path.dirname(__file__), "eeg_data", "Real_EEG_Sample.npy"),
        os.path.join(WORKSPACE, "research_uet", "evidence", "eeg_data", "Real_EEG_Sample.npy"),
    ]

    for path in paths:
        if os.path.exists(path):
            try:
                data = np.load(path)
                # Take 1D slice if multi-dimensional
                if data.ndim > 1:
                    data = data.flatten()[:5000]
                else:
                    data = data[:5000]
                print(f"   ✅ Brain: {path} ({len(data)} samples)")
                return data, "Brain (EEG)"
            except Exception as e:
                print(f"   ❌ Brain load error: {e}")

    print("   ❌ Brain: Real_EEG_Sample.npy not found")
    return None, "Brain"


def load_economy_real() -> Tuple[Optional[np.ndarray], str]:
    """Load S&P500 bubble data."""
    paths = [
        os.path.join(WORKSPACE, "research_v3", "01_data", "sp500_bubble.csv"),
    ]

    for path in paths:
        if os.path.exists(path):
            try:
                df = pd.read_csv(path, comment="#")
                # Create time series from earnings or volume
                if "Earnings" in df.columns:
                    data = df["Earnings"].values
                elif "Volume_Billions" in df.columns:
                    data = df["Volume_Billions"].values
                else:
                    data = df.iloc[:, 1].values
                print(f"   ✅ Economy: {path} ({len(data)} points)")
                return data.astype(float), "Economy (S&P500)"
            except Exception as e:
                print(f"   ❌ Economy load error: {e}")

    print("   ❌ Economy: sp500_bubble.csv not found")
    return None, "Economy"


def load_bio_real() -> Tuple[Optional[np.ndarray], str]:
    """Load HRV stress data."""
    paths = [
        os.path.join(WORKSPACE, "research_v3", "01_data", "hrv_stress.csv"),
    ]

    for path in paths:
        if os.path.exists(path):
            try:
                df = pd.read_csv(path, comment="#")
                # Extract RR intervals
                rr_cols = [c for c in df.columns if c.startswith("RR")]
                if rr_cols:
                    data = df[rr_cols].values.flatten()
                else:
                    data = df.iloc[:, 1:].values.flatten()
                data = data[~np.isnan(data)]
                print(f"   ✅ Bio: {path} ({len(data)} intervals)")
                return data.astype(float), "Bio (HRV)"
            except Exception as e:
                print(f"   ❌ Bio load error: {e}")

    print("   ❌ Bio: hrv_stress.csv not found")
    return None, "Bio"


def load_ai_real() -> Tuple[Optional[np.ndarray], str]:
    """Load LLM training loss curve."""
    paths = [
        os.path.join(WORKSPACE, "research_v3", "01_data", "llm_training.csv"),
    ]

    for path in paths:
        if os.path.exists(path):
            try:
                df = pd.read_csv(path, comment="#")
                if "Training_Loss" in df.columns:
                    data = df["Training_Loss"].values
                else:
                    data = df.iloc[:, 1].values
                print(f"   ✅ AI: {path} ({len(data)} steps)")
                return data.astype(float), "AI (LLM Loss)"
            except Exception as e:
                print(f"   ❌ AI load error: {e}")

    print("   ❌ AI: llm_training.csv not found")
    return None, "AI"


def load_social_real() -> Tuple[Optional[np.ndarray], str]:
    """Load social polarization data."""
    paths = [
        os.path.join(WORKSPACE, "research_v3", "01_data", "social_polarization.csv"),
    ]

    for path in paths:
        if os.path.exists(path):
            try:
                df = pd.read_csv(path, comment="#")
                if "Polarization_Score" in df.columns:
                    data = df["Polarization_Score"].values
                else:
                    data = df.iloc[:, 1].values
                print(f"   ✅ Social: {path} ({len(data)} points)")
                return data.astype(float), "Social (Polarization)"
            except Exception as e:
                print(f"   ❌ Social load error: {e}")

    print("   ❌ Social: social_polarization.csv not found")
    return None, "Social"


# =============================================================================
# PATTERN EXTRACTION (same as before)
# =============================================================================


def extract_spectral_slope(data: np.ndarray) -> float:
    """Extract spectral slope β from power spectrum."""
    N = len(data)
    data = data - np.mean(data)

    fft = np.fft.rfft(data)
    power = np.abs(fft) ** 2 / N
    freqs = np.fft.rfftfreq(N)

    valid = (freqs > 0.01) & (freqs < 0.4) & (power > 0)
    if np.sum(valid) > 5:
        log_f = np.log10(freqs[valid])
        log_P = np.log10(power[valid] + 1e-10)
        coef = np.polyfit(log_f, log_P, 1)
        return -coef[0]
    return 0.0


def extract_autocorr(data: np.ndarray, max_lag: int = 50) -> np.ndarray:
    """Extract normalized autocorrelation."""
    data = data - np.mean(data)
    N = len(data)
    autocorr = np.correlate(data, data, mode="full")
    autocorr = autocorr[N - 1 : N - 1 + max_lag]
    if autocorr[0] != 0:
        autocorr = autocorr / autocorr[0]
    return autocorr


def extract_kurtosis(data: np.ndarray) -> float:
    """Extract excess kurtosis."""
    mean = np.mean(data)
    std = np.std(data)
    if std > 0:
        return np.mean(((data - mean) / std) ** 4) - 3
    return 0.0


# =============================================================================
# PATTERN COMPARISON
# =============================================================================


def compare_real_patterns(datasets: Dict[str, np.ndarray]) -> Dict:
    """Compare patterns across all real datasets."""
    print("\n" + "=" * 60)
    print("🔗 COMPARING PATTERNS FROM REAL DATA")
    print("=" * 60)

    results = {
        "spectral_slopes": {},
        "kurtosis": {},
        "autocorr_similarity": {},
    }

    names = list(datasets.keys())
    autocorrs = {}

    # Extract patterns
    print("\n📊 Spectral Slopes (β):")
    for name, data in datasets.items():
        beta = extract_spectral_slope(data)
        kurtosis = extract_kurtosis(data)
        autocorrs[name] = extract_autocorr(data)

        results["spectral_slopes"][name] = beta
        results["kurtosis"][name] = kurtosis
        print(f"   {name:25}: β = {beta:.2f}, κ = {kurtosis:.2f}")

    # Compare autocorrelations (pattern similarity)
    print("\n🔍 AUTOCORRELATION SIMILARITY:")
    for i, name1 in enumerate(names):
        for j, name2 in enumerate(names):
            if i < j:
                ac1 = autocorrs[name1]
                ac2 = autocorrs[name2]
                min_len = min(len(ac1), len(ac2))

                if min_len > 5:
                    corr, pval = pearsonr(ac1[:min_len], ac2[:min_len])
                else:
                    corr, pval = 0, 1

                pair = f"{name1.split()[0]}-{name2.split()[0]}"
                results["autocorr_similarity"][pair] = {"r": corr, "p": pval}

                if corr > 0.7:
                    status = "✅ SIMILAR"
                elif corr > 0.3:
                    status = "⚠️ Weak"
                else:
                    status = "❌ Different"

                print(f"   {pair:30}: r = {corr:.3f} (p={pval:.3f}) {status}")

    # Count similar pairs
    similar = sum(1 for s in results["autocorr_similarity"].values() if s["r"] > 0.7)
    total = len(results["autocorr_similarity"])

    results["similar_pairs"] = similar
    results["total_pairs"] = total

    print(f"\n📊 RESULT: {similar}/{total} pairs show similar dynamics")

    if similar >= total * 0.5:
        print("   ✅ UNIVERSAL PATTERN CONFIRMED FROM REAL DATA!")
    else:
        print("   ⚠️ Patterns are domain-specific")

    return results


# =============================================================================
# VISUALIZATION
# =============================================================================


def visualize_real_patterns(datasets: Dict, results: Dict, output_dir: str = OUTPUT_DIR):
    """Create visualization of real data patterns."""
    print("\n" + "=" * 60)
    print("🎨 CREATING REAL DATA VISUALIZATION")
    print("=" * 60)

    os.makedirs(output_dir, exist_ok=True)

    n = len(datasets)
    fig, axes = plt.subplots(n, 3, figsize=(15, 3 * n))

    colors = ["blue", "green", "orange", "red", "purple", "brown"]

    for i, (name, data) in enumerate(datasets.items()):
        color = colors[i % len(colors)]

        # Raw data
        ax1 = axes[i, 0] if n > 1 else axes[0]
        ax1.plot(data[: min(500, len(data))], color=color, linewidth=0.5)
        ax1.set_ylabel(name.split()[0])
        if i == 0:
            ax1.set_title("Raw Signal (REAL DATA)")
        ax1.grid(True, alpha=0.3)

        # Power spectrum
        ax2 = axes[i, 1] if n > 1 else axes[1]
        fft = np.fft.rfft(data - np.mean(data))
        power = np.abs(fft) ** 2
        freqs = np.fft.rfftfreq(len(data))
        valid = freqs > 0.001
        ax2.loglog(freqs[valid], power[valid], color=color, linewidth=0.5)
        beta = results["spectral_slopes"].get(name, 0)
        ax2.set_title(f"β = {beta:.2f}")
        ax2.grid(True, alpha=0.3)

        # Autocorrelation
        ax3 = axes[i, 2] if n > 1 else axes[2]
        ac = extract_autocorr(data)
        ax3.plot(ac, color=color, linewidth=1)
        ax3.axhline(1 / np.e, color="gray", linestyle="--", alpha=0.5)
        ax3.set_title("Autocorrelation")
        ax3.grid(True, alpha=0.3)

    plt.tight_layout()

    output_path = os.path.join(output_dir, "real_data_pattern_analysis.png")
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()

    print(f"   ✅ Saved: {output_path}")
    return output_path


# =============================================================================
# MAIN
# =============================================================================


def run_real_pattern_analysis():
    """Run pattern analysis on REAL data only."""
    print("\n" + "=" * 60)
    print("🔍 UNIVERSAL PATTERN DETECTION: REAL DATA ONLY")
    print("=" * 60)
    print("\n⚠️ NO SYNTHETIC DATA - All from existing files")
    print()

    # Load all real datasets
    print("📂 Loading real data from workspace...")

    loaders = [
        load_galaxy_real,
        load_brain_real,
        load_economy_real,
        load_bio_real,
        load_ai_real,
        load_social_real,
    ]

    datasets = {}
    for loader in loaders:
        data, name = loader()
        if data is not None and len(data) > 10:
            datasets[name] = data

    if len(datasets) < 2:
        print("\n❌ ERROR: Need at least 2 datasets for comparison!")
        return None

    print(f"\n✅ Loaded {len(datasets)} real datasets")

    # Compare patterns
    results = compare_real_patterns(datasets)

    # Visualize
    output_path = visualize_real_patterns(datasets, results)

    print("\n" + "=" * 60)
    print("✅ REAL DATA ANALYSIS COMPLETE!")
    print("=" * 60)
    print(f"\n📊 Output: {output_path}")

    # Summary
    print("\n📋 SUMMARY (REAL DATA ONLY):")
    print(f"   Datasets analyzed: {len(datasets)}")
    print(f"   Similar pairs: {results['similar_pairs']}/{results['total_pairs']}")

    for name, beta in results["spectral_slopes"].items():
        print(f"   {name}: β = {beta:.2f}")

    return results


if __name__ == "__main__":
    run_real_pattern_analysis()
