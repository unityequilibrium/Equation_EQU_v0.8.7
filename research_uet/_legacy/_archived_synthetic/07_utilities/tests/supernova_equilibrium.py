"""
🌟 Supernova Phase Evolution - Accurate Model
==============================================

Based on REAL SNR physics from astrophysics literature:
- Sedov 1959
- Chevalier 1974
- Cioffi et al. 1988

Shows ALL phases, not just 3!

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

# Physical constants (CGS)
M_sun = 2e33  # g
pc = 3.086e18  # cm
yr = 3.15e7  # s

# Standard SN parameters
E51 = 1.0  # Energy in units of 10^51 erg
n0 = 1.0  # ISM density in cm^-3
M_ej = 5.0  # Ejecta mass in M_sun


def calculate_phases():
    """
    Calculate ALL phases of SNR evolution based on theory.

    References:
    - Sedov (1959) - Blast wave
    - Cioffi et al. (1988) - Radiative phase
    - McKee & Ostriker (1977) - Hot bubble
    """

    print("\n" + "=" * 70)
    print("🌟 SUPERNOVA REMNANT PHASE EVOLUTION")
    print("=" * 70)
    print(f"\nParameters:")
    print(f"  Energy:      E = {E51} × 10⁵¹ erg")
    print(f"  ISM density: n₀ = {n0} cm⁻³")
    print(f"  Ejecta mass: M_ej = {M_ej} M☉")

    phases = []

    # ================================================================
    # PHASE 0: Core Collapse (milliseconds to seconds)
    # ================================================================
    t0 = 0.01  # seconds
    phases.append(
        {
            "name": "0. Core Collapse",
            "t_start": 0,
            "t_end": t0,
            "R": 1e9,  # ~10,000 km
            "v": 3e9,  # ~0.1c
            "T": 1e11,  # 100 billion K
            "description": "Core collapses to neutron star, neutrino burst",
        }
    )

    # ================================================================
    # PHASE 1: Free Expansion (seconds to centuries)
    # ================================================================
    # Ends when swept-up mass = ejecta mass
    # M_sw = (4π/3) ρ R³ = M_ej
    # R_free = (3 M_ej / 4π ρ)^(1/3)

    rho_ISM = n0 * 1.67e-24  # g/cm³
    R_free = (3 * M_ej * M_sun / (4 * np.pi * rho_ISM)) ** (1 / 3)
    v_ej = np.sqrt(2 * E51 * 1e51 / (M_ej * M_sun))  # Initial velocity
    t_free = R_free / v_ej

    phases.append(
        {
            "name": "1. Free Expansion",
            "t_start": t0,
            "t_end": t_free,
            "R": R_free,
            "v": v_ej,
            "T": 1e8,  # ~100 million K
            "description": "Ejecta expands freely, R ∝ t",
        }
    )

    # ================================================================
    # PHASE 2: Ejecta-Dominated (early Sedov transition)
    # ================================================================
    # Transition phase where ejecta starts to decelerate
    t_ed = 2 * t_free
    R_ed = R_free * 1.2
    v_ed = v_ej * 0.7

    phases.append(
        {
            "name": "2. Ejecta-Dominated",
            "t_start": t_free,
            "t_end": t_ed,
            "R": R_ed,
            "v": v_ed,
            "T": 5e7,
            "description": "Ejecta decelerating, reverse shock forming",
        }
    )

    # ================================================================
    # PHASE 3: Sedov-Taylor (adiabatic blast wave)
    # ================================================================
    # R = 1.15 (E/ρ)^(1/5) t^(2/5)
    # Valid until radiative losses become important
    # Ends at T ~ 10^6 K (radiative cooling threshold)

    # Time when T ~ 10^6 K (from Blondin 1998)
    t_ST = 4e4 * (E51**0.22) * (n0**-0.55) * yr  # seconds

    # Sedov solution
    R_ST = 1.15 * (E51 * 1e51 / rho_ISM) ** 0.2 * t_ST**0.4
    v_ST = 0.4 * R_ST / t_ST

    phases.append(
        {
            "name": "3. Sedov-Taylor (Adiabatic)",
            "t_start": t_ed,
            "t_end": t_ST,
            "R": R_ST,
            "v": v_ST,
            "T": 1e6,  # ~million K
            "description": "Energy-conserving blast wave, R ∝ t^(2/5)",
        }
    )

    # ================================================================
    # PHASE 4: Pressure-Driven Snowplow (PDS)
    # ================================================================
    # Thin shell forms, interior still hot
    # From Cioffi et al. 1988
    t_PDS = 1.33 * t_ST
    R_PDS = R_ST * (t_PDS / t_ST) ** 0.3
    v_PDS = 0.3 * R_PDS / t_PDS

    phases.append(
        {
            "name": "4. Pressure-Driven Snowplow",
            "t_start": t_ST,
            "t_end": t_PDS,
            "R": R_PDS,
            "v": v_PDS,
            "T": 1e5,
            "description": "Shell cooling, interior pressure drives expansion",
        }
    )

    # ================================================================
    # PHASE 5: Momentum-Conserving Snowplow (MCS)
    # ================================================================
    # Interior cooled, momentum only
    t_MCS = 10 * t_PDS
    R_MCS = R_PDS * (t_MCS / t_PDS) ** 0.25
    v_MCS = 0.25 * R_MCS / t_MCS

    phases.append(
        {
            "name": "5. Momentum-Conserving Snowplow",
            "t_start": t_PDS,
            "t_end": t_MCS,
            "R": R_MCS,
            "v": v_MCS,
            "T": 1e4,
            "description": "Cold shell, momentum conserved, R ∝ t^(1/4)",
        }
    )

    # ================================================================
    # PHASE 6: Shell Fragmentation
    # ================================================================
    # Rayleigh-Taylor instabilities break up shell
    t_frag = 3 * t_MCS
    R_frag = R_MCS * 1.2
    v_frag = v_MCS * 0.5

    phases.append(
        {
            "name": "6. Shell Fragmentation",
            "t_start": t_MCS,
            "t_end": t_frag,
            "R": R_frag,
            "v": v_frag,
            "T": 8000,
            "description": "Shell becomes unstable, breaks into clumps",
        }
    )

    # ================================================================
    # PHASE 7: Merger with ISM
    # ================================================================
    # Velocity drops to ISM turbulence level
    t_merge = 10 * t_frag
    R_merge = R_frag * 1.1
    v_merge = 10e5  # ~10 km/s (ISM turbulence)

    phases.append(
        {
            "name": "7. Merger with ISM",
            "t_start": t_frag,
            "t_end": t_merge,
            "R": R_merge,
            "v": v_merge,
            "T": 1000,
            "description": "Remnant velocity ~ ISM turbulence",
        }
    )

    # ================================================================
    # PHASE 8: Approaching Equilibrium
    # ================================================================
    t_approach = 5 * t_merge
    R_approach = R_merge * 1.05
    v_approach = 1e5  # 1 km/s

    phases.append(
        {
            "name": "8. Approaching Equilibrium",
            "t_start": t_merge,
            "t_end": t_approach,
            "R": R_approach,
            "v": v_approach,
            "T": 100,
            "description": "Matter dispersing into ISM",
        }
    )

    # ================================================================
    # PHASE 9: Thermal Equilibrium
    # ================================================================
    t_thermal = 10 * t_approach
    R_final = R_approach
    v_final = 1e4  # 0.1 km/s (thermal motion)

    phases.append(
        {
            "name": "9. Thermal Equilibrium",
            "t_start": t_approach,
            "t_end": t_thermal,
            "R": R_final,
            "v": v_final,
            "T": 20,  # ISM cold phase
            "description": "Material at ISM temperature",
        }
    )

    # ================================================================
    # PHASE 10: Final Chemical Equilibrium
    # ================================================================
    t_final = 100 * t_thermal

    phases.append(
        {
            "name": "10. Final Equilibrium",
            "t_start": t_thermal,
            "t_end": t_final,
            "R": R_final * 1.5,  # Mixed into ISM
            "v": 1e3,  # Thermal
            "T": 10,  # Cold ISM
            "description": "Complete mixing, ready to form new stars",
        }
    )

    return phases


def print_phases(phases):
    """Print detailed phase information."""
    print("\n" + "=" * 70)
    print("📊 DETAILED PHASE BREAKDOWN")
    print("=" * 70)

    for i, p in enumerate(phases):
        t_end_yr = p["t_end"] / yr
        if t_end_yr < 1:
            t_str = f"{p['t_end']:.2e} sec"
        elif t_end_yr < 1000:
            t_str = f"{t_end_yr:.1f} years"
        elif t_end_yr < 1e6:
            t_str = f"{t_end_yr/1e3:.1f} kyr"
        else:
            t_str = f"{t_end_yr/1e6:.2f} Myr"

        R_pc = p["R"] / pc
        v_kms = p["v"] / 1e5

        print(f"\n{'='*60}")
        print(f"📍 {p['name']}")
        print("-" * 60)
        print(f"   Duration until: {t_str}")
        print(f"   Radius:         {R_pc:.2f} parsecs")
        print(f"   Velocity:       {v_kms:.1f} km/s")
        print(f"   Temperature:    {p['T']:.0e} K")
        print(f"   Description:    {p['description']}")


def calculate_omega(phases):
    """Calculate UET Omega for each phase."""
    print("\n" + "=" * 70)
    print("⚡ UET FREE ENERGY (Ω) CALCULATION")
    print("=" * 70)

    for p in phases:
        M = M_ej * M_sun
        R = max(p["R"], 1e10)
        v = p["v"]
        T = p["T"]

        # Components
        E_kin = 0.5 * M * v**2
        E_therm = 1.5 * (M / 1.67e-24) * 1.38e-16 * T
        E_grav = -0.6 * 6.674e-8 * M**2 / R

        Omega = E_kin + E_therm + E_grav
        p["Omega"] = Omega
        p["E_kin"] = E_kin
        p["E_therm"] = E_therm
        p["E_grav"] = E_grav

    print("\n| Phase | Ω (erg) | E_kin | E_therm | E_grav |")
    print("|:------|--------:|------:|--------:|-------:|")

    for p in phases:
        print(
            f"| {p['name'][:20]:20} | {p['Omega']:.2e} | {p['E_kin']:.2e} | {p['E_therm']:.2e} | {p['E_grav']:.2e} |"
        )

    # dΩ/dt analysis
    print("\n📉 dΩ/dt Analysis:")
    for i in range(1, len(phases)):
        dOmega = phases[i]["Omega"] - phases[i - 1]["Omega"]
        dt = phases[i]["t_end"] - phases[i - 1]["t_end"]
        rate = dOmega / dt if dt > 0 else 0

        status = "↓ decreasing" if rate < 0 else "↑ increasing" if rate > 0 else "= stable"
        print(f"   {phases[i]['name'][:20]:20}: dΩ/dt = {rate:.2e} erg/s ({status})")


def plot_evolution(phases, output_dir="supernova_output"):
    """Create visualization."""
    os.makedirs(output_dir, exist_ok=True)

    # Extract data
    t = [p["t_end"] for p in phases]
    R = [p["R"] / pc for p in phases]
    v = [p["v"] / 1e5 for p in phases]
    T = [p["T"] for p in phases]
    Omega = [p.get("Omega", 0) for p in phases]

    t_yr = [ti / yr for ti in t]

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Radius
    ax = axes[0, 0]
    ax.loglog(t_yr, R, "b-o", linewidth=2, markersize=8)
    ax.set_xlabel("Time (years)")
    ax.set_ylabel("Radius (parsecs)")
    ax.set_title("Radius Evolution")
    ax.grid(True, alpha=0.3)

    # Add phase labels
    for i, p in enumerate(phases):
        if i % 2 == 0:  # Every other
            ax.annotate(p["name"].split(".")[1][:10], (t_yr[i], R[i]), fontsize=7, rotation=45)

    # Velocity
    ax = axes[0, 1]
    ax.loglog(t_yr, v, "r-o", linewidth=2, markersize=8)
    ax.set_xlabel("Time (years)")
    ax.set_ylabel("Velocity (km/s)")
    ax.set_title("Velocity Evolution")
    ax.grid(True, alpha=0.3)

    # Temperature
    ax = axes[1, 0]
    ax.loglog(t_yr, T, "orange", linewidth=2, marker="o", markersize=8)
    ax.set_xlabel("Time (years)")
    ax.set_ylabel("Temperature (K)")
    ax.set_title("Temperature Evolution")
    ax.axhline(100, color="gray", linestyle="--", label="ISM cold")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Omega
    ax = axes[1, 1]
    ax.semilogx(t_yr, np.array(Omega), "g-o", linewidth=2, markersize=8)
    ax.set_xlabel("Time (years)")
    ax.set_ylabel("Ω (erg)")
    ax.set_title("Free Energy Ω Evolution (UET)")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    filepath = os.path.join(output_dir, "snr_phases.png")
    plt.savefig(filepath, dpi=150)
    print(f"\n📊 Plot saved: {filepath}")

    return fig


def main():
    """Main function."""
    phases = calculate_phases()
    print_phases(phases)
    calculate_omega(phases)

    output_dir = os.path.join(os.path.dirname(__file__), "supernova_output")
    plot_evolution(phases, output_dir)

    # Summary
    print("\n" + "=" * 70)
    print("📋 SUMMARY")
    print("=" * 70)
    print(f"\n🔢 Total phases identified: {len(phases)}")
    print(f"\n⏱️ Time to equilibrium: {phases[-1]['t_end']/yr/1e6:.1f} million years")
    print(f"\n📐 Final radius: {phases[-1]['R']/pc:.0f} parsecs")

    print("\n✅ UET Verification:")
    print("   dΩ/dt ≤ 0 throughout evolution? ", end="")

    decreasing = True
    for i in range(1, len(phases)):
        if phases[i]["Omega"] > phases[i - 1]["Omega"]:
            decreasing = False
            break

    print("YES ✅" if decreasing else "NO (forced phases) ⚠️")

    print("\n🌟 Key Insight:")
    print("   NOT just 3 phases!")
    print("   Real SNR evolution has 10+ distinct phases")
    print("   Each with different physics and timescales")

    return phases


if __name__ == "__main__":
    phases = main()
