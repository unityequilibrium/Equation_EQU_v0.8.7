"""
🧠 Brain EEG Test
=================
Test UET's β prediction using real EEG data.
UET predicts: β ≈ 2 (1/f² spectrum = Brownian motion)

Updated for UET V3.0
"""

import numpy as np

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

# Try to load real EEG data
EEG_PATH = "research_v3/03_universal_physics/data/Real_EEG.txt"


def load_eeg_data():
    """Load EEG data from research_v3."""
    if os.path.exists(EEG_PATH):
        data = np.loadtxt(EEG_PATH)
        print(f"✅ Loaded real EEG data: {len(data)} samples")
        return data
    else:
        print("⚠️ Real EEG not found, generating synthetic pink noise")
        # Pink noise (1/f) simulation
        N = 3000
        white = np.random.randn(N)
        X = np.fft.rfft(white)
        S = 1.0 / np.sqrt(np.arange(1, len(X) + 1))
        pink = np.fft.irfft(X * S).real * 50
        return pink


def compute_spectral_slope(signal, fs=200):
    """
    Compute spectral slope β from power spectrum.

    UET predicts β ≈ 2 for healthy brain (1/f² spectrum)
    """
    # Compute power spectrum
    N = len(signal)
    X = np.fft.rfft(signal)
    P = np.abs(X) ** 2 / N
    f = np.fft.rfftfreq(N, 1 / fs)

    # Fit in log-log space (1-50 Hz range)
    valid = (f > 1) & (f < 50)
    if np.sum(valid) < 10:
        return None, None

    log_f = np.log10(f[valid])
    log_P = np.log10(P[valid] + 1e-10)

    # Linear fit: log(P) = -β * log(f) + c
    coef = np.polyfit(log_f, log_P, 1)
    beta = -coef[0]  # Negative because P ∝ 1/f^β

    return beta, (f[valid], P[valid])


def run_test():
    print("=" * 60)
    print("🧠 BRAIN EEG TEST (UET Spectral Slope)")
    print("=" * 60)
    print()
    print("UET Prediction: β ≈ 2.0 (1/f² spectrum)")
    print()

    # Load data
    eeg = load_eeg_data()

    # Compute spectral slope
    beta, spectrum = compute_spectral_slope(eeg)

    if beta is None:
        print("❌ Could not compute spectral slope")
        return

    print(f"\n📊 Results:")
    print(f"   Spectral slope β = {beta:.2f}")
    print(f"   Expected (UET):   β ≈ 2.0")
    print()

    # Evaluate
    error = abs(beta - 2.0) / 2.0 * 100

    if abs(beta - 2.0) < 0.5:
        status = "✅ EXCELLENT"
    elif abs(beta - 2.0) < 1.0:
        status = "✅ GOOD"
    else:
        status = "⚠️ DEVIATION"

    print("=" * 60)
    print(f"Result: β = {beta:.2f} (error: {error:.1f}%)")
    print(f"Status: {status}")
    print("=" * 60)

    if 1.5 < beta < 2.5:
        print()
        print("🧠 Interpretation:")
        print("   Brain operates as 'information fluid'")
        print("   1/f² spectrum = Brownian-like dynamics")
        print("   Optimal for exploration + memory")


if __name__ == "__main__":
    run_test()
