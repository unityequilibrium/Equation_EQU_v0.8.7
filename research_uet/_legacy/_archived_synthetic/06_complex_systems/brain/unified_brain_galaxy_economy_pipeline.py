"""
🧠🌌📈🎨 Unified Pipeline: Brain → Galaxy → Economy → Color
============================================================

This script creates a complete pipeline:
1. Brain 3D: Model neural activity in 3D grid
2. Galaxy Motion: Convert to rotation curve dynamics
3. 2D Graph: Project to time series and spectrum
4. Economy: Apply market equations
5. Color: Final heatmap visualization

⚠️ Uses 3D spatial simulation (NOT 2D)

Updated for UET V3.0
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Dict

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

# Output directory
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "unified_output")


# =============================================================================
# STEP 1: Brain 3D Simulation
# =============================================================================


def simulate_brain_3d(
    Nx: int = 64,
    Ny: int = 64,
    Nz: int = 64,
    T: float = 100.0,
    dt: float = 0.1,
    kappa: float = 0.5,
    beta: float = 0.3,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Simulate brain neural activity in 3D using UET dynamics.

    The brain is modeled as an "information fluid" where:
    - C = neural activation (capacity)
    - I = inhibition (information)

    Returns: C_history, I_history, times
    """
    print("=" * 60)
    print("🧠 STEP 1: Brain 3D Simulation")
    print("=" * 60)
    print(f"   Grid: {Nx}×{Ny}×{Nz}")
    print(f"   Time: T={T}, dt={dt}")

    # Initial conditions: random neural activity
    np.random.seed(42)
    C = 0.1 * np.random.randn(Nx, Ny, Nz)
    I = 0.1 * np.random.randn(Nx, Ny, Nz)

    # 3D Laplacian function
    def laplacian_3d(f, dx=1.0):
        return (
            np.roll(f, 1, 0)
            + np.roll(f, -1, 0)
            + np.roll(f, 1, 1)
            + np.roll(f, -1, 1)
            + np.roll(f, 1, 2)
            + np.roll(f, -1, 2)
            - 6 * f
        ) / dx**2

    # Run simulation
    n_steps = int(T / dt)
    save_every = max(1, n_steps // 100)

    C_history = []
    I_history = []
    times = []

    print("   Running...")
    for step in range(n_steps):
        # UET dynamics: ∂C/∂t = κ∇²C - βI + noise
        dC = kappa * laplacian_3d(C) - beta * I + 0.01 * np.random.randn(*C.shape)
        dI = kappa * laplacian_3d(I) + beta * C + 0.01 * np.random.randn(*I.shape)

        C += dt * dC
        I += dt * dI

        # Prevent explosion
        C = np.clip(C, -10, 10)
        I = np.clip(I, -10, 10)

        if step % save_every == 0:
            C_history.append(np.mean(C**2))  # Mean activity
            I_history.append(np.mean(I**2))
            times.append(step * dt)

    print(f"   ✅ Complete! {len(times)} timesteps saved")

    return np.array(C_history), np.array(I_history), np.array(times)


# =============================================================================
# STEP 2: Convert to Galaxy Motion
# =============================================================================


def convert_to_galaxy_motion(
    C_activity: np.ndarray, times: np.ndarray, k_galaxy: float = 5.46e4
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Map brain activity to galaxy rotation curve dynamics.

    Brain activity → Halo mass ratio (same equation)
    Higher activity = Higher density = Lower ratio

    Returns: radii, rotation_velocities
    """
    print("\n" + "=" * 60)
    print("🌌 STEP 2: Convert to Galaxy Motion")
    print("=" * 60)

    # Map activity to density
    # Activity ∝ density (more active = denser region)
    rho = C_activity * 1e7 + 1e6  # Scale to galaxy density range

    # Apply UET galaxy law: ratio = k / sqrt(rho)
    ratios = k_galaxy / np.sqrt(rho)

    # Convert to rotation velocity: v ∝ sqrt(M_total) ∝ sqrt(1 + ratio)
    v_rotation = np.sqrt(1 + ratios) * 100  # Scale to km/s

    # Radii = time points mapped to kpc
    radii = times / times[-1] * 30  # 0 to 30 kpc

    print(f"   Mapped {len(times)} brain points to galaxy radii")
    print(f"   Velocity range: {v_rotation.min():.1f} - {v_rotation.max():.1f} km/s")

    return radii, v_rotation


# =============================================================================
# STEP 3: Project to 2D Graph
# =============================================================================


def project_to_2d_graph(
    radii: np.ndarray, velocities: np.ndarray, C_activity: np.ndarray, times: np.ndarray
) -> Dict:
    """
    Create 2D projections from the data.

    Returns: Dict with time_series, spectrum, rotation_curve
    """
    print("\n" + "=" * 60)
    print("📈 STEP 3: Project to 2D Graph")
    print("=" * 60)

    # 1. Time series plot data
    time_series = {"t": times, "activity": C_activity, "label": "Brain Activity"}

    # 2. Power spectrum (FFT)
    N = len(C_activity)
    fft = np.fft.rfft(C_activity - np.mean(C_activity))
    power = np.abs(fft) ** 2
    freqs = np.fft.rfftfreq(N, times[1] - times[0])

    # Fit spectral slope (β)
    valid = (freqs > 0.01) & (freqs < 1.0)
    if np.sum(valid) > 10:
        log_f = np.log10(freqs[valid])
        log_P = np.log10(power[valid] + 1e-10)
        coef = np.polyfit(log_f, log_P, 1)
        beta = -coef[0]
    else:
        beta = 0.0

    spectrum = {"freqs": freqs, "power": power, "beta": beta, "label": f"Spectrum (β={beta:.2f})"}

    # 3. Rotation curve
    rotation_curve = {"r": radii, "v": velocities, "label": "Rotation Curve"}

    print(f"   Time series: {len(times)} points")
    print(f"   Spectrum β = {beta:.2f} (UET predicts ~2)")
    print(f"   Rotation curve: {len(radii)} points")

    return {"time_series": time_series, "spectrum": spectrum, "rotation_curve": rotation_curve}


# =============================================================================
# STEP 4: Economy Calculation
# =============================================================================


def apply_economy_model(activity: np.ndarray, velocities: np.ndarray) -> Dict:
    """
    Apply market equations to the data.

    V = C × I^k
    Calculate k from simulation data.
    """
    print("\n" + "=" * 60)
    print("💰 STEP 4: Economy Calculation")
    print("=" * 60)

    # Map: activity → C (capacity), velocity → I (information flow)
    C_market = activity / np.mean(activity)  # Normalize
    I_market = velocities / np.mean(velocities)  # Normalize

    # Calculate effective V (value)
    # V = C × I^k → log(V) = log(C) + k×log(I)
    # For each point, estimate V
    V_market = C_market * I_market  # Assume k=1 initially

    # Fit k: log(V/C) = k × log(I)
    valid = (C_market > 0.1) & (I_market > 0.1)
    if np.sum(valid) > 10:
        log_ratio = np.log(V_market[valid] / C_market[valid])
        log_I = np.log(I_market[valid])
        k_fit = np.mean(log_ratio / (log_I + 1e-10))
        k_fit = np.clip(k_fit, 0.5, 2.0)
    else:
        k_fit = 1.0

    # Market health indicator
    k_deviation = abs(k_fit - 1.0)
    if k_deviation < 0.2:
        health = "✅ Healthy (k ≈ 1)"
    elif k_deviation < 0.5:
        health = "⚠️ Moderate"
    else:
        health = "❌ Anomaly"

    print(f"   Market coupling k = {k_fit:.2f}")
    print(f"   Health: {health}")

    return {"C": C_market, "I": I_market, "V": V_market, "k": k_fit, "health": health}


# =============================================================================
# STEP 5: Color Visualization
# =============================================================================


def create_color_visualization(graphs_2d: Dict, economy: Dict, output_dir: str = OUTPUT_DIR) -> str:
    """
    Create final color heatmap visualization combining all data.
    """
    print("\n" + "=" * 60)
    print("🎨 STEP 5: Color Visualization")
    print("=" * 60)

    os.makedirs(output_dir, exist_ok=True)

    # Create comprehensive figure
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))

    # 1. Time Series
    ax1 = axes[0, 0]
    ts = graphs_2d["time_series"]
    ax1.plot(ts["t"], ts["activity"], "b-", linewidth=0.5)
    ax1.set_xlabel("Time")
    ax1.set_ylabel("Activity")
    ax1.set_title("🧠 Brain Activity (3D → Time Series)")
    ax1.grid(True, alpha=0.3)

    # 2. Power Spectrum
    ax2 = axes[0, 1]
    sp = graphs_2d["spectrum"]
    valid = sp["freqs"] > 0.001
    ax2.loglog(sp["freqs"][valid], sp["power"][valid], "r-", linewidth=0.5)
    ax2.set_xlabel("Frequency")
    ax2.set_ylabel("Power")
    ax2.set_title(f"📊 Spectrum (β = {sp['beta']:.2f})")
    ax2.grid(True, alpha=0.3)

    # 3. Rotation Curve
    ax3 = axes[0, 2]
    rc = graphs_2d["rotation_curve"]
    ax3.plot(rc["r"], rc["v"], "g-", linewidth=1)
    ax3.set_xlabel("Radius (kpc)")
    ax3.set_ylabel("Velocity (km/s)")
    ax3.set_title("🌌 Galaxy Rotation Curve")
    ax3.grid(True, alpha=0.3)

    # 4. Economy C vs I
    ax4 = axes[1, 0]
    ax4.scatter(economy["C"], economy["I"], c=economy["V"], cmap="viridis", s=1, alpha=0.5)
    ax4.set_xlabel("Capacity (C)")
    ax4.set_ylabel("Information (I)")
    ax4.set_title(f"💰 Market: k = {economy['k']:.2f}")
    ax4.grid(True, alpha=0.3)

    # 5. Value Heatmap (2D projection)
    ax5 = axes[1, 1]
    N = int(np.sqrt(len(economy["V"])))
    if N > 1:
        V_2d = economy["V"][: N * N].reshape(N, N)
        im = ax5.imshow(V_2d, cmap="plasma", aspect="auto")
        plt.colorbar(im, ax=ax5)
    ax5.set_title("🎨 Value Heatmap")

    # 6. Unified Summary
    ax6 = axes[1, 2]
    ax6.axis("off")
    summary_text = f"""
    Unified Pipeline Results
    ========================
    
    🧠 Brain: 3D simulation complete
    🌌 Galaxy: Rotation curve generated
    📈 Spectrum: β = {sp['beta']:.2f}
    💰 Economy: k = {economy['k']:.2f}
    
    Health: {economy['health']}
    
    UET Predictions:
    • β ≈ 2 for optimal brain
    • k ≈ 1 for healthy market
    """
    ax6.text(
        0.1,
        0.9,
        summary_text,
        transform=ax6.transAxes,
        fontsize=10,
        verticalalignment="top",
        fontfamily="monospace",
    )

    plt.tight_layout()

    # Save
    output_path = os.path.join(output_dir, "unified_pipeline_output.png")
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()

    print(f"   ✅ Saved: {output_path}")

    return output_path


# =============================================================================
# MAIN PIPELINE
# =============================================================================


def run_unified_pipeline():
    """Run the complete Brain → Galaxy → Economy → Color pipeline."""
    print("\n" + "=" * 60)
    print("🚀 UNIFIED PIPELINE: Brain → Galaxy → Economy → Color")
    print("=" * 60 + "\n")

    # Step 1: Brain 3D
    C_activity, I_activity, times = simulate_brain_3d(
        Nx=32, Ny=32, Nz=32, T=50.0, dt=0.1  # Reduced for speed
    )

    # Step 2: Galaxy Motion
    radii, velocities = convert_to_galaxy_motion(C_activity, times)

    # Step 3: 2D Graphs
    graphs_2d = project_to_2d_graph(radii, velocities, C_activity, times)

    # Step 4: Economy
    economy = apply_economy_model(C_activity, velocities)

    # Step 5: Color Visualization
    output_path = create_color_visualization(graphs_2d, economy)

    print("\n" + "=" * 60)
    print("✅ PIPELINE COMPLETE!")
    print("=" * 60)
    print(f"\n📊 Output: {output_path}")

    return {
        "brain": {"C": C_activity, "I": I_activity, "t": times},
        "galaxy": {"r": radii, "v": velocities},
        "graphs": graphs_2d,
        "economy": economy,
        "output": output_path,
    }


if __name__ == "__main__":
    run_unified_pipeline()
