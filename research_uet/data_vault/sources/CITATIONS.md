# 📚 Data Sources & Citations

**เอกสารอ้างอิงข้อมูลทั้งหมดสำหรับ UET Research**

---

## ⚠️ IMPORTANT: Data Authenticity

| Dataset | Status | Source Type |
|:--------|:-------|:------------|
| Black Holes | ✅ **REAL** | Downloaded from SDSS |
| Galaxies (NGC6503) | ✅ **REAL** | Downloaded from SPARC |
| Brain (EEG) | ✅ **REAL** | Downloaded from MNE/PhysioNet |
| Economy | ⚠️ **REPRESENTATIVE** | Based on real patterns |
| Bio (HRV) | ⚠️ **REPRESENTATIVE** | Based on PhysioNet patterns |
| AI | ⚠️ **REPRESENTATIVE** | Based on published papers |
| Social | ⚠️ **REPRESENTATIVE** | Based on research patterns |

**REPRESENTATIVE = สร้างจาก real patterns แต่ไม่ใช่ raw download**

---

## 1. Black Holes (REAL DATA ✅)

### Shen 2011 Quasar Catalog
```bibtex
@article{shen2011,
  author = {Shen, Yue and Richards, Gordon T. and Strauss, Michael A. and others},
  title = {A Catalog of Quasar Properties from Sloan Digital Sky Survey Data Release 7},
  journal = {The Astrophysical Journal Supplement Series},
  volume = {194},
  number = {2},
  pages = {45},
  year = {2011},
  doi = {10.1088/0067-0049/194/2/45}
}
```
- **URL:** https://vizier.cds.unistra.fr/viz-bin/VizieR?-source=J/ApJS/194/45
- **Objects:** 105,783 quasars from SDSS DR7
- **Data:** BH masses, redshifts, luminosities

### Kormendy & Ho 2013
```bibtex
@article{kormendy2013,
  author = {Kormendy, John and Ho, Luis C.},
  title = {Coevolution (Or Not) of Supermassive Black Holes and Host Galaxies},
  journal = {Annual Review of Astronomy and Astrophysics},
  volume = {51},
  pages = {511-653},
  year = {2013},
  doi = {10.1146/annurev-astro-082708-101811}
}
```
- **Objects:** 25 nearby elliptical galaxies
- **Data:** M_BH, M_bulge relationships

### MPA-JHU Galaxy Catalog
```bibtex
@misc{mpa_jhu,
  author = {Kauffmann, Guinevere and others},
  title = {MPA-JHU DR7 Release},
  year = {2003},
  url = {https://wwwmpa.mpa-garching.mpg.de/SDSS/DR7/}
}
```
- **Data:** Galaxy stellar masses, star formation rates

---

## 2. Galaxies (REAL DATA ✅)

### SPARC Database
```bibtex
@article{lelli2016,
  author = {Lelli, Federico and McGaugh, Stacy S. and Schombert, James M.},
  title = {SPARC: Mass Models for 175 Disk Galaxies with Spitzer Photometry and Accurate Rotation Curves},
  journal = {The Astronomical Journal},
  volume = {152},
  number = {6},
  pages = {157},
  year = {2016},
  doi = {10.3847/0004-6256/152/6/157}
}
```
- **URL:** http://astroweb.cwru.edu/SPARC/
- **Galaxies:** 175 late-type galaxies
- **Data:** Rotation curves, surface photometry

---

## 3. Brain EEG (REAL DATA ✅)

### MNE-Python Sample Dataset
```bibtex
@article{gramfort2013,
  author = {Gramfort, Alexandre and others},
  title = {MEG and EEG data analysis with MNE-Python},
  journal = {Frontiers in Neuroscience},
  volume = {7},
  pages = {267},
  year = {2013},
  doi = {10.3389/fnins.2013.00267}
}
```
- **URL:** https://mne.tools/stable/documentation/datasets.html
- **Data:** Real EEG recordings

### PhysioNet (Original Source)
```bibtex
@article{goldberger2000,
  author = {Goldberger, Ary L. and others},
  title = {PhysioBank, PhysioToolkit, and PhysioNet},
  journal = {Circulation},
  volume = {101},
  number = {23},
  pages = {e215-e220},
  year = {2000},
  doi = {10.1161/01.CIR.101.23.e215}
}
```
- **URL:** https://physionet.org/

---

## 4. Economy (REPRESENTATIVE ⚠️)

### Based on Yahoo Finance Historical Data
```
Source: Yahoo Finance (https://finance.yahoo.com/)
Assets: S&P500, NASDAQ, Dow Jones, Bitcoin, Gold
Period: 2000-2024
Type: Year-end closing prices

⚠️ NOTE: These are REPRESENTATIVE values based on real historical
patterns, not raw downloads. For publication, please verify with:
- Yahoo Finance: https://finance.yahoo.com/
- FRED: https://fred.stlouisfed.org/
- Investing.com: https://www.investing.com/
```

### For Real Download, Use:
```python
# pip install yfinance
import yfinance as yf
sp500 = yf.download("^GSPC", start="2000-01-01", end="2024-12-31")
```

---

## 5. Bio HRV (REPRESENTATIVE ⚠️)

### Based on MIT-BIH Database
```bibtex
@misc{mitbih,
  author = {Moody, George B. and Mark, Roger G.},
  title = {MIT-BIH Arrhythmia Database},
  year = {1992},
  url = {https://physionet.org/content/mitdb/}
}
```

### For Real Download:
```python
# pip install wfdb
import wfdb
record = wfdb.rdrecord('mitdb/100', pn_dir='mitdb')
```
- **URL:** https://physionet.org/content/mitdb/1.0.0/

---

## 6. AI Training (REPRESENTATIVE ⚠️)

### Based on Published Training Curves
```bibtex
@article{radford2019gpt2,
  author = {Radford, Alec and others},
  title = {Language Models are Unsupervised Multitask Learners},
  journal = {OpenAI Blog},
  year = {2019},
  url = {https://openai.com/research/better-language-models}
}

@article{touvron2023llama,
  author = {Touvron, Hugo and others},
  title = {LLaMA: Open and Efficient Foundation Language Models},
  journal = {arXiv preprint arXiv:2302.13971},
  year = {2023}
}
```

### For Real Data:
- Weights & Biases: https://wandb.ai/
- TensorBoard logs from actual training runs

---

## 7. Social Network (REPRESENTATIVE ⚠️)

### Based on Research Patterns
```bibtex
@article{dunbar2016,
  author = {Dunbar, Robin I. M.},
  title = {Do online social media cut through the constraints that limit the size of offline social networks?},
  journal = {Royal Society Open Science},
  volume = {3},
  number = {1},
  pages = {150292},
  year = {2016},
  doi = {10.1098/rsos.150292}
}
```

### For Real Data:
- Twitter API: https://developer.twitter.com/
- Facebook Graph API: https://developers.facebook.com/
- Stanford SNAP: https://snap.stanford.edu/data/

---

## 📝 How to Cite in Paper

### For REAL data (Black Holes, Galaxies, Brain):
```
We used the SPARC database (Lelli et al. 2016) containing rotation
curves for 175 late-type galaxies...
```

### For REPRESENTATIVE data:
```
We generated synthetic datasets based on published patterns from
[source] to demonstrate the analysis methodology. For validation,
readers should obtain data from [original source].
```

---

## ⚠️ Recommendations for Publication

1. **Download fresh data** from original sources before publication
2. **Verify all values** against official databases
3. **Include download scripts** in supplementary materials
4. **Cite original papers** not just URLs

---

*Last updated: 2025-12-31*
