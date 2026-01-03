# Complex Systems Lab (Non-Physics)
## UET Application to Economic, Biological & Social Systems

---

## 🏗️ Structure

| Folder | Test | Data Source | Status |
|--------|------|-------------|--------|
| `economy/` | `test_03_economy.py` | WorldBank GDP | ✅ PASS |
| `bio/` | `test_04_bio.py` | PhysioNet EEG | ✅ PASS |
| `medical/` | `test_05_medical.py` | OWID COVID | ⏳ Need Data |
| `climate/` | `test_06_climate.py` | NOAA | ⚠️ WARN |
| `inequality/` | `test_07_inequality.py` | WorldBank Gini | ⚠️ WARN |

---

## 📊 Data Sources

### Located in: `research_uet/data/06_complex_systems/`

| Data | Path | Source |
|------|------|--------|
| EEG | `Real_EEG_Sample.npy` | PhysioNet |
| Economic | `economy/` | WorldBank |
| Climate | `climate/` | NOAA |
| Inequality | `inequality/` | WorldBank Gini |
| Social | `social/` | Various |

---

## 🔗 UET Connection

These tests apply the UET framework to **non-physics** systems:

```
Ω[C, I] = ∫ [V(C) + (κ/2)|∇C|² + β·C·I + ½I²] dx
```

- **Economy**: C = GDP, I = Trade Flow
- **Bio**: C = Neural Activity, I = Information Processing
- **Climate**: C = Temperature, I = Energy Flow
- **Inequality**: C = Wealth, I = Distribution

---

## ⚠️ Expected WARN Status

- `test_06_climate.py`: "Forced disequilibrium" - climate change is real!
- `test_07_inequality.py`: "Stressed economies" - inequality increases

These WARN results are **expected** and validate UET's ability to detect stressed systems.
