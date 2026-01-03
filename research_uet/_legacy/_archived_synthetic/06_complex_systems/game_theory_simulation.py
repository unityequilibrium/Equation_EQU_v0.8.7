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



class UETGameAgent:
    def __init__(self, id, initial_pot, initial_kin):
        self.id = id
        self.pot = initial_pot  # Potential Energy (Wealth/Stability)
        self.kin = initial_kin  # Kinetic Energy (Cost/Risk)
        self.strategy = np.random.rand()  # 0 = Defect (High Kin), 1 = Cooperate (High Pot)
        self.history = []

    def decide(self, neighbors):
        """
        Decide strategy based on neighbor states (Payoff Equation).
        Goal: Maximize Potential, Minimize Kinetic Loss.
        """
        if not neighbors:
            return

        # Calculate average neighbor stability
        avg_pot = np.mean([n.pot for n in neighbors])

        # Payoff Function (Simplified UET Game Equation)
        # Payoff = Gain in Potential - Dissipation of Kinetic
        # If neighbors are stable (high pot), cooperation yields high return.

        cooperation_bonus = 0.1 * avg_pot * self.strategy
        dissipation_cost = 0.05 * self.kin

        net_gain = cooperation_bonus - dissipation_cost

        # Adaptation (Learning)
        if net_gain > 0:
            # Successful strategy: Reinforce cooperation, Convert Kin to Pot
            self.pot += net_gain
            self.kin -= dissipation_cost
            self.strategy = min(1.0, self.strategy + 0.01)
        else:
            # Failed strategy: Panic, increase Kinetic (chaos), decrease stability
            self.pot += net_gain  # net_gain is negative here
            self.kin += 0.02  # Panic energy
            self.strategy = max(0.0, self.strategy - 0.02)

        # Physical Limits
        self.pot = max(0.0, self.pot)
        self.kin = max(0.0, self.kin)

        self.history.append(self.pot)


class UETUniverseGame:
    def __init__(self, n_agents=50, steps=100):
        self.agents = [UETGameAgent(i, 10.0, 5.0) for i in range(n_agents)]
        self.steps = steps
        self.global_omega = []  # Vacuum Pressure (Instability Metric)

    def run(self):
        print(f"Starting UET Game Simulation with {len(self.agents)} agents...")

        for t in range(self.steps):
            total_instability = 0

            for i, agent in enumerate(self.agents):
                # Define neighbors (simple ring topology for demo)
                left = self.agents[(i - 1) % len(self.agents)]
                right = self.agents[(i + 1) % len(self.agents)]
                neighbors = [left, right]

                agent.decide(neighbors)

                # UET Omega ~ Ratio of Kinetic Chaos to Potential Stability
                # If Pot is 0, instability is infinite (avoid div by zero)
                if agent.pot > 0:
                    total_instability += agent.kin / agent.pot
                else:
                    total_instability += 100.0

            avg_omega = total_instability / len(self.agents)
            self.global_omega.append(avg_omega)

        print("Simulation Complete.")

    def plot_results(self, output_path="uet_game_results.png"):
        plt.figure(figsize=(10, 6))

        # Plot Global Instability (Omega)
        plt.subplot(2, 1, 1)
        plt.plot(self.global_omega, label="Global Vacuum Pressure ($\Omega$)")
        plt.title("UET Game Theory: Convergence to Equilibrium")
        plt.ylabel("Instability ($\Omega$)")
        plt.grid(True)
        plt.legend()

        # Plot Agent Potentials
        plt.subplot(2, 1, 2)
        for i in range(min(5, len(self.agents))):  # Plot first 5 agents
            plt.plot(self.agents[i].history, alpha=0.7, label=f"Agent {i}")
        plt.title("Agent Potential Energy Over Time")
        plt.xlabel("Time Step")
        plt.ylabel("Potential Energy")
        plt.legend()

        plt.tight_layout()
        plt.savefig(output_path)
        print(f"Results saved to {output_path}")


if __name__ == "__main__":
    sim = UETUniverseGame(n_agents=100, steps=200)
    sim.run()
    # Save to current directory or specific output
    sim.plot_results(os.path.join(os.path.dirname(__file__), "game_theory_convergence.png"))
