# ⚡ Supplement: Magneto-Hydrodynamics (MHD) in UET

> **Status:** Proposed Theoretical Extension (v2.0)
> **Goal:** Bridge the gap between "Hot Gas" (Hydro) and "True Plasma" (MHD).

## 1. The Missing Physics: Lorentz Force
Current UET simulations (Supernova) model the **Hydrodynamic** evolution:
$$ \rho \frac{D\mathbf{v}}{Dt} = -\nabla P + \rho \mathbf{g} $$

To model true **Plasma** (e.g., Solar Flares, Tokamaks, Active Galactic Nuclei), we must "Supplement" this with the **Lorentz Force**:
$$ \mathbf{F}_{mag} = \mathbf{J} \times \mathbf{B} $$

Where:
- $\mathbf{J} = \nabla \times \mathbf{B} / \mu_0$ (Current Density)
- $\mathbf{B}$ = Magnetic Field

## 2. Integrated Equation (v2.0 Target)
The Unified Equation of Motion becomes:
$$ \rho \frac{D\mathbf{v}}{Dt} = \underbrace{-\nabla P}_{\text{Pressure}} + \underbrace{\rho \mathbf{g}}_{\text{Gravity}} + \underbrace{\frac{1}{\mu_0}(\nabla \times \mathbf{B}) \times \mathbf{B}}_{\text{Magnetic Force}} $$

Using the vector identity $(\nabla \times \mathbf{B}) \times \mathbf{B} = -\nabla(B^2/2\mu_0) + (\mathbf{B}\cdot\nabla)\mathbf{B}$, we get notions of:
1.  **Magnetic Pressure:** $P_{mag} = \frac{B^2}{2\mu_0}$ (Acts like gas pressure $\nabla P$)
2.  **Magnetic Tension:** $\frac{(\mathbf{B}\cdot\nabla)\mathbf{B}}{\mu_0}$ (Acts like a stretched rubber band)

## 3. UET Connection (The "Information" Link)
In UET, we posit that **Forces emerge from Information Gradients**.
- **Gravity** $\to$ Gradient of Matter Information ($I_m$)
- **Magnetic** $\to$ Gradient of *Spin/Charge* Information ($I_c$)

**Hypothesis for v2.0:**
The Magnetic Field $\mathbf{B}$ is the "Curl" of the Information Potential Vector $\mathbf{A}_I$:
$$ \mathbf{B} = \nabla \times \mathbf{A}_I $$
And "Magnetic Pressure" is simply "Ram Pressure" of the Information Flux.

## 4. Implementation Plan
To upgrade `snr_4d_simulation.py` to `plasma_mhd_simulation.py`:
1.  **Add State Variable:** `self.B = np.zeros((DIM, DIM, DIM, 3))`
2.  **Add Evolution Step:** Induction Equation
    $$ \frac{\partial \mathbf{B}}{\partial t} = \nabla \times (\mathbf{v} \times \mathbf{B}) + \eta \nabla^2 \mathbf{B} $$
3.  **Add Force:** Include $\mathbf{J} \times \mathbf{B}$ in the momentum step `step_hydro`.
4.  **Divergence Cleaning:** Enforce $\nabla \cdot \mathbf{B} = 0$.

This roadmap "supplements" the current Hydrodynamics work to ensure completeness.
