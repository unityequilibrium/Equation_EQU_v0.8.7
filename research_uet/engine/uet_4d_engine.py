"""
🌌 UET 4D Solver
================
4D Cahn-Hilliard solver for UET 4D Field Dynamics (Universal).

⚠️ ALL SIMULATIONS ARE 4D (3 spatial + 1 time)
   NO 2D SIMULATIONS ALLOWED.
"""

import numpy as np
from typing import Callable, Tuple, Optional
import time


class UET4DSolver:
    """
    4D Unity Equilibrium Theory Solver.

    Solves Cahn-Hilliard dynamics in 3+1 spacetime:

        ∂C/∂t = M∇²(δΩ/δC)

    Where:
        Ω = ∫[V(C) + (κ/2)|∇C|² + β·C·I] dx
    """

    def __init__(
        self,
        Nx: int = 32,
        Ny: int = 32,
        Nz: int = 32,
        Lx: float = 10.0,
        Ly: float = 10.0,
        Lz: float = 10.0,
        dt: float = 0.001,
        kappa: float = 0.5,
        beta: float = 1.0,
        mobility: float = 1.0,
    ):
        """
        Initialize 4D solver.

        Parameters:
        -----------
        Nx, Ny, Nz : int
            Grid points in each spatial dimension
        Lx, Ly, Lz : float
            Physical size in each dimension
        dt : float
            Time step
        kappa : float
            Gradient energy coefficient
        beta : float
            C-I coupling strength
        mobility : float
            Cahn-Hilliard mobility coefficient
        """
        self.Nx, self.Ny, self.Nz = Nx, Ny, Nz
        self.Lx, self.Ly, self.Lz = Lx, Ly, Lz
        self.dt = dt
        self.kappa = kappa
        self.beta = beta
        self.M = mobility

        # Grid spacing
        self.dx = Lx / Nx
        self.dy = Ly / Ny
        self.dz = Lz / Nz

        # Coordinate grids
        self.x = np.linspace(0, Lx, Nx, endpoint=False)
        self.y = np.linspace(0, Ly, Ny, endpoint=False)
        self.z = np.linspace(0, Lz, Nz, endpoint=False)
        self.X, self.Y, self.Z = np.meshgrid(self.x, self.y, self.z, indexing="ij")

        # History storage
        self.history = {"t": [], "energy": [], "C_mean": [], "I_mean": []}

        print(f"✅ UET 4D Solver initialized: {Nx}×{Ny}×{Nz} grid")
        print(f"   Memory usage: ~{(Nx*Ny*Nz*8*2)/1e6:.1f} MB for C+I fields")

    def laplacian_3d(self, field: np.ndarray) -> np.ndarray:
        """
        Compute 3D Laplacian using finite differences.
        Uses periodic boundary conditions.
        """
        lap = np.zeros_like(field)

        # Second derivatives in each direction
        lap += (np.roll(field, 1, axis=0) - 2 * field + np.roll(field, -1, axis=0)) / self.dx**2
        lap += (np.roll(field, 1, axis=1) - 2 * field + np.roll(field, -1, axis=1)) / self.dy**2
        lap += (np.roll(field, 1, axis=2) - 2 * field + np.roll(field, -1, axis=2)) / self.dz**2

        return lap

    def gradient_3d(self, field: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Compute 3D gradient using central differences."""
        grad_x = (np.roll(field, -1, axis=0) - np.roll(field, 1, axis=0)) / (2 * self.dx)
        grad_y = (np.roll(field, -1, axis=1) - np.roll(field, 1, axis=1)) / (2 * self.dy)
        grad_z = (np.roll(field, -1, axis=2) - np.roll(field, 1, axis=2)) / (2 * self.dz)
        return grad_x, grad_y, grad_z

    def potential_derivative(
        self,
        C: np.ndarray,
        potential_type: str = "quartic",
        a: float = -0.5,
        delta: float = 1.0,
        s: float = 0.0,
    ) -> np.ndarray:
        """
        Compute dV/dC for various potential types.

        quartic: V(C) = a*C² + δ*C⁴ + s*C (asymmetric)
        """
        if potential_type == "quartic":
            return 2 * a * C + 4 * delta * C**3 + s
        elif potential_type == "mexican_hat":
            # V = -μ²|C|² + λ|C|⁴
            mu2, lam = a, delta  # reuse params
            return -2 * mu2 * C + 4 * lam * C**3
        else:
            return 2 * a * C + 4 * delta * C**3

    def chemical_potential(
        self,
        C: np.ndarray,
        I: np.ndarray,
        potential_type: str = "quartic",
        a: float = -0.5,
        delta: float = 1.0,
        s: float = 0.0,
    ) -> np.ndarray:
        """
        Compute chemical potential μ = δΩ/δC.

        μ = dV/dC - κ∇²C + β·I
        """
        mu = self.potential_derivative(C, potential_type, a, delta, s)
        mu -= self.kappa * self.laplacian_3d(C)
        mu += self.beta * I
        return mu

    def compute_energy(
        self,
        C: np.ndarray,
        I: np.ndarray,
        potential_type: str = "quartic",
        a: float = -0.5,
        delta: float = 1.0,
        s: float = 0.0,
    ) -> float:
        """
        Compute total free energy Ω.

        Ω = ∫[V(C) + (κ/2)|∇C|² + β·C·I] dx
        """
        # Potential energy
        if potential_type == "quartic":
            V = a * C**2 + delta * C**4 + s * C
        else:
            V = a * C**2 + delta * C**4

        # Gradient energy
        gx, gy, gz = self.gradient_3d(C)
        grad_sq = gx**2 + gy**2 + gz**2

        # Coupling energy
        coupling = self.beta * C * I

        # Total energy (integrated)
        energy_density = V + 0.5 * self.kappa * grad_sq + coupling
        dV = self.dx * self.dy * self.dz
        return np.sum(energy_density) * dV

    def evolve_step(
        self,
        C: np.ndarray,
        I: np.ndarray,
        potential_type: str = "quartic",
        a: float = -0.5,
        delta: float = 1.0,
        s: float = 0.0,
        evolve_I: bool = True,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Evolve C and I by one time step.

        Uses Cahn-Hilliard dynamics:
            ∂C/∂t = M∇²μ
        """
        # Chemical potential
        mu_C = self.chemical_potential(C, I, potential_type, a, delta, s)

        # Cahn-Hilliard update for C
        C_new = C + self.dt * self.M * self.laplacian_3d(mu_C)

        # I field dynamics (simplified)
        if evolve_I:
            mu_I = self.beta * C
            I_new = I + self.dt * self.M * self.laplacian_3d(mu_I)
        else:
            I_new = I

        return C_new, I_new

    def run(
        self,
        C0: np.ndarray,
        I0: np.ndarray,
        n_steps: int = 100,
        potential_type: str = "quartic",
        a: float = -0.5,
        delta: float = 1.0,
        s: float = 0.0,
        evolve_I: bool = True,
        save_interval: int = 10,
        verbose: bool = True,
    ) -> Tuple[np.ndarray, np.ndarray, dict]:
        """
        Run full 4D simulation.

        Returns final C, I, and history dictionary.
        """
        C = C0.copy()
        I = I0.copy()

        self.history = {"t": [], "energy": [], "C_mean": [], "I_mean": []}

        start_time = time.time()

        for step in range(n_steps):
            # Evolve
            C, I = self.evolve_step(C, I, potential_type, a, delta, s, evolve_I)

            # Record history
            if step % save_interval == 0:
                t = step * self.dt
                E = self.compute_energy(C, I, potential_type, a, delta, s)

                self.history["t"].append(t)
                self.history["energy"].append(E)
                self.history["C_mean"].append(np.mean(C))
                self.history["I_mean"].append(np.mean(I))

                if verbose and step % (save_interval * 10) == 0:
                    print(f"   Step {step:5d}: t={t:.2f}, E={E:.4f}, <C>={np.mean(C):.4f}")

        elapsed = time.time() - start_time
        if verbose:
            print(f"✅ Simulation complete in {elapsed:.1f}s")

        return C, I, self.history


def create_initial_condition_3d(
    Nx: int, Ny: int, Nz: int, type: str = "random", amplitude: float = 0.1, seed: int = 42
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Create initial conditions for 4D simulation.

    Types:
    - random: Random fluctuations
    - gaussian: Gaussian blob
    - plane_wave: Sinusoidal wave
    """
    np.random.seed(seed)

    if type == "random":
        C0 = amplitude * (np.random.rand(Nx, Ny, Nz) - 0.5)
        I0 = amplitude * (np.random.rand(Nx, Ny, Nz) - 0.5)

    elif type == "gaussian":
        x = np.linspace(-1, 1, Nx)
        y = np.linspace(-1, 1, Ny)
        z = np.linspace(-1, 1, Nz)
        X, Y, Z = np.meshgrid(x, y, z, indexing="ij")

        C0 = amplitude * np.exp(-(X**2 + Y**2 + Z**2) / 0.2)
        I0 = amplitude * np.exp(-(X**2 + Y**2 + Z**2) / 0.5)

    elif type == "plane_wave":
        x = np.linspace(0, 2 * np.pi, Nx)
        y = np.linspace(0, 2 * np.pi, Ny)
        z = np.linspace(0, 2 * np.pi, Nz)
        X, Y, Z = np.meshgrid(x, y, z, indexing="ij")

        C0 = amplitude * np.sin(X + Y)
        I0 = amplitude * np.cos(X + Z)

    else:
        C0 = np.zeros((Nx, Ny, Nz))
        I0 = np.zeros((Nx, Ny, Nz))

    return C0, I0


def test_solver():
    """Quick test of the 4D solver."""
    print("=" * 60)
    print("🧪 UET 4D SOLVER TEST")
    print("=" * 60)

    # Create solver
    solver = UET4DSolver(Nx=32, Ny=32, Nz=32, dt=0.01, kappa=0.5, beta=0.3)

    # Initial conditions
    C0, I0 = create_initial_condition_3d(32, 32, 32, type="random")

    # Run simulation
    print("\n🔄 Running 4D simulation...")
    C_final, I_final, history = solver.run(C0, I0, n_steps=100, save_interval=10, verbose=True)

    # Check results
    print("\n📊 Results:")
    print(f"   Initial energy: {history['energy'][0]:.4f}")
    print(f"   Final energy:   {history['energy'][-1]:.4f}")
    print(f"   Energy change:  {history['energy'][-1] - history['energy'][0]:.4f}")

    if history["energy"][-1] <= history["energy"][0]:
        print("   ✅ Energy decreasing (Lyapunov stable)")
    else:
        print("   ⚠️ Energy increased")

    print("\n✅ 4D solver test complete!")
    return solver, history


if __name__ == "__main__":
    test_solver()
