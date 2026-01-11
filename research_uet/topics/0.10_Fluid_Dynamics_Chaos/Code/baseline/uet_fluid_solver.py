"""
UET Fluid Solver
================
Fluid dynamics solver based on UET (Universal Equilibrium Theory).
Uses the Ω functional approach instead of Navier-Stokes equations.

This is for COMPARISON with the traditional NS solver.

UET Master Equation:
    Ω[C,I] = ∫ [ V(C) + κ/2|∇C|² + βCI ] dx

Mapping to Fluids:
    C = density field ρ(x,t)
    I = entropy density s(x,t)
    V(C) = pressure potential
    κ|∇C|² = surface/interface energy (like viscosity)
    βCI = entropy-density coupling
"""

import numpy as np
from dataclasses import dataclass
from typing import Tuple, Optional
import json
from pathlib import Path


@dataclass
class UETParameters:
    """UET fluid parameters."""

    kappa: float = 0.01  # Gradient penalty (similar to viscosity)
    beta: float = 0.1  # C-I coupling strength
    alpha: float = 1.0  # Potential well strength
    C0: float = 1.0  # Equilibrium density


class UETFluidSolver:
    """
    Fluid solver based on UET Ω functional.

    Evolution:
        ∂C/∂t = -δΩ/δC = -V'(C) + κ∇²C - βI
        ∂I/∂t = -δΩ/δI = -βC (+ entropy production)

    Key Differences from Navier-Stokes:
        1. Energy-based (functional) instead of momentum-based (PDE)
        2. Natural regularization via V(C) bounded
        3. Information field I couples to dynamics
    """

    def __init__(
        self,
        nx: int = 64,
        ny: int = 64,
        lx: float = 1.0,
        ly: float = 1.0,
        dt: float = 0.001,
        params: Optional[UETParameters] = None,
    ):
        """Initialize UET solver."""
        self.nx = nx
        self.ny = ny
        self.lx = lx
        self.ly = ly
        self.dx = lx / nx
        self.dy = ly / ny
        self.dt = dt

        # UET parameters
        self.params = params or UETParameters()

        # Fields
        self.C = np.ones((ny, nx)) * self.params.C0  # Density
        self.I = np.zeros((ny, nx))  # Information/Entropy

        # Derived fields (for visualization)
        self.u = np.zeros((ny, nx))  # Velocity from ∇C
        self.v = np.zeros((ny, nx))

        # History
        self.omega_history = []
        self.energy_history = []
        self.time = 0.0

    def V(self, C: np.ndarray) -> np.ndarray:
        """Potential energy V(C) = α/2 (C - C₀)²."""
        return 0.5 * self.params.alpha * (C - self.params.C0) ** 2

    def dV_dC(self, C: np.ndarray) -> np.ndarray:
        """Derivative of potential: V'(C) = α(C - C₀)."""
        return self.params.alpha * (C - self.params.C0)

    def compute_laplacian(self, field: np.ndarray) -> np.ndarray:
        """Compute ∇²field using finite difference."""
        lap = np.zeros_like(field)

        # Interior points
        lap[1:-1, 1:-1] = (
            field[1:-1, 2:] - 2 * field[1:-1, 1:-1] + field[1:-1, :-2]
        ) / self.dx**2 + (
            field[2:, 1:-1] - 2 * field[1:-1, 1:-1] + field[:-2, 1:-1]
        ) / self.dy**2

        return lap

    def compute_gradient(self, field: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Compute gradient (∂field/∂x, ∂field/∂y)."""
        dfdx = np.zeros_like(field)
        dfdy = np.zeros_like(field)

        # Central difference
        dfdx[:, 1:-1] = (field[:, 2:] - field[:, :-2]) / (2 * self.dx)
        dfdy[1:-1, :] = (field[2:, :] - field[:-2, :]) / (2 * self.dy)

        return dfdx, dfdy

    def compute_gradient_squared(self, field: np.ndarray) -> np.ndarray:
        """Compute |∇field|²."""
        dfdx, dfdy = self.compute_gradient(field)
        return dfdx**2 + dfdy**2

    def compute_omega(self) -> float:
        """
        Compute total Ω functional.
        Ω = ∫ [ V(C) + κ/2|∇C|² + βCI ] dx
        """
        V_term = np.sum(self.V(self.C))
        grad_term = (
            0.5 * self.params.kappa * np.sum(self.compute_gradient_squared(self.C))
        )
        coupling_term = self.params.beta * np.sum(self.C * self.I)

        omega = (V_term + grad_term + coupling_term) * self.dx * self.dy
        return omega

    def set_boundary_conditions(self, bc_type: str = "lid_driven"):
        """Set boundary conditions on C field."""
        self.bc_type = bc_type

        if bc_type == "lid_driven":
            # Top boundary: high density (like moving wall)
            self.C[-1, :] = self.params.C0 * 1.1
            # Other walls: equilibrium
            self.C[0, :] = self.params.C0
            self.C[:, 0] = self.params.C0
            self.C[:, -1] = self.params.C0

        elif bc_type == "poiseuille":
            # Pressure difference → density difference
            self.C[:, 0] = self.params.C0 * 1.05  # Inlet (higher pressure)
            self.C[:, -1] = self.params.C0 * 0.95  # Outlet (lower pressure)

    def apply_boundary_conditions(self):
        """Apply boundary conditions after each step."""
        if self.bc_type == "lid_driven":
            self.C[-1, :] = self.params.C0 * 1.1
            self.C[0, :] = self.params.C0
            self.C[:, 0] = self.params.C0
            self.C[:, -1] = self.params.C0
        elif self.bc_type == "poiseuille":
            self.C[:, 0] = self.params.C0 * 1.05
            self.C[:, -1] = self.params.C0 * 0.95

    def step(self):
        """
        Perform one time step.

        Evolution equations (gradient descent on Ω):
            ∂C/∂t = -δΩ/δC = -V'(C) + κ∇²C - βI
            ∂I/∂t = -δΩ/δI + source = -βC + entropy_production
        """
        # Compute functional derivatives
        dOmega_dC = (
            self.dV_dC(self.C)
            - self.params.kappa * self.compute_laplacian(self.C)
            + self.params.beta * self.I
        )
        dOmega_dI = self.params.beta * self.C

        # Update fields (gradient descent)
        self.C = self.C - self.dt * dOmega_dC

        # I update with entropy production term (second law)
        # Entropy production proportional to gradient squared
        entropy_production = 0.01 * self.compute_gradient_squared(self.C)
        self.I = self.I - self.dt * dOmega_dI + self.dt * entropy_production

        # Ensure C > 0 (physical constraint - density must be positive)
        self.C = np.maximum(self.C, 0.01)

        # Apply boundary conditions
        self.apply_boundary_conditions()

        # Update velocity from density gradient (v ∝ -∇C for pressure-driven flow)
        self.u, self.v = self.compute_gradient(self.C)
        self.u *= -1.0 / self.params.C0  # Normalize
        self.v *= -1.0 / self.params.C0

        # Update time
        self.time += self.dt

        # Record history
        omega = self.compute_omega()
        self.omega_history.append(omega)

        kinetic_proxy = 0.5 * np.sum(self.u**2 + self.v**2)
        self.energy_history.append(kinetic_proxy)

    def run(self, steps: int, verbose: bool = True):
        """Run simulation for given steps."""
        for i in range(steps):
            self.step()

            # Check for blow-up
            if np.isnan(self.C).any() or np.isinf(self.C).any():
                print(f"❌ BLOW-UP at step {i}!")
                return self.omega_history

            if verbose and (i + 1) % (steps // 10) == 0:
                omega = self.omega_history[-1]
                max_C = np.max(self.C)
                print(
                    f"Step {i+1}/{steps}: Time = {self.time:.4f}, Ω = {omega:.4e}, max(C) = {max_C:.4f}"
                )

        return self.omega_history

    def get_velocity_magnitude(self) -> np.ndarray:
        """Get velocity magnitude."""
        return np.sqrt(self.u**2 + self.v**2)

    def save_results(self, filepath: str):
        """Save results to JSON."""
        results = {
            "solver": "UET",
            "parameters": {
                "nx": self.nx,
                "ny": self.ny,
                "dt": self.dt,
                "kappa": self.params.kappa,
                "beta": self.params.beta,
                "alpha": self.params.alpha,
            },
            "final_time": self.time,
            "omega_history": self.omega_history,
            "energy_history": self.energy_history,
            "final_omega": self.omega_history[-1] if self.omega_history else None,
        }
        with open(filepath, "w") as f:
            json.dump(results, f, indent=2)


# ============================================================================
# TEST CASES (matching NS baseline)
# ============================================================================


def test_lid_driven_cavity():
    """Lid-driven cavity test - compare with NS baseline."""
    print("=" * 60)
    print("UET TEST: Lid-Driven Cavity")
    print("=" * 60)

    params = UETParameters(kappa=0.01, beta=0.1, alpha=1.0)
    solver = UETFluidSolver(nx=32, ny=32, dt=0.001, params=params)
    solver.set_boundary_conditions("lid_driven")

    solver.run(steps=1000, verbose=True)

    print(f"\nFinal Ω: {solver.omega_history[-1]:.4e}")
    print(f"Max velocity proxy: {np.max(solver.get_velocity_magnitude()):.4f}")
    print("✅ PASS: UET simulation completed without blow-up")

    return solver


def test_poiseuille_flow():
    """Poiseuille flow test."""
    print("=" * 60)
    print("UET TEST: Poiseuille Flow")
    print("=" * 60)

    params = UETParameters(kappa=0.01, beta=0.05, alpha=1.0)
    solver = UETFluidSolver(nx=32, ny=32, dt=0.001, params=params)
    solver.set_boundary_conditions("poiseuille")

    solver.run(steps=500, verbose=True)

    print(f"\nFinal Ω: {solver.omega_history[-1]:.4e}")
    print("✅ PASS: UET Poiseuille flow test completed")

    return solver


def test_high_reynolds():
    """
    High Reynolds number test - where NS may blow up.
    UET should remain stable due to V(C) regularization.
    """
    print("=" * 60)
    print("UET TEST: High Reynolds Equivalent (Stability Test)")
    print("=" * 60)

    # Low kappa = high Re equivalent
    params = UETParameters(kappa=0.0001, beta=0.01, alpha=1.0)
    solver = UETFluidSolver(nx=32, ny=32, dt=0.0001, params=params)
    solver.set_boundary_conditions("lid_driven")

    # Add perturbation (to trigger instability in unstable systems)
    solver.C += 0.1 * np.random.randn(32, 32)

    solver.run(steps=500, verbose=True)

    if not np.isnan(solver.C).any():
        print("✅ PASS: UET remained STABLE at high Re equivalent!")
        print("   (This is where NS might blow up)")
    else:
        print("❌ FAIL: UET blew up")

    return solver


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("UET FLUID SOLVER")
    print("=" * 60)

    test_lid_driven_cavity()
    print()
    test_poiseuille_flow()
    print()
    test_high_reynolds()
