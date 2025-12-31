# 🏗️ UET Neutrino Research: Structural Blueprint
> **Design Documentation for Directory Organization**

This document outlines the architectural logic behind the reorganization of the `neutrino_research` module. This design was implemented to ensure scalability, separation of concerns, and code stability.

---

## 1. The Directory Tree (Visual Map)

```text
research_uet/
├── uet_4d_engine.py           <-- THE UNIVERSAL ENGINE (Solvers)
│                                  (Shared by Galaxies, Neutrinos, Brain, etc.)
├── neutrino_research/         <-- SUB-PROJECT 1: Neutrinos
│   ├── README.md
│   │
│   ├── analysis/              <-- The Lab
│   │   ├── muon_g2_uet.py
│   │   └── ...
│   │
│   └── data_acquisition/      <-- The Data
│       └── ...
```

---

## 2. Design Logic (Why this structure?)

### A. Separation of Concerns
*   **Problem:** The original design hid the "Universal Solver" inside the Neutrino folder, making it look like a "Neutrino-only" tool.
*   **Solution (The Unified Fix):**
    *   **Universal Engine:** `uet_4d_engine.py` is now at the ROOT of research. It is the "One Truth" for all UET simulations.
    *   **Components:** `neutrino_research`, `galaxy_research` (future), etc., are just *consumers* of this engine.

### B. Stability Assurance (The "Wiring")
How do we ensure moving files doesn't break the code? We use **Relative Path Imports**.

**1. The Analysis Scripts (`analysis/*.py`)**
They need the Universal Engine from the root.
*   *The Fix:* We point 2 levels up.
    ```python
    import sys
    # Point to research_uet root
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
    from uet_4d_engine import UET4DSolver
    ```

**2. The Data Loading (`analysis/*.py`)**
They need data from `data_acquisition`.
*   *The Fix:* Relative path pointers.
    ```python
    # Look one folder up (..) then into data_acquisition/data
    data_path = os.path.join(os.path.dirname(__file__), "../data_acquisition/data", "file.json")
    ```

---

## 3. Workflow Validation

| Action | Old Way (Flat) | New Way (Structured) | Benefit |
|:-------|:---------------|:---------------------|:--------|
| **Run G-2 Test** | `python muon_g2.py` | `cd analysis` -> `python muon_g2.py` | Keeps output files away from source code. |
| **Fix Solver** | Search in 20 files | Go to `core/uet_solver_4d.py` | Single point of truth. |
| **Add New Exp** | Clutters root folder | Create `analysis/new_exp.py` | Infinite scalability. |

---

*This design ensures that even if we add 50 new experiments, the 'Core' engine remains clean and untouched.*
