"""
UET Parameter Calibration for Fluid Dynamics
=============================================
Find optimal UET parameters (κ, β, α) to match physical fluid behavior.

Goal: Match Poiseuille flow profile shape and magnitude.
"""

import numpy as np
import json
from pathlib import Path
from uet_fluid_solver import UETFluidSolver, UETParameters


def analytical_poiseuille(y, H, dP_dx, mu):
    """Analytical Poiseuille velocity profile."""
    return (dP_dx / (2 * mu)) * y * (H - y)


def compute_error(
    params: UETParameters, target_u_max: float, ny: int = 32, H: float = 1.0
) -> dict:
    """Compute error between UET and target Poiseuille profile."""
    solver = UETFluidSolver(nx=64, ny=ny, lx=2.0, ly=H, dt=0.001, params=params)
    solver.set_boundary_conditions("poiseuille")
    solver.run(steps=500, verbose=False)

    # Extract profile
    u_uet = -solver.u[:, solver.nx // 2]  # Negative for correct direction

    # Check stability
    if np.isnan(solver.C).any():
        return {"stable": False, "error": float("inf")}

    # Compute metrics
    u_max = np.max(np.abs(u_uet))

    # Magnitude error
    if u_max > 0:
        magnitude_ratio = u_max / target_u_max
    else:
        magnitude_ratio = 0.0

    # Shape correlation
    y = np.linspace(0, H, ny)
    u_anal = analytical_poiseuille(y, H, 0.1, 0.01)
    u_anal_norm = u_anal / np.max(u_anal)
    u_uet_norm = (
        np.abs(u_uet) / np.max(np.abs(u_uet)) if u_max > 0 else np.zeros_like(u_uet)
    )

    # Trim edges
    if len(u_anal_norm[2:-2]) == len(u_uet_norm[2:-2]):
        try:
            correlation = np.corrcoef(u_anal_norm[2:-2], u_uet_norm[2:-2])[0, 1]
        except:
            correlation = 0.0
    else:
        correlation = 0.0

    return {
        "stable": True,
        "u_max_uet": u_max,
        "u_max_target": target_u_max,
        "magnitude_ratio": magnitude_ratio,
        "correlation": correlation,
        "kappa": params.kappa,
        "beta": params.beta,
        "alpha": params.alpha,
    }


def parameter_sweep():
    """Sweep parameters to find best match."""
    print("=" * 60)
    print("UET PARAMETER CALIBRATION")
    print("=" * 60)

    # Target from analytical Poiseuille
    H = 1.0
    mu = 0.01
    dP_dx = 0.1
    target_u_max = (dP_dx / (2 * mu)) * (H / 2) * (H - H / 2)
    print(f"Target u_max: {target_u_max:.4f} m/s")

    # Parameter ranges
    kappas = [0.001, 0.005, 0.01, 0.05, 0.1]
    betas = [0.01, 0.05, 0.1, 0.5]
    alphas = [0.5, 1.0, 2.0]

    results = []
    best_result = None
    best_score = -1

    total = len(kappas) * len(betas) * len(alphas)
    count = 0

    print(f"\nTesting {total} parameter combinations...")

    for kappa in kappas:
        for beta in betas:
            for alpha in alphas:
                count += 1

                params = UETParameters(kappa=kappa, beta=beta, alpha=alpha, C0=1.0)
                result = compute_error(params, target_u_max)
                results.append(result)

                if result["stable"]:
                    # Score based on correlation (higher is better)
                    score = abs(
                        result["correlation"]
                    )  # abs because -1 is also good shape

                    if score > best_score:
                        best_score = score
                        best_result = result
                        print(
                            f"  [{count}/{total}] κ={kappa}, β={beta}, α={alpha} → corr={result['correlation']:.4f} ★"
                        )

    print("\n" + "=" * 60)
    print("BEST PARAMETERS")
    print("=" * 60)

    if best_result:
        print(f"κ (kappa): {best_result['kappa']}")
        print(f"β (beta):  {best_result['beta']}")
        print(f"α (alpha): {best_result['alpha']}")
        print(f"Correlation: {best_result['correlation']:.4f}")
        print(f"Magnitude ratio: {best_result['magnitude_ratio']:.4f}")
    else:
        print("No stable configuration found!")

    # Save results
    result_dir = Path(__file__).parent.parent.parent / "Result" / "calibration"
    result_dir.mkdir(parents=True, exist_ok=True)

    with open(result_dir / "parameter_sweep.json", "w") as f:
        json.dump(
            {
                "target_u_max": target_u_max,
                "best": best_result,
                "all_results": [r for r in results if r["stable"]],
            },
            f,
            indent=2,
            default=str,
        )

    print(f"\n📊 Results saved to: {result_dir / 'parameter_sweep.json'}")

    return best_result


def test_best_params():
    """Test with best found parameters."""
    print("\n" + "=" * 60)
    print("TESTING CALIBRATED PARAMETERS")
    print("=" * 60)

    # Best parameters from sweep (or defaults)
    params = UETParameters(kappa=0.01, beta=0.1, alpha=1.0, C0=1.0)

    solver = UETFluidSolver(nx=64, ny=32, lx=2.0, ly=1.0, dt=0.001, params=params)
    solver.set_boundary_conditions("poiseuille")

    print("Running simulation...")
    solver.run(steps=1000, verbose=False)

    print(f"Stable: {not np.isnan(solver.C).any()}")
    print(f"Final Ω: {solver.omega_history[-1]:.4e}")

    # Check profile
    u_uet = -solver.u[:, solver.nx // 2]
    print(f"Max velocity: {np.max(np.abs(u_uet)):.6f}")

    return solver


if __name__ == "__main__":
    best = parameter_sweep()
    test_best_params()
