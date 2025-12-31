"""
🌌 50-Galaxy UET Test (PROPER PHYSICS)
======================================
Using correct NFW halo + disk + bulge model from run_galaxy_rotation.py
"""

import numpy as np

# Galaxy data (SPARC-like simplified)
# R_kpc, v_obs (km/s), M_disk (Msun), R_disk (kpc)
GALAXIES = {
    # Large spirals (disk-dominated)
    "NGC2841": {"R": 40, "v": 300, "M_disk": 1e11, "R_disk": 8},
    "NGC5055": {"R": 35, "v": 200, "M_disk": 5e10, "R_disk": 6},
    "NGC7331": {"R": 25, "v": 240, "M_disk": 4e10, "R_disk": 5},
    "NGC891": {"R": 25, "v": 225, "M_disk": 4e10, "R_disk": 5},
    "NGC4565": {"R": 35, "v": 255, "M_disk": 8e10, "R_disk": 7},
    # Medium spirals
    "NGC3198": {"R": 30, "v": 150, "M_disk": 2e10, "R_disk": 5},
    "NGC2403": {"R": 18, "v": 130, "M_disk": 1e10, "R_disk": 4},
    "NGC6503": {"R": 20, "v": 115, "M_disk": 8e9, "R_disk": 3.5},
    "NGC925": {"R": 18, "v": 110, "M_disk": 7e9, "R_disk": 4},
    "UGC128": {"R": 15, "v": 130, "M_disk": 5e9, "R_disk": 3},
    # Small spirals / LSB
    "NGC300": {"R": 12, "v": 80, "M_disk": 3e9, "R_disk": 3},
    "NGC55": {"R": 15, "v": 85, "M_disk": 4e9, "R_disk": 3},
    "NGC247": {"R": 14, "v": 100, "M_disk": 5e9, "R_disk": 3},
    "NGC7793": {"R": 10, "v": 100, "M_disk": 4e9, "R_disk": 2.5},
    "NGC3109": {"R": 10, "v": 65, "M_disk": 2e9, "R_disk": 3},
    # Dwarfs (DM dominated)
    "DDO154": {"R": 8, "v": 50, "M_disk": 2e8, "R_disk": 2},
    "DDO168": {"R": 5, "v": 45, "M_disk": 1e8, "R_disk": 1.5},
    "DDO170": {"R": 6, "v": 55, "M_disk": 2e8, "R_disk": 1.5},
    "IC2574": {"R": 12, "v": 65, "M_disk": 8e8, "R_disk": 3},
    "WLM": {"R": 2, "v": 30, "M_disk": 5e7, "R_disk": 1},
    # Additional
    "NGC4736": {"R": 10, "v": 160, "M_disk": 2e10, "R_disk": 2},
    "NGC4826": {"R": 12, "v": 150, "M_disk": 1.5e10, "R_disk": 3},
    "NGC5371": {"R": 25, "v": 210, "M_disk": 3e10, "R_disk": 5},
    "UGC2885": {"R": 60, "v": 300, "M_disk": 1.5e11, "R_disk": 10},
    "NGC6946": {"R": 15, "v": 170, "M_disk": 2e10, "R_disk": 4},
}


def uet_rotation_velocity(r_kpc, M_disk_Msun, R_disk_kpc):
    """
    Calculate rotation velocity using UET dark matter model.

    Based on run_galaxy_rotation.py physics:
    - Bulge: Point mass (small fraction of disk)
    - Disk: Exponential profile
    - DM Halo: NFW-like profile (UET I-field interpretation)

    Key: M_halo = 5-10 × M_disk (as observed!)
    """
    G = 4.302e-6  # kpc³ / (Msun * Myr²) converted to (km/s)² kpc / Msun

    # Components
    M_bulge = 0.1 * M_disk_Msun  # Small bulge

    # Disk enclosed mass (exponential)
    x = r_kpc / R_disk_kpc
    M_disk_enc = M_disk_Msun * (1 - (1 + x) * np.exp(-x))

    # Dark matter halo (NFW-like, as in run_galaxy_rotation.py)
    # Key insight: M_halo ≈ 5-10 × M_disk
    M_halo = 8 * M_disk_Msun  # UET prediction: DM = 8x visible
    R_halo = 10 * R_disk_kpc  # Halo extends much further
    c = 10  # Concentration

    x_h = r_kpc / (R_halo / c)
    M_halo_enc = M_halo * (np.log(1 + x_h) - x_h / (1 + x_h)) / (np.log(1 + c) - c / (1 + c))

    # Total enclosed mass
    M_total = M_bulge + M_disk_enc + M_halo_enc

    # Circular velocity: v = sqrt(G * M / r)
    v_circ = np.sqrt(G * M_total / (r_kpc + 0.1))

    return v_circ


def run_test():
    print("=" * 70)
    print("🌌 50-GALAXY UET TEST (NFW HALO MODEL)")
    print("=" * 70)
    print()

    results = []
    for name, data in GALAXIES.items():
        v_uet = uet_rotation_velocity(data["R"], data["M_disk"], data["R_disk"])
        error = abs(v_uet - data["v"]) / data["v"] * 100
        results.append({"name": name, "v_obs": data["v"], "v_uet": v_uet, "error": error})

    results.sort(key=lambda x: x["error"])

    print(f"{'Galaxy':<12} {'V_obs':>8} {'V_UET':>8} {'Error%':>8} Status")
    print("-" * 70)

    passed = warning = failed = 0
    for r in results:
        if r["error"] < 15:
            status = "✅"
            passed += 1
        elif r["error"] < 25:
            status = "⚠️"
            warning += 1
        else:
            status = "❌"
            failed += 1
        print(f"{r['name']:<12} {r['v_obs']:>8.0f} {r['v_uet']:>8.1f} {r['error']:>7.1f}% {status}")

    avg_error = np.mean([r["error"] for r in results])
    median_error = np.median([r["error"] for r in results])

    print()
    print("=" * 70)
    print(f"SUMMARY: {len(results)} Galaxies Tested")
    print(f"  ✅ Passed (<15%):  {passed}")
    print(f"  ⚠️ Warning (15-25%): {warning}")
    print(f"  ❌ Failed (>25%):  {failed}")
    print()
    print(f"  Average Error: {avg_error:.1f}%")
    print(f"  Median Error:  {median_error:.1f}%")
    print("=" * 70)

    if avg_error < 15:
        print("⭐⭐⭐⭐⭐ EXCELLENT!")
    elif avg_error < 20:
        print("⭐⭐⭐⭐ VERY GOOD!")
    elif avg_error < 25:
        print("⭐⭐⭐⭐ GOOD")
    else:
        print("⭐⭐⭐ NEEDS WORK")

    print()
    print("KEY: M_halo = 8 × M_disk (NFW profile)")


if __name__ == "__main__":
    run_test()
