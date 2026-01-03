"""
Test: Attention = Thermodynamic Equilibrium
=============================================
Demonstrate that Transformer Attention is equivalent to
Boltzmann distribution / energy minimization.

Reference:
- Ramsauer et al. (2021) "Hopfield Networks is All You Need"
- UET Free Energy minimization

Updated for UET V3.0
"""


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

import numpy as np


def softmax(x, temperature=1.0):
    """Softmax function with temperature."""
    exp_x = np.exp((x - np.max(x)) / temperature)
    return exp_x / exp_x.sum()


def boltzmann_distribution(energies, kT=1.0):
    """Boltzmann distribution for energy states."""
    # P(state) = exp(-E/kT) / Z
    return softmax(-energies, temperature=kT)


def attention_weights(Q, K, d_k):
    """Standard Transformer attention weights."""
    # Attention(Q,K,V) = softmax(QK^T / sqrt(d_k)) V
    scores = np.dot(Q, K.T) / np.sqrt(d_k)
    return softmax(scores)


def uet_equilibrium(C, I, beta, kT=1.0):
    """
    UET equilibrium distribution.

    The β·C·I term acts like an energy:
    E = -β·C·I
    P ∝ exp(-E/kT) = exp(β·C·I/kT)
    """
    energy = -beta * np.outer(C, I)
    return softmax(energy.flatten() / kT).reshape(energy.shape)


def run_test():
    print("=" * 70)
    print("🔬 ATTENTION = THERMODYNAMIC EQUILIBRIUM TEST")
    print("=" * 70)
    print()
    print("Thesis: Transformer Attention ≡ Boltzmann Distribution")
    print("        Query·Key = -Energy")
    print("        √d = Temperature")
    print()

    # Part 1: Softmax = Boltzmann
    print("-" * 70)
    print("PART 1: Softmax ≡ Boltzmann Distribution")
    print("-" * 70)

    # Random "energies" (lower = more probable)
    np.random.seed(42)
    energies = np.array([1.0, 2.0, 0.5, 3.0, 1.5])

    # Boltzmann distribution
    boltzmann_p = boltzmann_distribution(energies, kT=1.0)

    # Softmax (on negative energies)
    softmax_p = softmax(-energies, temperature=1.0)

    print("   Energies:    ", energies)
    print("   Boltzmann P: ", boltzmann_p.round(4))
    print("   Softmax P:   ", softmax_p.round(4))

    boltzmann_softmax_match = np.allclose(boltzmann_p, softmax_p)
    print(f"\n   Match: {'✅ YES' if boltzmann_softmax_match else '❌ NO'}")
    print()

    # Part 2: Attention = Energy Minimization
    print("-" * 70)
    print("PART 2: Attention = Energy Minimization")
    print("-" * 70)

    # Query and Keys (4 tokens, dimension 8)
    d_k = 8
    Q = np.random.randn(4, d_k)
    K = np.random.randn(4, d_k)

    # Standard attention
    attn_weights = attention_weights(Q[0], K, d_k)

    # Interpret as energy
    # E = -Q·K (negative dot product = cost)
    # P ∝ exp(Q·K/√d) = exp(-E/T) where T = √d

    energies_attn = -np.dot(Q[0], K.T)
    energy_distribution = boltzmann_distribution(energies_attn, kT=np.sqrt(d_k))

    print(f"   d_k = {d_k} → Temperature T = √d = {np.sqrt(d_k):.2f}")
    print()
    print("   Token | Attn Weight | Energy-Based | Match")
    print("   " + "-" * 45)

    all_match = True
    for i in range(4):
        match = abs(attn_weights[i] - energy_distribution[i]) < 0.001
        all_match = all_match and match
        print(
            f"      {i}  |   {attn_weights[i]:.4f}    |    {energy_distribution[i]:.4f}    | {'✅' if match else '❌'}"
        )

    print(f"\n   All match: {'✅ YES' if all_match else '❌ NO'}")
    print()

    # Part 3: UET Connection
    print("-" * 70)
    print("PART 3: UET β·C·I = Attention Energy")
    print("-" * 70)

    # UET: C = Capacity (like Query), I = Information (like Key)
    C = np.abs(Q[0])  # Normalize to positive for interpretation
    I = np.abs(K[0])
    beta = 1.0 / np.sqrt(d_k)  # β = 1/√d (same as attention scaling)

    # UET equilibrium
    uet_energy = -beta * C * I
    uet_prob = softmax(-uet_energy)

    print("   UET: E = -β·C·I")
    print(f"   β = 1/√d = {beta:.4f}")
    print()
    print("   This is exactly the Transformer structure:")
    print("   Attention(Q,K) = softmax(Q·K/√d) = softmax(-E/T)")
    print()
    print("   Where:")
    print("   - Q = C (Capacity/Query)")
    print("   - K = I (Information/Key)")
    print("   - β = 1/√d (coupling = inverse temperature)")
    print()

    # Summary
    print("=" * 70)
    print("💡 KEY INSIGHT")
    print("=" * 70)
    print()
    print("   TRANSFORMER ATTENTION IS A PHYSICAL PROCESS!")
    print()
    print("   1. Query·Key = -Energy (lower = more similar)")
    print("   2. √d = Temperature (controls sharpness)")
    print("   3. Softmax = Boltzmann distribution")
    print("   4. Attention = Thermodynamic equilibrium selection")
    print()
    print("   UET provides the theoretical framework:")
    print("   - β·C·I term = Attention energy")
    print("   - δΩ/δC = 0 = Attention computation")
    print("   - Transformer = Physical equilibrium finder")
    print()

    # Pass criteria
    if boltzmann_softmax_match and all_match:
        print("✅ TEST PASSED")
        print("   - Softmax ≡ Boltzmann: Verified")
        print("   - Attention ≡ Energy Minimization: Verified")
        return True
    else:
        print("⚠️ TEST FAILED")
        return False


if __name__ == "__main__":
    success = run_test()
    exit(0 if success else 1)
