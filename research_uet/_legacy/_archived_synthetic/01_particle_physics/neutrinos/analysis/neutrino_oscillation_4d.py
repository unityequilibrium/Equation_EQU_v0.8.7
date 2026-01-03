"""
🌌 Neutrino Oscillation in UET 4D Framework
============================================
Models neutrino flavor oscillation as C↔I field mixing.

Physics Mapping:
- Active neutrinos (νₑ, νμ, ντ) → C field
- Sterile neutrino (νₛ) → I field
- Mixing angle θ → Coupling β
- Mass difference Δm² → Potential curvature

⚠️ ALL SIMULATIONS ARE 4D

Updated for UET V3.0
"""

import numpy as np
import json
import sys

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

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
)  # Point to research_uet root
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../engine"))
)  # Point to engine
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../data_acquisition")))

# Import 4D solver (Central Engine)
from uet_4d_engine import UET4DSolver, create_initial_condition_3d


def load_oscillation_params() -> Dict:
    """Load PDG oscillation parameters."""
    data_path = os.path.join(os.path.dirname(__file__), "data", "oscillation_params.json")

    if os.path.exists(data_path):
        with open(data_path, "r") as f:
            return json.load(f)
    else:
        print("⚠️ Data not found, using defaults")
        return {
            "sin2_theta12": {"value": 0.307},
            "sin2_theta23_NO": {"value": 0.545},
            "sin2_theta13": {"value": 0.0220},
            "delta_m21_sq": {"value": 7.53e-5},
            "delta_m32_sq_NO": {"value": 2.453e-3},
        }


def standard_oscillation_probability(L: float, E: float, dm2: float, sin2_2theta: float) -> float:
    """
    Standard 2-flavor neutrino oscillation probability.

    P(να → νβ) = sin²(2θ) × sin²(1.27 × Δm² × L / E)

    Parameters:
    -----------
    L : float - Baseline in km
    E : float - Energy in GeV
    dm2 : float - Mass-squared difference in eV²
    sin2_2theta : float - sin²(2θ)
    """
    # Oscillation phase (natural units factor: 1.27)
    phase = 1.27 * dm2 * L / E
    return sin2_2theta * np.sin(phase) ** 2


def uet_oscillation_probability(
    L: float, E: float, dm2: float, sin2_2theta: float, beta: float, kappa: float = 0.5
) -> Tuple[float, float]:
    """
    UET-enhanced neutrino oscillation probability.

    Includes I-field (sterile neutrino) contribution.

    Returns:
    --------
    P_standard : float - Standard oscillation probability
    P_UET : float - UET-corrected probability
    """
    # Standard oscillation
    P_std = standard_oscillation_probability(L, E, dm2, sin2_2theta)

    # UET correction from Information field coupling
    # The I-field introduces an effective mass modification
    effective_dm2 = dm2 * (1 + beta * kappa / E)

    # UET oscillation phase
    phase_uet = 1.27 * effective_dm2 * L / E
    P_uet = sin2_2theta * np.sin(phase_uet) ** 2

    # Additional damping from C-I coupling (decoherence)
    damping = np.exp(-(beta**2) * L / (E * 100))  # Scale factor for realistic damping
    P_uet *= damping

    return P_std, P_uet


