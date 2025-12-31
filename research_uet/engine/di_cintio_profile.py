"""
🌌 Di Cintio DC14 Cored Dark Matter Profile
=============================================
Implementation of the mass-dependent dark matter density profile
from Di Cintio et al. (2014, MNRAS 441, 2986).

The DC14 profile accounts for baryonic feedback effects that
transform cuspy NFW profiles into cored profiles in dwarf galaxies.

Key insight: The profile shape depends on M*/M_halo ratio.
- Cuspy at extremes (very low or very high M*/M_halo)
- Cored at "sweet spot" (M*/M_halo ~ 0.5%)
"""

import numpy as np


def dc14_profile_params(M_star, M_halo):
    """
    Calculate Di Cintio DC14 profile parameters (α, β, γ) as functions
    of stellar-to-halo mass ratio.

    From Di Cintio et al. 2014, Equations 1-4.

    Parameters:
    -----------
    M_star : float - Stellar mass in solar masses
    M_halo : float - Halo mass (virial mass) in solar masses

    Returns:
    --------
    tuple: (alpha, beta, gamma) - Profile shape parameters
    """
    # Stellar-to-halo mass ratio (log scale)
    X = np.log10(M_star / M_halo)

    # Valid range: -4.1 < X < -1.3
    # Outside this range, use boundary values
    X = np.clip(X, -4.1, -1.3)

    # Fitting functions from Di Cintio et al. 2014
    # These were calibrated from hydrodynamical simulations

    # Alpha (transition sharpness)
    alpha = 2.94 - np.log10((10 ** (X + 2.33)) ** (-1.08) + (10 ** (X + 2.33)) ** 2.29)

    # Beta (outer slope)
    beta = 4.23 + 1.34 * X + 0.26 * X**2

    # Gamma (inner slope - most important for cores!)
    # gamma = 0 is fully cored, gamma = -1 is NFW cuspy
    gamma = -0.06 + np.log10((10 ** (X + 2.56)) ** (-0.68) + 10 ** (X + 2.56))

    # Ensure physical bounds
    alpha = np.clip(alpha, 0.5, 5.0)
    beta = np.clip(beta, 2.0, 6.0)
    gamma = np.clip(gamma, -1.0, 0.0)  # -1 = cuspy, 0 = cored

    return alpha, beta, gamma


def dc14_density(r, M_halo, c, M_star, r_s=None):
    """
    DC14 dark matter density profile.

    ρ(r) = ρ_s / [(r/r_s)^γ × (1 + (r/r_s)^α)^((β-γ)/α)]

    Parameters:
    -----------
    r : float or array - Radius in kpc
    M_halo : float - Halo mass in solar masses
    c : float - Concentration parameter
    M_star : float - Stellar mass in solar masses
    r_s : float - Scale radius in kpc (default: r_vir / c)

    Returns:
    --------
    float or array - Density in Msun/kpc^3
    """
    # Get profile parameters
    alpha, beta, gamma = dc14_profile_params(M_star, M_halo)

    # Virial radius (approximation: R_vir ~ (M_halo / 1e12)^(1/3) × 200 kpc)
    R_vir = 200 * (M_halo / 1e12) ** (1 / 3)  # kpc

    # Scale radius
    if r_s is None:
        r_s = R_vir / c

    # Characteristic density (from enclosed mass constraint)
    # Simplified: use NFW-like normalization then adjust
    rho_crit = 2.775e11  # h^2 Msun/Mpc^3 → ~1e-6 Msun/kpc^3
    delta_c = (200 / 3) * c**3 / (np.log(1 + c) - c / (1 + c))
    rho_s = delta_c * rho_crit * 1e-9  # Convert to Msun/kpc^3

    # DC14 profile
    x = r / r_s
    rho = rho_s / (x**gamma * (1 + x**alpha) ** ((beta - gamma) / alpha))

    return rho


def dc14_enclosed_mass(r, M_halo, c, M_star):
    """
    Enclosed dark matter mass within radius r for DC14 profile.
    Uses numerical integration.

    Parameters:
    -----------
    r : float - Radius in kpc
    M_halo : float - Halo mass in solar masses
    c : float - Concentration parameter
    M_star : float - Stellar mass in solar masses

    Returns:
    --------
    float - Enclosed mass in solar masses
    """
    from scipy import integrate

    def integrand(r_prime):
        return 4 * np.pi * r_prime**2 * dc14_density(r_prime, M_halo, c, M_star)

    # Avoid r=0 singularity
    r_min = r * 1e-6
    M_enc, _ = integrate.quad(integrand, r_min, r)

    return M_enc


