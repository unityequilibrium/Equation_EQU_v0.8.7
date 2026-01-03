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



def demonstrate_layered_kinematics():
    """
    Simulation of Phase CVII (MLK): Newtonian vs Gradient Layers.
    Shows how 'Intent' (Information Gradient) overrides 'Habit' (Newtonian Gravity).
    """
    # 1. Setup Environment
    # We have a central mass (Newtonian source) and an awareness peak (Information source)
    mass_center = np.array([0, 0])
    awareness_peak = np.array([5, 5])

    dt = 0.1
    steps = 100

    # Starting position
    pos_newton = np.array([-5.0, 5.0])
    pos_gradient = np.array([-5.0, 5.0])  # Same starting point
    pos_combined = np.array([-5.0, 5.0])

    vel_newton = np.array([1.0, 0.0])  # Orbit-like start
    vel_combined = np.array([1.0, 0.0])

    history_n = [pos_newton.copy()]
    history_g = [pos_gradient.copy()]
    history_c = [pos_combined.copy()]

    for _ in range(steps):
        # A. Newtonian Layer (Gravity prop to 1/r^2)
        r_n = pos_newton - mass_center
        acc_n = -r_n / (np.linalg.norm(r_n) ** 3 + 1e-10)
        vel_newton += acc_n * dt
        pos_newton += vel_newton * dt
        history_n.append(pos_newton.copy())

        # B. Pure Gradient Layer (Direct movement to awareness)
        r_g = awareness_peak - pos_gradient
        vel_grad = (r_g / np.linalg.norm(r_g)) * 0.5  # Constant speed toward peak
        pos_gradient += vel_grad * dt
        history_g.append(pos_gradient.copy())

        # C. Combined Unified Layer (Phase CVII)
        # v_total = v_newton + eta * v_gradient
        r_cn = pos_combined - mass_center
        acc_cn = -r_cn / (np.linalg.norm(r_cn) ** 3 + 1e-10)
        vel_combined += acc_cn * dt

        r_cg = awareness_peak - pos_combined
        v_grad_comp = (r_cg / np.linalg.norm(r_cg)) * 0.4  # Strategic Intent

        pos_combined += (vel_combined + v_grad_comp) * dt
        history_c.append(pos_combined.copy())

    # Plotting
    hn = np.array(history_n)
    hg = np.array(history_g)
    hc = np.array(history_c)

    plt.figure(figsize=(10, 6))
    plt.plot(hn[:, 0], hn[:, 1], "b--", label="Newtonian Layer (Habitual/Gravity)")
    plt.plot(hg[:, 0], hg[:, 1], "g:", label="Gradient Layer (Pure Intent/LLM)")
    plt.plot(hc[:, 0], hc[:, 1], "r-", linewidth=2, label="Unified UET 3.0 (Layered Realism)")

    plt.scatter([0], [0], color="blue", marker="o", label="Mass Center")
    plt.scatter([5], [5], color="green", marker="*", s=200, label="Awareness Peak")

    plt.title("UET Phase CVII: Multi-Layered Kinematics (MLK) Demonstration")
    plt.xlabel("Spatial X")
    plt.ylabel("Spatial Y")
    plt.legend()
    plt.grid(True)

    # Save output
    output_path = "research_uet/lab/03_evolution/mlk_demonstration.png"
    plt.savefig(output_path)
    print(f"✅ MLK Demonstration completed. Result saved to {output_path}")


if __name__ == "__main__":
    demonstrate_layered_kinematics()
