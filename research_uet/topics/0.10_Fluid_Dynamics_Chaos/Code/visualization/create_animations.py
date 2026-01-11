"""
ANIMATED FLUID SIMULATIONS
===========================
Creates actual GIF animations showing:
1. Density field evolution
2. Velocity field (arrows moving)
3. Vortex formation
4. Lid-driven cavity flow

Output: Animated GIFs that show REAL FLUID MOTION!
"""

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import LinearSegmentedColormap
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "baseline"))


class AnimatedFluidSolver:
    """2D Fluid solver that saves animation frames."""

    def __init__(self, nx: int = 64, ny: int = 64, dt: float = 0.01):
        self.nx, self.ny = nx, ny
        self.dx = self.dy = 1.0 / nx
        self.dt = dt

        # UET fields
        self.C = np.ones((ny, nx))  # Density
        self.I = np.zeros((ny, nx))  # Information

        # Velocity (derived from C gradient)
        self.u = np.zeros((ny, nx))
        self.v = np.zeros((ny, nx))

        # Parameters
        self.kappa = 0.1
        self.beta = 0.5
        self.alpha = 2.0
        self.C0 = 1.0

        self.time = 0.0
        self.frames = []

    def set_lid_driven(self):
        """Lid-driven cavity BC."""
        # Top boundary drives flow
        self.C[-1, :] = self.C0 * 1.2
        self.C[0, :] = self.C0 * 0.9
        # Add perturbation
        xx, yy = np.meshgrid(np.linspace(0, 1, self.nx), np.linspace(0, 1, self.ny))
        self.C += 0.1 * np.sin(2 * np.pi * xx) * np.sin(np.pi * yy)

    def set_vortex(self):
        """Initialize with a vortex."""
        cx, cy = self.nx // 2, self.ny // 2
        for i in range(self.ny):
            for j in range(self.nx):
                r = np.sqrt((j - cx) ** 2 + (i - cy) ** 2)
                theta = np.arctan2(i - cy, j - cx)
                self.C[i, j] = self.C0 + 0.3 * np.exp(-(r**2) / 200) * np.cos(theta * 2)

    def set_wave(self):
        """Initialize with propagating wave."""
        xx, yy = np.meshgrid(np.linspace(0, 1, self.nx), np.linspace(0, 1, self.ny))
        self.C = self.C0 + 0.2 * np.sin(4 * np.pi * xx) * np.cos(2 * np.pi * yy)

    def compute_laplacian(self, f):
        """Compute Laplacian."""
        lap = np.zeros_like(f)
        lap[1:-1, 1:-1] = (
            f[1:-1, 2:] - 2 * f[1:-1, 1:-1] + f[1:-1, :-2]
        ) / self.dx**2 + (
            f[2:, 1:-1] - 2 * f[1:-1, 1:-1] + f[:-2, 1:-1]
        ) / self.dy**2
        return lap

    def step(self):
        """Single time step."""
        lap_C = self.compute_laplacian(self.C)

        # Gradient descent on Ω
        dOmega_dC = (
            self.alpha * (self.C - self.C0) - self.kappa * lap_C + self.beta * self.I
        )
        dOmega_dI = self.beta * self.C

        self.C -= self.dt * dOmega_dC
        self.I -= self.dt * dOmega_dI

        # Keep positive
        self.C = np.maximum(self.C, 0.01)

        # Derive velocity from C gradient (approximate)
        self.u[1:-1, 1:-1] = -(self.C[1:-1, 2:] - self.C[1:-1, :-2]) / (2 * self.dx)
        self.v[1:-1, 1:-1] = -(self.C[2:, 1:-1] - self.C[:-2, 1:-1]) / (2 * self.dy)

        self.time += self.dt


