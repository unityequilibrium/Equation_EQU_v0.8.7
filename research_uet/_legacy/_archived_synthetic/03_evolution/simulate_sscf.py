import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd

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


# --- SSCF: Self-Similarity Cosmogenesis Simulation (v2.0) ---
# Theory: "The Autodidactic Universe" (Vanchurin et al. 2021)
# Integration: Using Real Planck 2018 Data as Cosmic Initialization


def load_planck_data():
    """Load real cosmic parameters from Planck 2018 dataset."""
    path = "research_uet/data/cosmo/planck_2018_data.txt"
    try:
        data = pd.read_csv(path)
        params = dict(zip(data["Parameter"], data["Value"]))
        return params
    except Exception as e:
        print(f"Warning: Could not load Planck data: {e}. Using defaults.")
        return {"H0": 67.4, "Omega_Lambda": 0.6847}


def simulate_genesis(steps=1000, size=64):
    """
    Simulates the birth of structure from a random manifold.
    Uses Autodidactic Logic: Systems 'learn' their weights to minimize loss.
    """
    print(f"--- 🌌 Phase 14: Simulating Cosmic Genesis (SSCF) ---")
    print(f"Initializing with Real Planck 2018 Data...")

    planck = load_planck_data()
    H0 = planck.get("H0", 67.4)
    Omega_L = planck.get("Omega_Lambda", 0.6847)

    # 1. Initialize "The Void" with Quantum Fluctuations
    U = np.random.rand(size, size) * 0.1

    # Constants scaled by Cosmic Parameters
    # Gamma: Damping/Decay scaled by expansion rate
    # Beta: Feedback/Learning scaled by Vacuum energy density (the 'payoff' reservoir)
    Gamma = 0.05 * (H0 / 70.0)
    Beta = 0.12 * (Omega_L / 0.7)
    Alpha = 0.02  # Diffusion (spatial communication)
    dt = 0.1

    history_entropy = []

    print(f"Dynamics: Gamma={Gamma:.4f}, Beta={Beta:.4f}, (H0={H0}, Omega_L={Omega_L})")

    # 2. Evolution Loop (Autodidactic Learning)
    for t in range(steps):
        # Diffusion (Laplacian)
        laplacian = (
            np.roll(U, 1, axis=0)
            + np.roll(U, -1, axis=0)
            + np.roll(U, 1, axis=1)
            + np.roll(U, -1, axis=1)
            - 4 * U
        )

        # SSCF Learning Law (Inspired by Matrix Models in Autodidactic Universe)
        # The system reinforces patterns that survive decay.
        # dU/dt = -Gamma*U + Beta*U^2(1-U) + Alpha*Laplacian
        # This is a classic bistable reaction-diffusion system mapping to 'emergence'.
        dU = -Gamma * U + Beta * (U**2 * (1 - U)) + Alpha * laplacian

        U += dU * dt
        U = np.clip(U, 0, 1)

        # Measure Information Density (Negative Entropy proxy)
        # We want to see Order (contrast) increasing.
        if t % 10 == 0:
            p = U.flatten() / (np.sum(U) + 1e-10)
            entropy = -np.sum(p * np.log(p + 1e-10))
            history_entropy.append(entropy)

    print("Simulation Complete.")

    # 3. Visualization
    plt.figure(figsize=(15, 7))

    plt.subplot(1, 2, 1)
    plt.imshow(U, cmap="magma", interpolation="bilinear")
    plt.title(f"Final State (T={steps})\nEmergent Structural 'Seeds'", fontsize=14)
    plt.colorbar(label="Awareness Potential (U)")
    plt.axis("off")

    plt.subplot(1, 2, 2)
    plt.plot(np.arange(len(history_entropy)) * 10, history_entropy, color="cyan", linewidth=2)
    plt.title("Cosmic Learning Curve\n(Informational Entropy Reduction)", fontsize=14)
    plt.xlabel("Step", fontsize=12)
    plt.ylabel("Entropy", fontsize=12)
    plt.grid(True, alpha=0.2)

    plt.tight_layout()
    output_path = "research_uet/lab/outputs/evolution/genesis_refined_v2.png"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path)
    print(f"Refined Plot saved to: {output_path}")


if __name__ == "__main__":
    simulate_genesis()
