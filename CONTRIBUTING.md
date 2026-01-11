# 🤝 Contributing to Unity Equilibrium Theory

**Status: 125 Tests / 20 Topics — 98.4% PASS with REAL DATA + Real-Time APIs**

---

## 🌟 The Mission: Why We Build

### The Problem: A Fragmented Universe
For the last century, physics has been divided. We have **General Relativity** for the stars and **Quantum Mechanics** for the atoms, but they speak different languages.

### The Solution: A Unified Perspective
**Unity Equilibrium Theory (UET)** offers a new "Middle Language." It posits that the universe is a self-optimizing system seeking equilibrium through information processing.

### 📚 Essential Reading for Contributors

| Document | Description |
|:---------|:------------|
| [UET_RESEARCH_HUB.md](research_uet/UET_RESEARCH_HUB.md) | Full test matrix (125 tests) |
| [SINGLE_SOURCE_OF_TRUTH.md](research_uet/SINGLE_SOURCE_OF_TRUTH.md) | Canonical metrics & DOIs |
| [DATA_SOURCE_MAP.md](research_uet/DATA_SOURCE_MAP.md) | All 25 data sources (incl. real-time APIs) |
| [topics/](research_uet/topics/) | 20 physics domains |

---

## 🎯 Core Equation

$$\Omega[C,I] = \int \left[ V(C) + \frac{\kappa}{2}|\nabla C|^2 + \beta C I \right] dx$$

| Variable | Meaning |
|:---------|:--------|
| **C** | Capacity (mass, liquidity, connectivity) |
| **I** | Information (entropy, stimulus) |
| **V** | Potential (cost of becoming) |
| **κ** | Gradient penalty |
| **β** | Coupling constant |

---

## 📋 Physics Contribution Standards (STRICT)

We only accept physics contributions that are validated against **Independent Empirical Data**.

### 1. The Validation Matrix Requirement
Every PR adding a physics domain must update the **README Matrix** with:

1. **Phenomenon:** What are you testing? (e.g., *Hydrogen Spectrum*)
2. **Equation:** Derived from `Ω[C, I]`
3. **Data Source:** Must have a DOI (e.g., *NIST ASD*, *PDG 2024*, *SPARC*)
4. **Error Metric:** Quantitative result (e.g., *<1% Error*, *PASS/FAIL*)

### 2. Prohibited Content
- ❌ **No Pure Theory:** We do not accept "philosophical" papers without data
- ❌ **No Parameter Fixing:** Constants must be derived, not curve-fit
- ❌ **No Circular Logic:** Must use external, independent data sources

### 3. Required Files for New Topics
```
topics/0.XX_Topic_Name/
├── README.md           # Following 'how to README.md' template
├── Code/
│   └── test_*.py       # At least one test file
├── Ref/
│   └── REFERENCES.py   # DOIs for all data sources
├── Data/
│   └── download_data.py
└── Doc/
    └── section_1/
        ├── before/Doc.md
        └── after/Doc.md
```

---

## 🛠️ Development Workflow

### For New Contributors (First Time Only)

```bash
git clone https://github.com/unityequilibrium/Equation-UET-v0.8.7.git
cd Equation-UET-v0.8.7
pip install -r requirements.txt
```

### Run Tests

```bash
python research_uet/topics/run_all_tests.py
# Expected: 125 tests, 98.4% pass
```

### Adding a New Test

1. Create test in `topics/0.XX_Your_Topic/Code/test_*.py`
2. Use REAL data with DOI reference
3. Assert `error < tolerance`
4. Update docs (UET_RESEARCH_HUB.md, SINGLE_SOURCE_OF_TRUTH.md)

---

## 🐛 Bug Reports

Please include:
1. **Script Name**: Which test failed?
2. **Error Log**: Full Python traceback
3. **Data Context**: Which dataset?

---

## 🔍 Transparency

**AI-Assisted Framework:**
This codebase was developed using agentic AI workflows.
- **Review Process:** Code is reviewed for *scientific accuracy*, not *authorship intent*
- **Verification:** The ultimate arbiter is the **Data**

---

## 📜 License
By contributing, you agree that your code will be licensed under **MIT License**.

---

*Unity Equilibrium Theory — A Simulation Framework, Not a Universal Law*

*[GitHub](https://github.com/unityequilibrium/Equation-UET-v0.8.7)*