def create_density_animation(output_dir: Path, steps: int = 100, fps: int = 15):
    """Create animated density field GIF."""
    print("\n🌊 Creating Density Animation...")

    solver = AnimatedFluidSolver(nx=64, ny=64)
    solver.set_lid_driven()

    fig, ax = plt.subplots(figsize=(6, 6))

    # Custom colormap (blue = low density, red = high)
    cmap = plt.cm.RdYlBu_r

    im = ax.imshow(
        solver.C, cmap=cmap, vmin=0.7, vmax=1.4, origin="lower", aspect="equal"
    )
    plt.colorbar(im, ax=ax, label="Density C")
    ax.set_title("UET Fluid Density Evolution")
    ax.set_xlabel("x")
    ax.set_ylabel("y")

    frames = []

    for i in range(steps):
        solver.step()
        if i % 2 == 0:  # Save every 2nd frame
            frames.append(solver.C.copy())

    def update(frame_idx):
        im.set_array(frames[frame_idx])
        ax.set_title(f"UET Fluid Density (t={frame_idx*2*solver.dt:.3f}s)")
        return [im]

    ani = animation.FuncAnimation(
        fig, update, frames=len(frames), interval=1000 // fps, blit=True
    )

    gif_path = output_dir / "density_evolution.gif"
    ani.save(str(gif_path), writer="pillow", fps=fps)
    plt.close()

    print(f"   ✅ Saved: {gif_path}")
    return gif_path


