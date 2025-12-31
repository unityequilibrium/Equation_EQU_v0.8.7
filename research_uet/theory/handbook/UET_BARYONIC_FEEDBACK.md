# 🔥 UET Baryonic Feedback Extension
> **Solving the Core-Cusp Problem via Stellar Feedback**

---

## 1. The Problem UET Faces

**Current UET Performance:**
| Galaxy Type | Pass Rate | Issue |
|:---|:---:|:---|
| LSB | 93% | ✅ Excellent |
| Spiral | 60% | ⚠️ |
| Dwarf | 59% | ⚠️ |
| **Compact** | 40% | ❌ **Core-Cusp Mismatch** |

**Root Cause:** UET assumes NFW-like cuspy profiles, but compact/dwarf galaxies show **cored** DM distributions.

---

## 2. Physics of Baryonic Feedback

### 2.1 Mechanism
1. **Supernovae/Stellar Winds** → Gas outflows from center
2. **Gravitational Potential Fluctuates** → Rapid mass changes
3. **Dark Matter Heats** → Particles gain energy, move outward
4. **Cusp → Core Transformation** → Central density flattens

### 2.2 Key Parameters
| Parameter | Symbol | Meaning |
|:---|:---|:---|
| Star Formation Rate | SFR | Rate of new stars forming |
| Stellar Mass Fraction | $f_*$ | $M_*/M_{baryon}$ |
| Gas Fraction | $f_g$ | $M_{gas}/M_{baryon}$ |
| Feedback Efficiency | $\epsilon_{fb}$ | Energy coupling to DM |

---

## 3. UET Implementation

### 3.1 Modified Halo Profile
Standard UET:
$$\frac{M_{halo}}{M_{disk}} = \frac{k}{\sqrt{\rho}}$$

With Baryonic Feedback:
$$\frac{M_{halo}}{M_{disk}} = \frac{k}{\sqrt{\rho}} \times \eta_{fb}$$

Where feedback correction:
$$\eta_{fb} = 1 - \epsilon_{fb} \cdot f_* \cdot \left(\frac{r}{r_c}\right)^{-\alpha}$$

- $r_c$ = Core radius (where cusp transforms to core)
- $\alpha$ ≈ 1 for typical feedback models
- $\epsilon_{fb}$ ≈ 0.1-0.3 (calibrated from simulations)

### 3.2 Expected Improvement
| Galaxy Type | Before | After (Expected) |
|:---|:---:|:---:|
| Compact | 40% | **60-70%** |
| Dwarf | 59% | **70-80%** |
| Overall | 73% | **78-82%** |

---

## 4. Data Sources for Testing

### SPARC (Current)
- 175 galaxies
- Good for spirals
- Limited dwarf coverage

### LITTLE THINGS (Recommended)
- 41 dwarf irregulars
- High-resolution HI (6" angular)
- Better for testing feedback model
- URL: http://science.nrao.edu/science/surveys/littlethings

---

## 5. Implementation Status

- [x] Theory documentation
- [ ] Add $\eta_{fb}$ term to galaxy test
- [ ] Download LITTLE THINGS data
- [ ] Run comparison test

---

*References: Pontzen & Governato (2012), Di Cintio et al. (2014)*
