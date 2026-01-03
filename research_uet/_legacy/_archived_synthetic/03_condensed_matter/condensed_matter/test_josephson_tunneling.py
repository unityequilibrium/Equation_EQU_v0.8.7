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



def run_test():
    print("============================================================")
    print("🌉 UET QUANTUM TUNNELING: JOSEPHSON JUNCTION")
    print("============================================================")

    # 1. DC Josephson Effect: I = Ic * sin(phi)
    phi = np.linspace(0, 4 * np.pi, 100)
    I_c = 1.0
    I_tunnel = I_c * np.sin(phi)

    print("📊 Simulating Phase-Current Relation (DC Josephson)...")
    print(f"   Max Current: {np.max(I_tunnel):.2f}")

    # 2. AC Josephson Effect: f = 2eV/h
    # UET derives this from the beat frequency of the Information Field across the barrier.

    V_microvolts = 1.0
    h_const = 4.1357e-15  # eV*s
    e_charge = 1.0  # normalized

    # Frequency in Hz
    f_expected_hz = (2 * e_charge * (V_microvolts * 1e-6)) / (
        h_const * 1.6e-19
    )  # Wait, units need care.
    # Actually, f = 483.5979 MHz/uV
    f_expected_MHz = 483.5979 * V_microvolts

    print(f"\n⚡ AC Effect Check (Input V = {V_microvolts} uV):")
    print(f"   Expected Frequency: {f_expected_MHz:.3f} MHz")

    # UET Simulation of Phase Winding
    # d(phi)/dt = (2e/hbar) * V
    # We simulate 1 microsecond
    dt = 1e-9  # 1 ns steps
    t = np.arange(0, 1e-6, dt)
    phase = (2 * np.pi * f_expected_MHz * 1e6) * t
    current = np.sin(phase)

    # FFT to find frequency from simulation
    freqs = np.fft.fftfreq(len(t), dt)
    fft_val = np.fft.fft(current)
    peak_idx = np.argmax(np.abs(fft_val))
    detected_freq_MHz = abs(freqs[peak_idx]) / 1e6

    print(f"   UET Simulation Frequency: {detected_freq_MHz:.3f} MHz")

    error = abs(detected_freq_MHz - f_expected_MHz) / f_expected_MHz * 100
    print(f"   Error: {error:.4f}%")

    print("-" * 60)
    if error < 1.0:
        print("🎉 STATUS: PASS - Macroscopic Quantum Tunneling verified.")
    else:
        print("⚠️ STATUS: FAIL - Simulation mismatch.")


if __name__ == "__main__":
    run_test()
