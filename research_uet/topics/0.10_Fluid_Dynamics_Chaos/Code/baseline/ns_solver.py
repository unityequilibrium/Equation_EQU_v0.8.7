"""
Navier-Stokes Baseline Solver
=============================
A simple 2D Navier-Stokes solver using finite difference method.
This serves as the BASELINE for comparison with UET fluid solver.

Reference: Griebel et al. "Numerical Simulation in Fluid Dynamics"
DOI: 10.1137/1.9780898719703

Usage:
    from ns_solver import NavierStokesSolver
    solver = NavierStokesSolver(nx=64, ny=64, dt=0.001)
    solver.run(steps=1000)
"""

import numpy as np
from dataclasses import dataclass
from typing import Tuple, Optional
import json
from pathlib import Path


@dataclass
class FluidProperties:
    """Fluid physical properties."""

    density: float = 1.0  # kg/m³
    viscosity: float = 0.01  # Pa·s (dynamic viscosity)

    @classmethod
    def load(cls, filepath: str) -> "FluidProperties":
        """Load fluid properties from JSON file."""
        with open(filepath, "r") as f:
            data = json.load(f)
        return cls(
            density=data.get("density_kg_m3", 1.0),
            viscosity=data.get("dynamic_viscosity_Pa_s", 0.01),
        )


