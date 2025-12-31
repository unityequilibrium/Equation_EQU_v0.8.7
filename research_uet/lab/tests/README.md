# UET Test Suite

ชุดทดสอบสมการ UET กับข้อมูลจริง

## ไฟล์ทั้งหมด

| Script | สมการ | ข้อมูล |
|:-------|:------|:-------|
| `test_01_galaxies.py` | M_halo = k/√ρ | SPARC 175 galaxies |
| `test_02_brain.py` | β ≈ 2 | PhysioNet EEG |
| `test_03_economy.py` | V = C × I^k | Yahoo Finance |
| `test_04_bio.py` | dΩ/dt ≤ 0 | PhysioNet HRV |
| `test_05_medical.py` | Diffusion | COVID-19 JHU |
| `test_06_climate.py` | Forced Ω | NASA/NOAA |
| `test_07_inequality.py` | Economic k | World Bank |
| `run_all_tests.py` | **ทุกอัน** | **รันทั้งหมด** |

## วิธีใช้

### รันทีละอัน:
```bash
python test_01_galaxies.py
python test_02_brain.py
# ...
```

### รันทั้งหมด:
```bash
python run_all_tests.py
```

## Output

- `UET_VALIDATION_REPORT.md` - รายงานผล
- `results.json` - ผลลัพธ์ JSON