def simulate_neutrino_propagation_4d(
    Nx: int = 32,
    Ny: int = 32,
    Nz: int = 32,
    L_km: float = 1000.0,
    E_GeV: float = 1.0,
    dm2_eV2: float = 2.5e-3,
    sin2_2theta: float = 1.0,
    beta: float = 0.1,
    n_steps: int = 200,
) -> Dict:
    """
    Simulate neutrino propagation in 4D UET framework.

    The neutrino wave packet propagates through 3D space over time,
    with C-I mixing representing flavor oscillation.
    """
    print("=" * 60)
    print("🌌 4D NEUTRINO OSCILLATION SIMULATION")
    print("=" * 60)
    print(f"   Baseline L = {L_km} km")
    print(f"   Energy E = {E_GeV} GeV")
    print(f"   Δm² = {dm2_eV2} eV²")
    print(f"   sin²(2θ) = {sin2_2theta}")
    print(f"   UET coupling β = {beta}")
    print()

    # Map physical parameters to UET parameters
    # Δm² maps to potential curvature 'a'
    a = -dm2_eV2 * 1e3  # Scale for simulation

    # sin²(2θ) maps to C-I coupling β
    effective_beta = beta * np.sqrt(sin2_2theta)

    # Create solver
    solver = UET4DSolver(
        Nx=Nx,
        Ny=Ny,
        Nz=Nz,
        Lx=L_km / 100,
        Ly=10.0,
        Lz=10.0,  # Scaled
        dt=0.01,
        kappa=0.5,
        beta=effective_beta,
    )

    # Initial condition: localized wave packet
    # C = active neutrino (starts at 1)
    # I = sterile neutrino (starts at 0)
    x = np.linspace(0, 1, Nx)
    y = np.linspace(0, 1, Ny)
    z = np.linspace(0, 1, Nz)
    X, Y, Z = np.meshgrid(x, y, z, indexing="ij")

    # Gaussian wave packet for active neutrino
    sigma = 0.1
    C0 = np.exp(-((X - 0.5) ** 2 + (Y - 0.5) ** 2 + (Z - 0.5) ** 2) / (2 * sigma**2))
    I0 = np.zeros_like(C0)  # No sterile component initially

    print("🔄 Running 4D propagation...")

    # Run simulation
    C_final, I_final, history = solver.run(
        C0,
        I0,
        n_steps=n_steps,
        potential_type="quartic",
        a=a,
        delta=1.0,
        evolve_I=True,
        save_interval=10,
        verbose=True,
    )

    # Analyze results
    # Oscillation probability = fraction transferred to I field
    initial_C_total = np.sum(C0)
    final_C_total = np.sum(np.abs(C_final))
    final_I_total = np.sum(np.abs(I_final))

    P_disappearance = 1 - final_C_total / initial_C_total
    P_sterile = final_I_total / (final_C_total + final_I_total)

    # Compare with standard prediction
    P_std, P_uet = uet_oscillation_probability(L_km, E_GeV, dm2_eV2, sin2_2theta, beta)

    results = {
        "L_km": L_km,
        "E_GeV": E_GeV,
        "dm2_eV2": dm2_eV2,
        "sin2_2theta": sin2_2theta,
        "beta": beta,
        "P_disappearance_sim": P_disappearance,
        "P_sterile_sim": P_sterile,
        "P_standard_theory": P_std,
        "P_UET_theory": P_uet,
        "history": history,
        "C_final": C_final,
        "I_final": I_final,
    }

    print()
    print("📊 OSCILLATION RESULTS:")
    print("-" * 40)
    print(f"   P(disappearance) from simulation: {P_disappearance:.4f}")
    print(f"   P(sterile) from simulation:       {P_sterile:.4f}")
    print(f"   P(standard theory):               {P_std:.4f}")
    print(f"   P(UET theory):                    {P_uet:.4f}")

    return results


def scan_baseline_4d(
    E_GeV: float = 1.0,
    dm2: float = 2.5e-3,
    sin2_2theta: float = 1.0,
    beta: float = 0.1,
    L_values: list = None,
) -> Dict:
    """
    Scan oscillation probability vs baseline L.
    """
    if L_values is None:
        L_values = np.linspace(100, 3000, 30)

    P_std_list = []
    P_uet_list = []

    for L in L_values:
        P_std, P_uet = uet_oscillation_probability(L, E_GeV, dm2, sin2_2theta, beta)
        P_std_list.append(P_std)
        P_uet_list.append(P_uet)

    return {
        "L_km": L_values,
        "P_standard": P_std_list,
        "P_UET": P_uet_list,
        "E_GeV": E_GeV,
        "dm2": dm2,
        "beta": beta,
    }


def test_oscillation():
    """Test neutrino oscillation in 4D."""
    print("=" * 60)
    print("🧪 NEUTRINO OSCILLATION TEST")
    print("=" * 60)

    # Load real parameters
    params = load_oscillation_params()

    # Atmospheric oscillation (T2K-like)
    dm2_atm = params["delta_m32_sq_NO"]["value"]  # 2.453e-3 eV²
    sin2_theta23 = params["sin2_theta23_NO"]["value"]  # 0.545
    sin2_2theta23 = 4 * sin2_theta23 * (1 - sin2_theta23)  # ~0.99

    print(f"\n📋 Using PDG parameters:")
    print(f"   Δm²₃₂ = {dm2_atm} eV²")
    print(f"   sin²(2θ₂₃) = {sin2_2theta23:.4f}")

    # Run 4D simulation (reduced size for quick test)
    results = simulate_neutrino_propagation_4d(
        Nx=16,
        Ny=16,
        Nz=16,  # Smaller grid for test
        L_km=295,  # T2K baseline
        E_GeV=0.6,  # T2K peak energy
        dm2_eV2=dm2_atm,
        sin2_2theta=sin2_2theta23,
        beta=0.1,
        n_steps=100,
    )

    # Baseline scan
    print("\n📊 Baseline scan (analytical):")
    scan = scan_baseline_4d(
        E_GeV=0.6,
        dm2=dm2_atm,
        sin2_2theta=sin2_2theta23,
        beta=0.1,
        L_values=np.linspace(100, 1000, 10),
    )

    for L, P_std, P_uet in zip(scan["L_km"][:5], scan["P_standard"][:5], scan["P_UET"][:5]):
        print(f"   L={L:.0f} km: P_std={P_std:.3f}, P_UET={P_uet:.3f}")

    print("\n✅ Test complete!")
    return results


if __name__ == "__main__":
    test_oscillation()
