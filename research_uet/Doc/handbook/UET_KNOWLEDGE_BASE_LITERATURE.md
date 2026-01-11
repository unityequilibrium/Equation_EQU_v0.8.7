# 📚 UET Knowledge Base: Literature & Comparisons
> **Validating UET against established science (Astrophysics, Neuroscience, Physics)**

---

## 1. Astrophysics: Supernova Remnants (SNR)

**Objective:** Compare UET 4D Simulation with standard literature (Sedov, Taylor, Cioffi).

### 1.1 Evolution Phases matched
| Phase | Duration (Lit) | UET Simulation | Status |
|:------|:---------------|:---------------|:-------|
| **Free Expansion** | ~200 yr | 800 yr (w/ high mass) | ⚠️ Calibrating |
| **Sedov-Taylor** | 10-20 kyr | 12 kyr | ✅ Match |
| **Snowplow** | 20+ kyr | 22 kyr | ✅ Match |

### 1.2 Key Equations Validated
*   **Sedov-Taylor:** $R(t) \propto (E/\rho)^{1/5} t^{2/5}$ (UET reproduces this scaling naturally).
*   **Transition:** Matches Cioffi et al. (1988) cooling time approximation.

### 1.3 Cas A Specifics
*   **Observed Radius:** ~2.5 pc (approx 340 years)
*   **UET Predicted:** 2.4-2.6 pc (Error < 5%)
*   **MHD Note:** Magnetic pressure term ($B^2/8\pi$) was required to match deceleration profile.

---

## 2. Neuroscience: Brain Dynamics

**Objective:** Compare UET's $\beta$ parameter with 1/f noise in EEG spectra.

### 2.1 The "Criticality" Hypothesis
Literature (Beggs & Plenz, 2003) suggests the brain operates at a critical point (phase transition).
*   **Spectral Slope:** Power $S(f) \propto 1/f^{\beta}$
*   **Healthy Brain:** $\beta \in [1.5, 2.5]$
*   **UET Finding:** $\beta \approx 1.94$ (from `brain_eeg_test.py`)

### 2.2 Interpretation
UET's $\beta$ coupling constant directly maps to the spectral exponent of the Neural "Information Fluid".
*   $\beta < 1$: White noise (Disorder/Epilepsy?)
*   $\beta > 3$: Brownian noise (Coma/Sleep?)
*   $\beta \approx 2$: Pink noise (Active Processing) -> **UET Sweet Spot**

---

## 3. Physics: Grand Unification Targets

**Objective:** Identifying gaps where UET can bridge Micro and Macro physics.

### 3.1 The G-2 Anomaly (Micro)
*   **Problem:** Muon magnetic moment deviates by 4.2$\sigma$.
*   **UET Solution:** Information Field Mass ($M_I$) of ~102 GeV explains the gap when coupled at $\beta \approx 2$.

### 3.2 Dark Matter (Macro)
*   **Problem:** Galaxy rotation curves imply missing mass.
*   **Standard Model:** WIMPs (statistically distinct particles).
*   **UET Solution:** Geometric projection of the *same* Information Field ($M_I \approx 4\pi \times k_{galaxy}$).

---

## 4. General Relativity: Black Holes (CCBH)

**Objective:** Does UET work in extreme gravity? (Re-evaluating Black Hole Entropy).

### 4.1 The CCBH Test Findings
Analysis of the 'Cosmological Coupling of Black Holes' (CCBH) data:
*   **Hypothesis:** If Black Holes are purely "gravitational", $k$ might differ from 1.0.
*   **Result:** CCBH analysis shows $k \approx 3.0$ (Volume coupling) in some contexts, BUT strictly Information-Theoretic $k \approx 1.0$ holds for event horizon bits ($S_{BH} = A/4$).
*   **UET Interpretation:** A Black Hole is a "Maximum Information Density" object ($C_{max}$). The Event Horizon acts as the ultimate Boundary where $C \to \infty$ relative to outside.

---

## 5. Cosmology: The Lambda ($\Lambda$) Sweep

**Objective:** What is Dark Energy in UET?

### 5.1 The Lambda Parameter
In the Quartic Potential $V(C) = aC^2 + \delta C^4$:
*   Standard Physics: $\Lambda$ is "Vacuum Energy".
*   UET: $\delta$ (Quartic coefficient) acts like an effective $\Lambda$.

### 5.2 Sweep Results
*   **High $\delta$:** System collapses (Big Crunch).
*   **Negative $\delta$:** System explodes (Big Rip).
*   **Small Positive $\delta$:** System supports stable, long-lived structures (Galaxies).
*   **Conclusion:** The observed small $\Lambda$ value is a *requirement* for Information Complexity to emerge. It's not a fine-tuning accident; it's an Anthropic selection of the "Information Fluid" viscosity.

---

*Compiled from: SNR_LITERATURE_REVIEW.md, UET_LITERATURE_BRAIN.md, NEUTRINO_DARK_MATTER_BRIDGE.md, CCBH_ANALYSIS, LAMBDA_SWEEP_LOGS*
