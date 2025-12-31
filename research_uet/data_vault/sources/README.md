# 📂 Real Data Sources

**ข้อมูลจริง 100% จาก Official Sources**
**Updated: 2025-12-31**

---

## 📊 Complete Data Inventory

| Category | Files | Records | Source | Status |
|:---------|:------|:--------|:-------|:-------|
| 📊 **Inequality** | 8 | 20,000+ | World Bank | ✅ NEW |
| 💰 **Economic Health** | 9 | 32,000+ | World Bank | ✅ NEW |
| 🌍 **Gapminder** | 2 | 11,000+ | Gapminder | ✅ NEW |
| 🏥 **Medical** | 4 | 430,000+ | JHU, OWID | ✅ |
| 🌍 **Climate** | 4 | 2,500+ | NASA, NOAA | ✅ |
| 🌋 **Earthquakes** | 4 | 700+ | USGS | ✅ |
| 🌌 **Grav. Waves** | 2 | 220 | LIGO | ✅ |
| 🇹🇭 **Thailand** | 4 | 11,000+ | Yahoo | ✅ |
| 🕳️ **Black Holes** | 10 | 50,000+ | SDSS | ✅ |
| 💹 **Economy** | 8 | 26,000+ | Yahoo | ✅ |
| ❤️ **Bio** | 6 | 495,000+ | PhysioNet | ✅ |
| 🧠 **Brain** | 1 | 166,800 | MNE | ✅ |
| ✨ **Galaxies** | 1 | 20 | SPARC | ✅ |
| 👥 **Social** | 3 | 20,000 | Stanford | ✅ |

**Total: 70+ files, ~1M+ records, ~600 MB**

---

## 🆕 New Economic Analysis Data

### Inequality (World Bank)
```
inequality/
├── worldbank_gini_index.csv        (2,200 records)
├── worldbank_income_top10.csv      (2,200 records)
├── worldbank_income_bottom10.csv   (2,200 records)
├── worldbank_poverty_190.csv       (2,666 records)
├── worldbank_gdp_per_capita.csv    (8,646 records)
├── worldbank_life_expectancy.csv   (7,751 records)
└── worldbank_unemployment.csv      (records)
```

### Economic Health
```
economic_health/
├── econ_private_credit_gdp.csv     (5,289 records)
├── econ_government_debt_gdp.csv    (1,203 records)
├── econ_current_account_gdp.csv    (4,243 records)
├── econ_trade_gdp.csv              (5,218 records)
├── econ_broad_money_gdp.csv        (4,692 records)
├── econ_gdp_growth.csv             (6,119 records)
├── econ_inflation.csv              (5,473 records)
└── UET_ECONOMIC_HEALTH.md          (UET formula!)
```

### Gapminder
```
gapminder/
├── gapminder_gdp_per_capita.csv    (11,182 records)
└── CITATIONS.md
```

---

## 🎯 UET Economic Health Index

Traditional ranking uses GDP. UET uses **circulation health**:

```python
k = sqrt(Productivity / Debt_Ratio) × Employment_Factor

k > 1.5  →  Very Healthy
k = 1.0  →  Balanced
k < 0.7  →  Stressed
k < 0.3  →  Crisis
```

See `economic_health/UET_ECONOMIC_HEALTH.md` for details.

---

## 📁 Full Structure

```
real_data_sources/
├── inequality/          # Gini, poverty, income
├── economic_health/     # Debt, trade, growth + UET formula
├── gapminder/           # Life expectancy, population
├── medical/             # COVID-19
├── climate/             # Temperature, CO2, sea level
├── earthquakes/         # USGS data
├── gravitational_waves/ # LIGO events
├── thailand/            # SET, THB/USD, PTT
├── black_holes/         # 50K quasars
├── economy/             # Stock markets
├── bio/                 # PhysioNet HRV
├── brain/               # EEG
├── galaxies/            # SPARC
├── social/              # Network edges
└── *.py                 # Download scripts
```

---

## 📚 Citations

Each folder has `CITATIONS.md` with BibTeX entries.

Main sources:
- World Bank Open Data
- Johns Hopkins CSSE
- NASA GISS / NOAA
- USGS / LIGO-GWOSC
- Gapminder Foundation
- PhysioNet / Stanford SNAP

---

*All data from official sources*
*Last updated: 2025-12-31*