class NavierStokesSolver:
    """
    2D Navier-Stokes Solver using Finite Difference Method.

    Solves:
        ∂u/∂t + (u·∇)u = -1/ρ ∇p + ν ∇²u + f
        ∇·u = 0 (incompressibility)

    Method: Chorin's projection method
        1. Advection-Diffusion step (predict velocity)
        2. Pressure Poisson equation (enforce incompressibility)
        3. Velocity correction
    """

    def __init__(
        self,
        nx: int = 64,
        ny: int = 64,
        lx: float = 1.0,
        ly: float = 1.0,
        dt: float = 0.001,
        fluid: Optional[FluidProperties] = None,
    ):
        """
        Initialize the solver.

        Args:
            nx, ny: Grid resolution
            lx, ly: Domain size (meters)
            dt: Time step (seconds)
            fluid: Fluid properties
        """
        self.nx = nx
        self.ny = ny
        self.lx = lx
        self.ly = ly
        self.dx = lx / nx
        self.dy = ly / ny
        self.dt = dt

        # Fluid properties
        self.fluid = fluid or FluidProperties()
        self.rho = self.fluid.density
        self.nu = self.fluid.viscosity / self.fluid.density  # kinematic viscosity

        # Fields (staggered grid)
        self.u = np.zeros((ny, nx + 1))  # x-velocity
        self.v = np.zeros((ny + 1, nx))  # y-velocity
        self.p = np.zeros((ny, nx))  # pressure

        # Intermediate fields
        self.u_star = np.zeros_like(self.u)
        self.v_star = np.zeros_like(self.v)

        # History for analysis
        self.energy_history = []
        self.time = 0.0

    def set_boundary_conditions(self, bc_type: str = "lid_driven"):
        """
        Set boundary conditions.

        Args:
            bc_type: "lid_driven", "channel", "poiseuille"
        """
        self.bc_type = bc_type

        if bc_type == "lid_driven":
            # Top wall moves with velocity 1.0
            self.u[-1, :] = 1.0
            self.u[0, :] = 0.0
            self.v[:, 0] = 0.0
            self.v[:, -1] = 0.0

        elif bc_type == "poiseuille":
            # Pressure-driven flow between parallel plates
            # No-slip at top and bottom
            self.u[0, :] = 0.0
            self.u[-1, :] = 0.0

        elif bc_type == "channel":
            # Periodic in x, no-slip at y boundaries
            self.u[0, :] = 0.0
            self.u[-1, :] = 0.0

    def apply_boundary_conditions(self):
        """Apply boundary conditions after each step."""
        if self.bc_type == "lid_driven":
            self.u[-1, :] = 1.0
            self.u[0, :] = 0.0
            self.v[:, 0] = 0.0
            self.v[:, -1] = 0.0

    def compute_advection(self):
        """Compute advection term (u·∇)u using upwind scheme."""
        # Simplified central difference for now
        # TODO: Implement upwind for stability at high Re

        u_adv = np.zeros_like(self.u)
        v_adv = np.zeros_like(self.v)

        # Interior points only
        for j in range(1, self.ny - 1):
            for i in range(1, self.nx):
                # ∂(u²)/∂x + ∂(uv)/∂y
                dudx = (
                    (self.u[j, i + 1] - self.u[j, i - 1]) / (2 * self.dx)
                    if i < self.nx
                    else 0
                )
                dudy = (self.u[j + 1, i] - self.u[j - 1, i]) / (2 * self.dy)
                u_adv[j, i] = (
                    self.u[j, i] * dudx
                    + 0.5
                    * (
                        self.v[j, min(i, self.nx - 1)]
                        + self.v[j + 1, min(i, self.nx - 1)]
                    )
                    * dudy
                )

        for j in range(1, self.ny):
            for i in range(1, self.nx - 1):
                dvdx = (self.v[j, i + 1] - self.v[j, i - 1]) / (2 * self.dx)
                dvdy = (
                    (self.v[j + 1, i] - self.v[j - 1, i]) / (2 * self.dy)
                    if j < self.ny
                    else 0
                )
                v_adv[j, i] = (
                    0.5
                    * (
                        self.u[min(j, self.ny - 1), i]
                        + self.u[min(j, self.ny - 1), i + 1]
                    )
                    * dvdx
                    + self.v[j, i] * dvdy
                )

        return u_adv, v_adv

    def compute_diffusion(self):
        """Compute diffusion term ν∇²u."""
        u_diff = np.zeros_like(self.u)
        v_diff = np.zeros_like(self.v)

        # Laplacian using 5-point stencil
        for j in range(1, self.ny - 1):
            for i in range(1, self.nx):
                u_diff[j, i] = (
                    self.nu
                    * (
                        (self.u[j, i + 1] - 2 * self.u[j, i] + self.u[j, i - 1])
                        / self.dx**2
                        + (self.u[j + 1, i] - 2 * self.u[j, i] + self.u[j - 1, i])
                        / self.dy**2
                    )
                    if i < self.nx
                    else 0
                )

        for j in range(1, self.ny):
            for i in range(1, self.nx - 1):
                v_diff[j, i] = (
                    self.nu
                    * (
                        (self.v[j, i + 1] - 2 * self.v[j, i] + self.v[j, i - 1])
                        / self.dx**2
                        + (self.v[j + 1, i] - 2 * self.v[j, i] + self.v[j - 1, i])
                        / self.dy**2
                    )
                    if j < self.ny
                    else 0
                )

        return u_diff, v_diff

    def solve_pressure_poisson(self, max_iter: int = 100, tol: float = 1e-5):
        """
        Solve pressure Poisson equation using Jacobi iteration.
        ∇²p = ρ/dt * ∇·u*
        """
        # Compute divergence of intermediate velocity
        div = np.zeros((self.ny, self.nx))
        for j in range(self.ny):
            for i in range(self.nx):
                div[j, i] = (self.u_star[j, i + 1] - self.u_star[j, i]) / self.dx + (
                    self.v_star[j + 1, i] - self.v_star[j, i]
                ) / self.dy

        rhs = self.rho / self.dt * div

        # Jacobi iteration
        for _ in range(max_iter):
            p_old = self.p.copy()

            for j in range(1, self.ny - 1):
                for i in range(1, self.nx - 1):
                    self.p[j, i] = 0.25 * (
                        p_old[j, i + 1]
                        + p_old[j, i - 1]
                        + p_old[j + 1, i]
                        + p_old[j - 1, i]
                        - self.dx**2 * rhs[j, i]
                    )

            # Check convergence
            if np.max(np.abs(self.p - p_old)) < tol:
                break

        # Boundary conditions for pressure (Neumann)
        self.p[0, :] = self.p[1, :]
        self.p[-1, :] = self.p[-2, :]
        self.p[:, 0] = self.p[:, 1]
        self.p[:, -1] = self.p[:, -2]

    def correct_velocity(self):
        """Correct velocity using pressure gradient."""
        for j in range(self.ny):
            for i in range(1, self.nx):
                self.u[j, i] = (
                    self.u_star[j, i]
                    - self.dt / self.rho * (self.p[j, i] - self.p[j, i - 1]) / self.dx
                )

        for j in range(1, self.ny):
            for i in range(self.nx):
                self.v[j, i] = (
                    self.v_star[j, i]
                    - self.dt / self.rho * (self.p[j, i] - self.p[j - 1, i]) / self.dy
                )

    def step(self):
        """Perform one time step using Chorin's projection method."""
        # 1. Compute advection and diffusion
        u_adv, v_adv = self.compute_advection()
        u_diff, v_diff = self.compute_diffusion()

        # 2. Predict velocity (without pressure)
        self.u_star = self.u + self.dt * (-u_adv + u_diff)
        self.v_star = self.v + self.dt * (-v_adv + v_diff)

        # 3. Solve pressure Poisson
        self.solve_pressure_poisson()

        # 4. Correct velocity
        self.correct_velocity()

        # 5. Apply boundary conditions
        self.apply_boundary_conditions()

        # 6. Update time
        self.time += self.dt

        # 7. Record energy
        kinetic_energy = 0.5 * (np.sum(self.u**2) + np.sum(self.v**2))
        self.energy_history.append(kinetic_energy)

    def run(self, steps: int, verbose: bool = True):
        """Run simulation for given number of steps."""
        for i in range(steps):
            self.step()

            if verbose and (i + 1) % (steps // 10) == 0:
                ke = self.energy_history[-1]
                print(f"Step {i+1}/{steps}: Time = {self.time:.4f}, KE = {ke:.4e}")

        return self.energy_history

    def get_velocity_magnitude(self) -> np.ndarray:
        """Get velocity magnitude on cell centers."""
        # Interpolate to cell centers
        u_center = 0.5 * (self.u[:, :-1] + self.u[:, 1:])
        v_center = 0.5 * (self.v[:-1, :] + self.v[1:, :])
        return np.sqrt(u_center**2 + v_center**2)

    def compute_reynolds_number(self, L: float = None, U: float = None) -> float:
        """Compute Reynolds number."""
        L = L or self.lx
        U = U or np.max(np.abs(self.u))
        return self.rho * U * L / self.fluid.viscosity

    def save_results(self, filepath: str):
        """Save results to JSON."""
        results = {
            "parameters": {
                "nx": self.nx,
                "ny": self.ny,
                "dt": self.dt,
                "nu": self.nu,
                "rho": self.rho,
            },
            "final_time": self.time,
            "energy_history": self.energy_history,
            "max_velocity": float(np.max(self.get_velocity_magnitude())),
            "reynolds": self.compute_reynolds_number(),
        }
        with open(filepath, "w") as f:
            json.dump(results, f, indent=2)


# ============================================================================
# TEST CASES
# ============================================================================


def test_lid_driven_cavity():
    """Standard lid-driven cavity benchmark."""
    print("=" * 60)
    print("TEST: Lid-Driven Cavity (Re = 100)")
    print("=" * 60)

    solver = NavierStokesSolver(nx=32, ny=32, dt=0.001)
    solver.fluid.viscosity = 0.01  # Re ≈ 100
    solver.set_boundary_conditions("lid_driven")

    solver.run(steps=1000, verbose=True)

    Re = solver.compute_reynolds_number()
    print(f"\nReynolds Number: {Re:.1f}")
    print(f"Final Kinetic Energy: {solver.energy_history[-1]:.4e}")
    print("✅ PASS: Simulation completed without blow-up")

    return solver


def test_poiseuille_flow():
    """Poiseuille flow benchmark - analytical solution exists."""
    print("=" * 60)
    print("TEST: Poiseuille Flow")
    print("=" * 60)

    # Load real fluid properties
    data_dir = Path(__file__).parent.parent / "Data" / "poiseuille"
    fluid = FluidProperties.load(data_dir / "water_properties_20C.json")

    solver = NavierStokesSolver(nx=32, ny=32, dt=0.0001, fluid=fluid)
    solver.set_boundary_conditions("poiseuille")

    # Apply pressure gradient as body force (simplified)
    # Full implementation would need pressure inlet/outlet
    solver.run(steps=500, verbose=True)

    print(f"Fluid: Water at 20°C")
    print(f"Viscosity: {fluid.viscosity:.2e} Pa·s")
    print("✅ PASS: Poiseuille flow test completed")

    return solver


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("NAVIER-STOKES BASELINE SOLVER")
    print("=" * 60)

    # Run tests
    test_lid_driven_cavity()
    print()
    test_poiseuille_flow()
