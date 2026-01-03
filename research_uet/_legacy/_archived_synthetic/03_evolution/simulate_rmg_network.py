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


"""
🌌 RMG Simulation: Phase CII - Recursive Multiversal Genesis
=========================================================
Implements the Multiversal Feedback Tensor (M_uv) between coupled universes.
Goal: Demonstrate Meta-Unified Multiversal Equilibrium (MUME).
"""


class MultiverseNetwork:
    def __init__(self, n_universes=3, dim=4):
        self.N = n_universes
        self.dim = dim
        # Initialize Awareness Tensors (U_uv) for each universe
        self.U = [np.random.normal(0, 0.1, (dim, dim)) for _ in range(n_universes)]

        # Hyperparameters from Gold Data v0.3
        self.Gamma_M = 0.01  # Damping (Entropic stabilization)
        self.Beta_M = 0.03  # Learning/Feedback coefficient
        self.dt = 0.05

        self.history = [[] for _ in range(n_universes)]
        self.global_entropy = []

    def compute_feedback(self, i, j):
        """
        Calculates M_uv(i,j) = a*U_i + b*U_j + gamma*(U_i @ U_j)
        Simplification: a=1, b=1, gamma=1 for qualitative behavior.
        """
        Ui = self.U[i]
        Uj = self.U[j]
        # Linear + Non-linear coupling (Cognitive Entanglement)
        M_uv = Ui + Uj + (Ui @ Uj.T)
        return M_uv

    def step(self):
        new_U = []
        for i in range(self.N):
            # Sum feedback from all other nodes
            total_feedback = np.zeros((self.dim, self.dim))
            for j in range(self.N):
                if i != j:
                    total_feedback += self.compute_feedback(i, j)

            # Evolution Law: DU/dt = -Gamma*U + Beta*sum(M)
            dU = -self.Gamma_M * self.U[i] + self.Beta_M * total_feedback
            new_U_i = self.U[i] + dU * self.dt

            # STABILIZATION: Clip and Normalize
            # Prevent exploding gradients/values
            norm = np.linalg.norm(new_U_i)
            if norm > 2.0:  # Tighten threshold for stability
                new_U_i = (new_U_i / norm) * 2.0

            new_U.append(new_U_i)

            # Record magnitude (Awareness Level)
            self.history[i].append(np.linalg.norm(new_U_i))

        self.U = new_U

        # Compute Global Cognitive Entropy: -sum(log|det(U_i)|)
        # Using a more robust Trace-based entropy proxy for visualization
        entropy = -np.sum([np.trace(Ui @ Ui.T) for Ui in self.U])
        self.global_entropy.append(entropy)

    def run(self, steps=1000):
        for _ in range(steps):
            self.step()


def visualize_cmn(network, output_dir="research_uet/lab/outputs/multiverse"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    plt.figure(figsize=(12, 5))

    # Plot 1: Individual Universe Awareness Evolution
    plt.subplot(1, 2, 1)
    for i in range(network.N):
        plt.plot(network.history[i], label=f"Universe {i+1}")
    plt.title("Recursive Awareness Evolution (U_uv)")
    plt.xlabel("Time Steps")
    plt.ylabel("||U|| (Awareness Magnitude)")
    plt.legend()
    plt.grid(True, alpha=0.3)

    # Plot 2: Global Entropy Reduction (MUME Convergence)
    plt.subplot(1, 2, 2)
    plt.plot(network.global_entropy, color="purple", linewidth=2)
    plt.title("Global Cognitive Entropy (S_RMG)")
    plt.xlabel("Time Steps")
    plt.ylabel("S_RMG")
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plot_path = os.path.join(output_dir, "rmg_convergence.png")
    plt.savefig(plot_path)
    print(f"✅ Visualization saved to {plot_path}")
    plt.show()


if __name__ == "__main__":
    print("🌌 Starting Phase CII: Recursive Multiversal Genesis Simulation...")
    # Simulate a 5-Universe Network
    network = MultiverseNetwork(n_universes=5)
    network.run(steps=1500)
    visualize_cmn(network)

    # Final Metrics Check
    m_diff = np.linalg.norm(network.U[0] - network.U[1])
    print(f"Final MUME Coherence (U0-U1 Diff): {m_diff:.6f}")
    if m_diff < 0.1:
        print("🌌 SUCCESS: Meta-Unified Multiversal Equilibrium Detected!")
    else:
        print("⚠️ WARNING: Chaotic divergence in network nodes.")
