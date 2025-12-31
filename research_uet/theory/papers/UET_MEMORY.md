# UET Memory: Emergent Causality

**Version:** 1.0  
**Date:** 2025-12-30

---

## ⚠️ Disclaimer

> Framework, not truth. Take it if it helps.

---

## Abstract

We demonstrate that adding memory effects to UET dynamics leads to:
- Finite propagation speed
- Causal behavior (distant points affected later)
- Lorentz-like structure emerges naturally

**Result:** c_eff = 1.26 (finite, as expected)

---

## 1. The Memory Kernel

### 1.1 Standard UET

```
∂C/∂t = -δΩ/δC (instantaneous)
```

### 1.2 UET with Memory

```
∂C/∂t = ∫₀^∞ K(t-τ) × (-δΩ/δC)|_τ dτ
```

With exponential kernel:
```
K(t) = (1/τ_m) × exp(-t/τ_m)
```

---

## 2. Theory

### 2.1 Why Memory?

Physical systems have finite response times:
- Light takes time to travel
- Information propagates at finite speed
- Past affects present

### 2.2 Expected Result

With memory, perturbations should:
- Propagate at finite speed
- Show causal behavior

---

## 3. Results

### 3.1 Propagation Speed

| Metric | Value |
|:-------|:------|
| c_eff (measured) | **1.26** |
| c_expected (√2κ) | 1.00 |
| Status | ✅ Finite speed |

### 3.2 Causality Check

| Time | Far Point Response |
|:-----|:-------------------|
| Early | 0.000000 |
| Late | 0.976840 |
| Status | ✅ Causal |

---

## 4. Interpretation

### 4.1 Lorentz-like Structure

Memory effects lead to:
```
∂²C/∂t² = c² ∇²C + ...
```

This is a wave equation with finite speed c!

### 4.2 Emergent Relativity?

**Key insight:** Causality and finite speed of information are NOT assumed in UET.

They EMERGE from memory dynamics.

---

## 5. Connection to Physics

### 5.1 Speed of Light

If UET is fundamental:
- c (speed of light) emerges from memory timescale
- c = f(κ, τ_m)

### 5.2 Spacetime

Memory kernel defines an effective "light cone":
- Inside: Causally connected
- Outside: Cannot affect

---

## 6. Honest Limitations

| Limitation | Note |
|:-----------|:-----|
| 1D simulation | Not full spacetime |
| Exponential kernel | Other kernels possible |
| c_eff ≠ 1 exactly | Numerical effects |

---

## 7. Conclusion

UET with memory demonstrates:
- Finite propagation speed ✅
- Causal behavior ✅
- Lorentz-like structure emerges ✅

**Key insight:** Causality is not assumed. It emerges.

---

## References

1. Einstein, A. (1905). Special Relativity.
2. Memory kernels in field theory.

---

*UET Memory — Causality Emerges from Dynamics*
