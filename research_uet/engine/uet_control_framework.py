"""
🎯 UET Inverse Control Framework
=================================
Instead of predicting the future, answer:
"If I want outcome X, what parameters/actions are needed?"

This is the TRUE power of UET - CONTROL not prediction!
"""

import numpy as np


class UETController:
    """
    UET-based controller for achieving desired outcomes.

    Uses Cahn-Hilliard dynamics in reverse:
    Given target C_target, find required μ (chemical potential)
    """

    def __init__(self, kappa=0.5, beta=2.0):
        self.kappa = kappa  # Gradient energy (stability)
        self.beta = beta  # Coupling strength

    def compute_required_intervention(self, C_current, C_target, dt=1.0):
        """
        Compute required intervention to move from C_current to C_target.

        From Cahn-Hilliard: dC/dt = ∇²μ
        We want: C_target = C_current + dt * intervention

        Returns:
            dict with required parameters and actions
        """
        # Desired change
        dC = C_target - C_current

        # Required "force" (chemical potential gradient)
        required_mu = dC / dt

        # Decompose into components
        # μ = dV/dC + κ∇²C + βI
        # So required_mu = dV/dC + κ∇²C + βI

        # For single point (no spatial):
        # dV/dC ≈ C(C² - 1) (double-well)
        dV_dC = C_current * (C_current**2 - 1)

        # Required I (information injection) to achieve target
        required_I = (required_mu - dV_dC) / self.beta

        return {
            "current": C_current,
            "target": C_target,
            "required_change": dC,
            "required_mu": required_mu,
            "required_I": required_I,
            "interpretation": self._interpret(dC, required_I),
        }

    def _interpret(self, dC, required_I):
        """Interpret results in plain language."""
        actions = []

        if dC > 0:
            actions.append(f"Need INCREASE of {abs(dC)*100:.1f}%")
        else:
            actions.append(f"Need DECREASE of {abs(dC)*100:.1f}%")

        if required_I > 0:
            actions.append(f"Inject positive information (I = {required_I:.2f})")
            actions.append("Actions: Buy pressure, positive news, capital inflow")
        else:
            actions.append(f"Extract information (I = {required_I:.2f})")
            actions.append("Actions: Sell pressure, negative news, capital outflow")

        return actions

    def plan_trajectory(self, C_start, C_target, n_steps=10):
        """
        Plan a trajectory from C_start to C_target.
        Returns required interventions at each step.
        """
        trajectory = []
        C = C_start

        # Linear interpolation for target trajectory
        C_path = np.linspace(C_start, C_target, n_steps + 1)

        for i in range(n_steps):
            step_target = C_path[i + 1]
            result = self.compute_required_intervention(C, step_target)
            trajectory.append(
                {"step": i + 1, "from": C, "to": step_target, "required_I": result["required_I"]}
            )
            C = step_target

        return trajectory


def run_demo():
    print("=" * 70)
    print("🎯 UET INVERSE CONTROL FRAMEWORK")
    print("=" * 70)
    print()
    print("Question: If I want stock to go from 100 to 110, what do I need?")
    print()

    controller = UETController(kappa=0.5, beta=2.0)

    # Normalize prices (C is normalized capacity)
    C_current = 0.0  # Current = equilibrium
    C_target = 0.1  # Want 10% increase

    result = controller.compute_required_intervention(C_current, C_target)

    print("📊 RESULT:")
    print(f"   Current state (C): {result['current']:.2f}")
    print(f"   Target state (C):  {result['target']:.2f}")
    print(f"   Required change:   {result['required_change']:.2f}")
    print()
    print("🔧 REQUIRED ACTIONS:")
    for action in result["interpretation"]:
        print(f"   • {action}")
    print()

    print("=" * 70)
    print("📈 TRAJECTORY PLANNING (10 steps to reach +10%)")
    print("=" * 70)

    trajectory = controller.plan_trajectory(0.0, 0.1, n_steps=10)

    print(f"\n{'Step':>5} {'From':>10} {'To':>10} {'Required I':>12}")
    print("-" * 40)

    for step in trajectory:
        print(
            f"{step['step']:>5} {step['from']:>10.3f} {step['to']:>10.3f} {step['required_I']:>12.4f}"
        )

    total_I = sum(s["required_I"] for s in trajectory)
    print("-" * 40)
    print(f"{'Total':>5} {'':<10} {'':<10} {total_I:>12.4f}")

    print()
    print("=" * 70)
    print("🎓 INTERPRETATION")
    print("=" * 70)
    print()
    print("To achieve +10% growth over 10 periods:")
    print(f"   • Total information injection needed: I = {total_I:.4f}")
    print(f"   • Average per period: I = {total_I/10:.4f}")
    print()
    print("In practical terms:")
    print("   • Consistent buy pressure each period")
    print("   • Positive information flow (earnings, news)")
    print("   • Capital inflow from external sources")
    print()

    print("=" * 70)
    print("🔄 REVERSE: If stock drops 20%, what happened?")
    print("=" * 70)

    drop_result = controller.compute_required_intervention(0.0, -0.2)
    print()
    print("Analysis of -20% drop:")
    print(f"   Required I = {drop_result['required_I']:.4f}")
    print()
    print("Interpretation:")
    print("   • Large negative information injection")
    print("   • Massive sell pressure")
    print("   • Capital flight / panic selling")
    print("   • Bad news or external shock")

    print()
    print("=" * 70)
    print("✅ UET CONTROL FRAMEWORK COMPLETE")
    print("=" * 70)
    print()
    print("Key insight: UET tells you WHAT TO DO to achieve outcomes,")
    print("not just what will happen. This is actionable intelligence!")


if __name__ == "__main__":
    run_demo()