def dc14_rotation_velocity(r, M_halo, c, M_star, M_disk, R_disk):
    """
    Rotation velocity from DC14 halo + exponential disk.

    V^2 = G × (M_halo_enc + M_disk_enc) / r

    Parameters:
    -----------
    r : float - Radius in kpc
    M_halo : float - Halo mass in solar masses
    c : float - Concentration parameter
    M_star : float - Stellar mass in solar masses
    M_disk : float - Disk mass in solar masses
    R_disk : float - Disk scale length in kpc

    Returns:
    --------
    float - Rotation velocity in km/s
    """
    G = 4.302e-6  # kpc (km/s)^2 / Msun

    # Halo contribution (DC14)
    alpha, beta, gamma = dc14_profile_params(M_star, M_halo)

    # Simplified enclosed mass (avoiding full integration for speed)
    # Use NFW-like formula with gamma correction for inner slope
    R_vir = 200 * (M_halo / 1e12) ** (1 / 3)
    r_s = R_vir / c
    x = r / r_s

    # Modified NFW enclosed mass with core correction
    core_factor = 1.0 / (1.0 - gamma)  # gamma = 0 → factor = 1, gamma = -1 → factor = 0.5
    M_halo_enc = (
        M_halo * core_factor * (np.log(1 + x) - x / (1 + x)) / (np.log(1 + c) - c / (1 + c))
    )

    # Disk contribution (exponential disk)
    x_disk = r / R_disk
    M_disk_enc = M_disk * (1 - (1 + x_disk) * np.exp(-x_disk))

    # Bulge (small contribution for dwarfs)
    M_bulge_enc = 0.1 * M_disk_enc

    # Total
    M_total = M_halo_enc + M_disk_enc + M_bulge_enc
    V = np.sqrt(G * M_total / (r + 0.01))

    return V


def dc14_concentration(M_halo, z=0):
    """
    Mass-concentration relation from Dutton & Macciò 2014.

    log10(c) = a + b × log10(M_halo / (10^12 h^-1 Msun))
    """
    h = 0.7  # Hubble parameter
    log_M = np.log10(M_halo / (1e12 / h))

    # z=0 parameters
    a = 0.905 - 0.101 * z
    b = -0.101 + 0.026 * z

    log_c = a + b * log_M
    return 10**log_c


def compare_nfw_vs_dc14(M_star, M_halo, show_plot=False):
    """
    Compare NFW (cuspy) vs DC14 (cored) profiles.

    Returns the "core factor" - how much flatter the inner profile is.
    """
    alpha, beta, gamma = dc14_profile_params(M_star, M_halo)

    # NFW has gamma = -1 (cuspy)
    # DC14 at sweet spot has gamma ≈ 0 (cored)
    core_factor = 1 + gamma  # 0 = NFW-like, 1 = fully cored

    return {
        "M_star_M_halo_ratio": M_star / M_halo,
        "log_ratio": np.log10(M_star / M_halo),
        "alpha": alpha,
        "beta": beta,
        "gamma": gamma,
        "core_factor": core_factor,
        "is_cored": gamma > -0.5,
    }


if __name__ == "__main__":
    print("=" * 60)
    print("🌌 Di Cintio DC14 Cored Profile Model")
    print("=" * 60)
    print()

    # Test cases spanning the mass range
    test_cases = [
        ("Ultra-faint dwarf", 1e5, 1e9),
        ("Dwarf irregular", 1e7, 1e10),
        ("Sweet spot (max core)", 2e8, 1e11),
        ("Massive dwarf", 1e9, 5e11),
        ("Milky Way", 5e10, 1e12),
    ]

    print(f"{'Galaxy Type':<20} {'M*/M_halo':<12} {'γ (inner)':<12} {'Core?':<8}")
    print("-" * 60)

    for name, M_star, M_halo in test_cases:
        result = compare_nfw_vs_dc14(M_star, M_halo)
        ratio = f"{result['log_ratio']:.2f}"
        gamma = f"{result['gamma']:.2f}"
        cored = "✅ YES" if result["is_cored"] else "❌ No"
        print(f"{name:<20} 10^{ratio:<8} {gamma:<12} {cored:<8}")

    print()
    print("Key insight: γ → 0 means CORED (feedback worked)")
    print("           γ → -1 means CUSPY (NFW-like)")
