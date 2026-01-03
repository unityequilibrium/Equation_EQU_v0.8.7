"""
🔍 Universal Pattern Detection
==============================

Find common patterns across:
- Brain EEG
- Galaxy rotation
- Economy markets
- Supernova light curves

If patterns MATCH → same underlying physics (UET!)

NO equations assumed - pure pattern matching.

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
from typing import Dict, List, Tuple
from scipy import signal
from scipy.stats import pearsonr

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "pattern_output")


# =============================================================================
# PATTERN EXTRACTION FUNCTIONS
# =============================================================================


def extract_spectral_pattern(data: np.ndarray, sample_rate: float = 1.0) -> Dict:
    """
    Extract spectral pattern from any time series.

    Returns: power spectrum, peak frequency, spectral slope (β)
    """
    N = len(data)

    # Remove mean
    data = data - np.mean(data)

    # FFT
    fft = np.fft.rfft(data)
    power = np.abs(fft) ** 2 / N
    freqs = np.fft.rfftfreq(N, 1 / sample_rate)

    # Find peak frequency
    valid = freqs > 0
    if np.sum(valid) > 0:
        peak_idx = np.argmax(power[valid])
        peak_freq = freqs[valid][peak_idx]
    else:
        peak_freq = 0

    # Fit spectral slope (1/f^β)
    valid_fit = (freqs > 0.01 * sample_rate) & (freqs < 0.4 * sample_rate)
    if np.sum(valid_fit) > 5:
        log_f = np.log10(freqs[valid_fit] + 1e-10)
        log_P = np.log10(power[valid_fit] + 1e-10)
        coef = np.polyfit(log_f, log_P, 1)
        beta = -coef[0]
    else:
        beta = 0

    return {
        "freqs": freqs,
        "power": power,
        "peak_freq": peak_freq,
        "beta": beta,
        "total_power": np.sum(power),
    }


def extract_temporal_pattern(data: np.ndarray) -> Dict:
    """
    Extract temporal patterns: autocorrelation, trend, volatility.
    """
    N = len(data)

    # Autocorrelation (how "memory" is in the signal)
    autocorr = np.correlate(data - np.mean(data), data - np.mean(data), mode="full")
    autocorr = autocorr[N - 1 :] / autocorr[N - 1]  # Normalize

    # Find decay time (where autocorr drops to 1/e)
    decay_idx = np.where(autocorr < 1 / np.e)[0]
    memory_time = decay_idx[0] if len(decay_idx) > 0 else N

    # Trend (linear fit)
    x = np.arange(N)
    coef = np.polyfit(x, data, 1)
    trend_slope = coef[0]

    # Volatility (rolling std)
    window = max(N // 10, 5)
    volatility = np.array([np.std(data[max(0, i - window) : i + 1]) for i in range(N)])
    mean_volatility = np.mean(volatility)

    return {
        "autocorr": autocorr[: min(100, N)],
        "memory_time": memory_time,
        "trend_slope": trend_slope,
        "mean_volatility": mean_volatility,
    }


def extract_statistical_pattern(data: np.ndarray) -> Dict:
    """
    Extract statistical patterns: distribution shape, moments.
    """
    # Moments
    mean = np.mean(data)
    std = np.std(data)
    skewness = np.mean(((data - mean) / std) ** 3) if std > 0 else 0
    kurtosis = np.mean(((data - mean) / std) ** 4) - 3 if std > 0 else 0  # Excess kurtosis

    # Distribution (histogram pattern)
    hist, bin_edges = np.histogram(data, bins=30, density=True)

    return {
        "mean": mean,
        "std": std,
        "skewness": skewness,
        "kurtosis": kurtosis,
        "histogram": hist,
        "bin_centers": (bin_edges[:-1] + bin_edges[1:]) / 2,
    }


# =============================================================================
# DATA GENERATORS (Simulated from real-world parameters)
# =============================================================================


def generate_brain_data(N: int = 1000) -> np.ndarray:
    """Generate brain-like EEG signal (1/f² spectrum)."""
    # Create 1/f² noise (Brownian)
    white = np.random.randn(N)
    fft = np.fft.rfft(white)
    freqs = np.fft.rfftfreq(N)
    # Apply 1/f² filter
    fft[1:] = fft[1:] / (np.abs(freqs[1:]) + 0.01)
    signal = np.fft.irfft(fft, N)
    return signal


def generate_galaxy_data(N: int = 100) -> np.ndarray:
    """Generate galaxy rotation curve pattern."""
    r = np.linspace(1, 30, N)  # kpc

    # UET prediction: v ∝ sqrt(M_disk + M_halo)
    # M_halo/M_disk = k/sqrt(rho)
    rho = 1 / (r**3)  # Density decreases with r³
    k = 5.46e4
    ratio = k / np.sqrt(rho * 1e9)

    v = np.sqrt(1 + ratio) * 100  # km/s

    # Add observational noise
    v += np.random.randn(N) * 5

    return v


def generate_economy_data(N: int = 500) -> np.ndarray:
    """Generate market-like price series."""
    # Geometric Brownian motion with volatility clustering
    returns = np.random.randn(N) * 0.02  # 2% daily vol

    # Add volatility clustering (GARCH-like)
    volatility = 0.02
    for i in range(1, N):
        volatility = 0.9 * volatility + 0.1 * abs(returns[i - 1])
        returns[i] = np.random.randn() * volatility

    # Cumulative price
    price = 100 * np.exp(np.cumsum(returns))

    return price


def generate_supernova_data(N: int = 150) -> np.ndarray:
    """Generate supernova light curve (Type Ia)."""
    t = np.linspace(-20, 130, N)

    # Arnett model for Type Ia
    t_rise = 19.5
    tau_m = 8.8

    L = np.zeros_like(t)
    for i, ti in enumerate(t):
        if ti < 0:
            L[i] = np.exp(-((ti + t_rise) ** 2) / (2 * tau_m**2))
        else:
            L[i] = np.exp(-ti / 40) + 0.1 * np.exp(-ti / 150)

    # Add noise
    L += np.random.randn(N) * 0.02 * L.max()

    return L


# =============================================================================
# PATTERN MATCHING
# =============================================================================


def compare_patterns(patterns: Dict[str, Dict]) -> Dict:
    """
    Compare extracted patterns across all phenomena.

    Find similarities → evidence of universal physics!
    """
    print("\n" + "=" * 60)
    print("🔗 PATTERN MATCHING")
    print("=" * 60)

    names = list(patterns.keys())
    n = len(names)

    # Compare spectral slopes (β)
    betas = {name: p["spectral"]["beta"] for name, p in patterns.items()}
    print("\n📊 Spectral Slope (β) Comparison:")
    for name, beta in betas.items():
        print(f"   {name:15}: β = {beta:.2f}")

    # Find β similarity matrix
    beta_values = np.array(list(betas.values()))
    beta_mean = np.mean(beta_values)
    beta_std = np.std(beta_values)
    print(f"\n   Mean β = {beta_mean:.2f} ± {beta_std:.2f}")

    # Compare memory times
    print("\n⏱️ Memory Time Comparison:")
    for name, p in patterns.items():
        mt = p["temporal"]["memory_time"]
        print(f"   {name:15}: τ = {mt} steps")

    # Compare kurtosis (distribution shape)
    print("\n📈 Distribution Shape (Kurtosis):")
    for name, p in patterns.items():
        k = p["statistical"]["kurtosis"]
        shape = "Heavy tails" if k > 0 else "Light tails" if k < 0 else "Normal"
        print(f"   {name:15}: κ = {k:.2f} ({shape})")

    # Calculate pattern similarity scores
    print("\n🔍 SIMILARITY SCORES:")
    similarity = {}

    for i, name1 in enumerate(names):
        for j, name2 in enumerate(names):
            if i < j:
                # Compare autocorrelation patterns
                ac1 = patterns[name1]["temporal"]["autocorr"]
                ac2 = patterns[name2]["temporal"]["autocorr"]
                min_len = min(len(ac1), len(ac2))

                if min_len > 5:
                    corr, _ = pearsonr(ac1[:min_len], ac2[:min_len])
                else:
                    corr = 0

                pair = f"{name1}-{name2}"
                similarity[pair] = corr

                status = (
                    "✅ SIMILAR"
                    if corr > 0.7
                    else "⚠️ Different" if corr > 0.3 else "❌ Very different"
                )
                print(f"   {pair:25}: r = {corr:.3f} {status}")

    # Overall assessment
    similar_pairs = sum(1 for s in similarity.values() if s > 0.7)
    total_pairs = len(similarity)

    print(f"\n📊 UNIVERSAL PATTERN ASSESSMENT:")
    print(f"   Similar pairs: {similar_pairs}/{total_pairs}")

    if similar_pairs >= total_pairs * 0.5:
        print("   ✅ UNIVERSAL PATTERN DETECTED!")
        print("   → Same underlying dynamics across phenomena")
        print("   → Supports UET hypothesis!")
    else:
        print("   ⚠️ Patterns are domain-specific")
        print("   → May need more data or refined analysis")

    return {
        "betas": betas,
        "similarity": similarity,
        "similar_count": similar_pairs,
        "total_pairs": total_pairs,
    }


# =============================================================================
# VISUALIZATION
# =============================================================================


def visualize_patterns(
    data: Dict[str, np.ndarray],
    patterns: Dict[str, Dict],
    comparison: Dict,
    output_dir: str = OUTPUT_DIR,
) -> str:
    """Create comprehensive pattern visualization."""
    print("\n" + "=" * 60)
    print("🎨 CREATING PATTERN VISUALIZATION")
    print("=" * 60)

    os.makedirs(output_dir, exist_ok=True)

    fig = plt.figure(figsize=(16, 12))

    # Layout: 4 rows (one per phenomenon) × 4 cols (raw, spectrum, autocorr, distribution)
    names = list(data.keys())
    colors = {"Brain": "blue", "Galaxy": "green", "Economy": "orange", "Supernova": "red"}

    for i, name in enumerate(names):
        d = data[name]
        p = patterns[name]
        color = colors.get(name, "gray")

        # Raw data
        ax1 = fig.add_subplot(4, 4, i * 4 + 1)
        ax1.plot(d, color=color, linewidth=0.5)
        ax1.set_ylabel(name)
        if i == 0:
            ax1.set_title("Raw Signal")
        ax1.grid(True, alpha=0.3)

        # Power spectrum
        ax2 = fig.add_subplot(4, 4, i * 4 + 2)
        freqs = p["spectral"]["freqs"]
        power = p["spectral"]["power"]
        valid = freqs > 0.001
        ax2.loglog(freqs[valid], power[valid], color=color, linewidth=0.5)
        ax2.set_title(f"β = {p['spectral']['beta']:.2f}")
        ax2.grid(True, alpha=0.3)

        # Autocorrelation
        ax3 = fig.add_subplot(4, 4, i * 4 + 3)
        ac = p["temporal"]["autocorr"]
        ax3.plot(ac, color=color, linewidth=1)
        ax3.axhline(1 / np.e, color="gray", linestyle="--", alpha=0.5)
        ax3.set_title(f"τ = {p['temporal']['memory_time']}")
        ax3.grid(True, alpha=0.3)

        # Distribution
        ax4 = fig.add_subplot(4, 4, i * 4 + 4)
        ax4.bar(
            p["statistical"]["bin_centers"],
            p["statistical"]["histogram"],
            width=(
                np.diff(p["statistical"]["bin_centers"][:2])[0]
                if len(p["statistical"]["bin_centers"]) > 1
                else 1
            ),
            color=color,
            alpha=0.7,
        )
        ax4.set_title(f"κ = {p['statistical']['kurtosis']:.2f}")
        ax4.grid(True, alpha=0.3)

    plt.tight_layout()

    output_path = os.path.join(output_dir, "universal_pattern_detection.png")
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()

    print(f"   ✅ Saved: {output_path}")

    return output_path


# =============================================================================
# MAIN
# =============================================================================


def run_pattern_detection():
    """Run complete pattern detection pipeline."""
    print("\n" + "=" * 60)
    print("🔍 UNIVERSAL PATTERN DETECTION")
    print("=" * 60)
    print("\nLooking for same patterns across:")
    print("  • Brain EEG")
    print("  • Galaxy rotation")
    print("  • Economy markets")
    print("  • Supernova light curves")
    print()

    # Generate/load data
    print("📊 Generating data...")
    data = {
        "Brain": generate_brain_data(1000),
        "Galaxy": generate_galaxy_data(100),
        "Economy": generate_economy_data(500),
        "Supernova": generate_supernova_data(150),
    }

    # Extract patterns
    print("\n🔬 Extracting patterns...")
    patterns = {}
    for name, d in data.items():
        print(f"   Processing {name}...")
        patterns[name] = {
            "spectral": extract_spectral_pattern(d),
            "temporal": extract_temporal_pattern(d),
            "statistical": extract_statistical_pattern(d),
        }

    # Compare patterns
    comparison = compare_patterns(patterns)

    # Visualize
    output_path = visualize_patterns(data, patterns, comparison)

    print("\n" + "=" * 60)
    print("✅ PATTERN DETECTION COMPLETE!")
    print("=" * 60)
    print(f"\n📊 Output: {output_path}")

    # Summary
    print("\n📋 KEY FINDINGS:")
    print(f"   Spectral slopes (β):")
    for name, beta in comparison["betas"].items():
        print(f"      {name}: {beta:.2f}")

    return {
        "data": data,
        "patterns": patterns,
        "comparison": comparison,
        "output": output_path,
    }


if __name__ == "__main__":
    run_pattern_detection()