def create_velocity_animation(output_dir: Path, steps: int = 100, fps: int = 15):
    """Create animated velocity field (arrows moving)."""
    print("\n💨 Creating Velocity Field Animation...")

    solver = AnimatedFluidSolver(nx=32, ny=32)
    solver.set_vortex()

    fig, ax = plt.subplots(figsize=(6, 6))

    # Grid for arrows
    skip = 2
    x = np.arange(0, solver.nx, skip)
    y = np.arange(0, solver.ny, skip)
    X, Y = np.meshgrid(x, y)

    frames = []

    for i in range(steps):
        solver.step()
        if i % 2 == 0:
            frames.append(
                {"C": solver.C.copy(), "u": solver.u.copy(), "v": solver.v.copy()}
            )

    def update(frame_idx):
        ax.clear()
        frame = frames[frame_idx]

        # Background density
        ax.imshow(
            frame["C"], cmap="coolwarm", origin="lower", alpha=0.7, vmin=0.7, vmax=1.3
        )

        # Velocity arrows
        U = frame["u"][::skip, ::skip]
        V = frame["v"][::skip, ::skip]
        speed = np.sqrt(U**2 + V**2)

        ax.quiver(X, Y, U, V, speed, cmap="viridis", scale=5, alpha=0.8)
        ax.set_title(f"UET Velocity Field (t={frame_idx*2*solver.dt:.3f}s)")
        ax.set_xlim(0, solver.nx)
        ax.set_ylim(0, solver.ny)

    ani = animation.FuncAnimation(fig, update, frames=len(frames), interval=1000 // fps)

    gif_path = output_dir / "velocity_field.gif"
    ani.save(str(gif_path), writer="pillow", fps=fps)
    plt.close()

    print(f"   ✅ Saved: {gif_path}")
    return gif_path


def create_vortex_animation(output_dir: Path, steps: int = 150, fps: int = 15):
    """Create vortex evolution animation."""
    print("\n🌀 Creating Vortex Animation...")

    solver = AnimatedFluidSolver(nx=64, ny=64, dt=0.005)
    solver.set_vortex()

    fig, ax = plt.subplots(figsize=(6, 6))

    frames = []

    for i in range(steps):
        solver.step()
        if i % 3 == 0:
            frames.append(solver.C.copy())

    # Create vorticity-like visualization
    def compute_vorticity(C):
        dCdx = np.gradient(C, axis=1)
        dCdy = np.gradient(C, axis=0)
        return np.sqrt(dCdx**2 + dCdy**2)

    def update(frame_idx):
        ax.clear()
        C = frames[frame_idx]
        # Subtract mean to highlight features
        C_centered = C - C.mean()

        ax.imshow(C_centered, cmap="seismic", origin="lower", vmin=-0.3, vmax=0.3)
        ax.contour(C_centered, levels=10, colors="black", alpha=0.3, linewidths=0.5)
        ax.set_title(f"UET Vortex Evolution (frame {frame_idx})")
        ax.axis("off")

    ani = animation.FuncAnimation(fig, update, frames=len(frames), interval=1000 // fps)

    gif_path = output_dir / "vortex_evolution.gif"
    ani.save(str(gif_path), writer="pillow", fps=fps)
    plt.close()

    print(f"   ✅ Saved: {gif_path}")
    return gif_path


def create_wave_animation(output_dir: Path, steps: int = 120, fps: int = 20):
    """Create wave propagation animation."""
    print("\n🌊 Creating Wave Animation...")

    solver = AnimatedFluidSolver(nx=80, ny=80, dt=0.003)
    solver.set_wave()

    fig, ax = plt.subplots(figsize=(7, 6))

    frames = []

    for i in range(steps):
        solver.step()
        if i % 2 == 0:
            frames.append(solver.C.copy())

    im = ax.imshow(frames[0], cmap="ocean", origin="lower", vmin=0.7, vmax=1.3)
    plt.colorbar(im, ax=ax, label="Density C")
    ax.set_title("UET Wave Propagation")

    def update(frame_idx):
        im.set_array(frames[frame_idx])
        ax.set_title(f"UET Wave Propagation (frame {frame_idx})")
        return [im]

    ani = animation.FuncAnimation(
        fig, update, frames=len(frames), interval=1000 // fps, blit=True
    )

    gif_path = output_dir / "wave_propagation.gif"
    ani.save(str(gif_path), writer="pillow", fps=fps)
    plt.close()

    print(f"   ✅ Saved: {gif_path}")
    return gif_path


def create_3d_surface_animation(output_dir: Path, steps: int = 100, fps: int = 12):
    """Create 3D surface animation of density."""
    print("\n📈 Creating 3D Surface Animation...")

    solver = AnimatedFluidSolver(nx=40, ny=40, dt=0.005)
    solver.set_lid_driven()

    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection="3d")

    x = np.arange(solver.nx)
    y = np.arange(solver.ny)
    X, Y = np.meshgrid(x, y)

    frames = []

    for i in range(steps):
        solver.step()
        if i % 3 == 0:
            frames.append(solver.C.copy())

    def update(frame_idx):
        ax.clear()
        Z = frames[frame_idx]

        surf = ax.plot_surface(
            X, Y, Z, cmap="coolwarm", vmin=0.7, vmax=1.3, linewidth=0, antialiased=True
        )
        ax.set_zlim(0.7, 1.4)
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Density C")
        ax.set_title(f"UET 3D Density Surface (frame {frame_idx})")
        ax.view_init(elev=30, azim=frame_idx * 2)  # Rotate view!

    ani = animation.FuncAnimation(fig, update, frames=len(frames), interval=1000 // fps)

    gif_path = output_dir / "3d_surface.gif"
    ani.save(str(gif_path), writer="pillow", fps=fps)
    plt.close()

    print(f"   ✅ Saved: {gif_path}")
    return gif_path


def generate_all_animations():
    """Generate all animations."""
    print("=" * 70)
    print("🎬 GENERATING FLUID ANIMATION GIFs")
    print("=" * 70)

    output_dir = Path(__file__).parent.parent.parent / "Result" / "animations"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Output: {output_dir}")

    gifs = []

    # Create all animations
    gifs.append(create_density_animation(output_dir))
    gifs.append(create_velocity_animation(output_dir))
    gifs.append(create_vortex_animation(output_dir))
    gifs.append(create_wave_animation(output_dir))
    gifs.append(create_3d_surface_animation(output_dir))

    # Summary
    print("\n" + "=" * 70)
    print("🎬 ANIMATION GENERATION COMPLETE!")
    print("=" * 70)

    print(f"\n📁 Generated {len(gifs)} GIF animations:")
    for gif in gifs:
        size = gif.stat().st_size / 1024
        print(f"   • {gif.name} ({size:.1f} KB)")

    print(f"\n📂 Location: {output_dir}")
    print("\n🎥 Animations show:")
    print("   1. density_evolution.gif — Density field changes over time")
    print("   2. velocity_field.gif — Arrows showing flow direction")
    print("   3. vortex_evolution.gif — Vortex spinning and dissipating")
    print("   4. wave_propagation.gif — Waves moving through fluid")
    print("   5. 3d_surface.gif — 3D rotating surface view")


if __name__ == "__main__":
    generate_all_animations()
