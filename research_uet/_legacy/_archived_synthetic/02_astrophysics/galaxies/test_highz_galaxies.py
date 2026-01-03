"""
JWST High-Redshift Galaxy Dynamics Test (UET Prediction)
========================================================

Test the falsifiable prediction that a₀ scales with H(z):
    a₀(z) = BETA_CI * c * H(z)
Where:
    H(z) = H₀ * sqrt(Ω_m(1+z)³ + Ω_Λ)

This script compares rotation curves for the same galaxy parameters
at z=0 vs z=5 to show the expected 'UET Boost' in the early universe.

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

import sys, os

# Add research_uet root path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from research_uet.theory.utility.universal_constants import c

# CONSTANTS (z=0)
H0_SI = 2.2e-18  # s⁻¹ (~68 km/s/Mpc)
BETA_CI = 0.18
Omega_m = 0.31
Omega_L = 0.69

# Astrophysics Units
kpc_to_m = 3.086e19
G_astro = 4.302e-6  # (km/s)² kpc / M_sun


def hubble_parameter(z):
    """Calculate H(z) in SI units."""
    return H0_SI * np.sqrt(Omega_m * (1 + z) ** 3 + Omega_L)


def get_a0_astro(z):
    """Calculate a0 at redshift z in (km/s)²/kpc."""
    H_z = hubble_parameter(z)
    a0_SI = BETA_CI * c * H_z
    return a0_SI * kpc_to_m / 1e6


def mu_simple(x):
    return x / (1 + x)


def mond_acceleration(g_newton, a0):
    if g_newton <= 0:
        return 0
    g = g_newton
    for _ in range(10):
        x = g / a0
        mu = mu_simple(x)
        g_new = g_newton / mu
        if abs(g_new - g) < 1e-5 * g:
            break
        g = g_new
    return g


def simulate_highz_prediction(z_target=5.0):
    print(f"🚀 Simulating UET Predictions for Redshift z = {z_target}")
    print("-" * 50)

    a0_z0 = get_a0_astro(0)
    a0_zh = get_a0_astro(z_target)

    print(f"a0 (z=0): {a0_z0:.4f} (km/s)²/kpc")
    print(f"a0 (z={z_target}): {a0_zh:.4f} (km/s)²/kpc (Boost: {a0_zh/a0_z0:.2f}x)")

    # Generic LSB Disk
    M_disk = 1e9  # LSB mass
    R_disk = 3.0  # kpc
    R = np.linspace(0.1, 15, 100)

    # Newtonian Acceleration
    g_N = G_astro * M_disk / R**2

    V_z0 = []
    V_zh = []

    # UET Phase 5 Params (Optimized)
    kappa = -0.7
    lambda_h = 0.7
    rho_ref = 3e7
    vol = (4 / 3) * np.pi * R_disk**3
    rho = M_disk / vol

    for gn in g_N:
        # z=0 calculation
        gm_0 = mond_acceleration(gn, a0_z0)
        fact_0 = max(1.0, (rho / rho_ref) ** kappa)
        gf_0 = (gm_0 * fact_0) + (lambda_h * gn)
        V_z0.append(np.sqrt(R * np.sqrt(gf_0**2)))  # dummy calc for R*g

        # z=high calculation
        gm_h = mond_acceleration(gn, a0_zh)
        fact_h = max(1.0, (rho / rho_ref) ** kappa)
        gf_h = (gm_h * fact_h) + (lambda_h * gn)
        V_zh.append(np.sqrt(gf_h * R))

    V_z0 = np.sqrt(
        np.array(
            [
                mond_acceleration(gn, a0_z0) * max(1.0, (rho / rho_ref) ** kappa) * r
                for gn, r in zip(g_N, R)
            ]
        )
    )
    V_zh = np.sqrt(
        np.array(
            [
                mond_acceleration(gn, a0_zh) * max(1.0, (rho / rho_ref) ** kappa) * r
                for gn, r in zip(g_N, R)
            ]
        )
    )

    plt.figure(figsize=(10, 6))
    plt.plot(R, V_z0, "b-", label="z = 0 (Current Universe)")
    plt.plot(R, V_zh, "r--", label=f"z = {z_target} (JWST Era)")
    plt.fill_between(R, V_z0, V_zh, color="red", alpha=0.1, label="UET Evolutionary Boost")

    plt.title(f"UET Prediction: Evolution of Rotation Curves (a₀ ∝ H(z))")
    plt.xlabel("Radius (kpc)")
    plt.ylabel("Circular Velocity (km/s)")
    plt.legend()
    plt.grid(True, alpha=0.3)

    output_png = "highz_evolution_prediction.png"
    plt.savefig(output_png)
    print(f"\nPrediction figure saved to {output_png}")
    print("Finding: UET predicts that high-z galaxies will show significantly higher ")
    print("rotation velocities for the same baryonic mass than local galaxies.")


if __name__ == "__main__":
    simulate_highz_prediction(z_target=5.0)
