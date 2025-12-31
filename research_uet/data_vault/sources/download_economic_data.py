"""
📥 Download Inequality, Air Quality & Economic Health Data
============================================================

Sources:
- World Bank: Gini Index, Poverty, Income Share
- OpenAQ: Air Quality (PM2.5, including Thailand)
- FRED: Economic indicators
- Gapminder: Life expectancy, population

All public APIs, no authentication needed.
"""

import os
import urllib.request
import json
import csv
from datetime import datetime

DATA_ROOT = os.path.dirname(__file__)


def download_json_api(url, description=""):
    """Download JSON from API."""
    print(f"   Downloading {description}...", end=" ")
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=60) as response:
            data = json.loads(response.read().decode())
            print("✅")
            return data
    except Exception as e:
        print(f"❌ {e}")
        return None


# =============================================================================
# WORLD BANK: Inequality Data
# =============================================================================


def download_worldbank_data():
    """Download inequality data from World Bank API."""
    print("\n" + "=" * 50)
    print("🏦 DOWNLOADING WORLD BANK DATA")
    print("=" * 50)

    output_dir = os.path.join(DATA_ROOT, "inequality")
    os.makedirs(output_dir, exist_ok=True)

    # World Bank Indicators API
    # Format: http://api.worldbank.org/v2/country/all/indicator/{indicator}?format=json&per_page=20000

    indicators = {
        "SI.POV.GINI": "gini_index",  # Gini coefficient
        "SI.DST.10TH.10": "income_top10",  # Income share top 10%
        "SI.DST.FRST.10": "income_bottom10",  # Income share bottom 10%
        "SI.POV.DDAY": "poverty_190",  # Poverty headcount $1.90/day
        "NY.GDP.PCAP.CD": "gdp_per_capita",  # GDP per capita
        "SP.DYN.LE00.IN": "life_expectancy",  # Life expectancy
        "SL.UEM.TOTL.ZS": "unemployment",  # Unemployment rate
    }

    base_url = "http://api.worldbank.org/v2/country/all/indicator"

    for indicator_code, filename in indicators.items():
        url = f"{base_url}/{indicator_code}?format=json&per_page=20000&date=1990:2023"
        data = download_json_api(url, filename)

        if data and len(data) > 1 and data[1]:
            filepath = os.path.join(output_dir, f"worldbank_{filename}.csv")
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["country_code", "country_name", "year", "value"])

                for record in data[1]:
                    if record["value"] is not None:
                        writer.writerow(
                            [
                                record["country"]["id"],
                                record["country"]["value"],
                                record["date"],
                                record["value"],
                            ]
                        )
            print(f"      → Saved {len([r for r in data[1] if r['value'] is not None])} records")

    # Create citations
    with open(os.path.join(output_dir, "CITATIONS.md"), "w", encoding="utf-8") as f:
        f.write(
            """# Inequality Data Citations

## World Bank Open Data
```bibtex
@misc{worldbank,
  author = {World Bank},
  title = {World Development Indicators},
  url = {https://data.worldbank.org/}
}
```

## Indicators Used
- SI.POV.GINI: Gini Index (0-100, higher = more inequality)
- SI.DST.10TH.10: Income share of top 10%
- SI.DST.FRST.10: Income share of bottom 10%
- SI.POV.DDAY: Poverty headcount at $1.90/day
- NY.GDP.PCAP.CD: GDP per capita (current USD)
- SP.DYN.LE00.IN: Life expectancy at birth
- SL.UEM.TOTL.ZS: Unemployment rate (% of labor force)
"""
        )
    print("   ✅ Created CITATIONS.md")


# =============================================================================
# OPENAQ: Air Quality Data
# =============================================================================


def download_openaq_data():
    """Download air quality data from OpenAQ."""
    print("\n" + "=" * 50)
    print("🌬️ DOWNLOADING AIR QUALITY DATA (OpenAQ)")
    print("=" * 50)

    output_dir = os.path.join(DATA_ROOT, "air_quality")
    os.makedirs(output_dir, exist_ok=True)

    # OpenAQ API v2
    # Get locations with PM2.5 data

    cities = [
        ("Bangkok", "TH"),
        ("Chiang Mai", "TH"),
        ("Beijing", "CN"),
        ("Delhi", "IN"),
        ("Los Angeles", "US"),
        ("London", "GB"),
    ]

    for city_name, country in cities:
        url = f"https://api.openaq.org/v2/locations?city={city_name}&country={country}&parameter=pm25&limit=10"
        data = download_json_api(url, f"{city_name} PM2.5")

        if data and "results" in data and data["results"]:
            filepath = os.path.join(
                output_dir, f"openaq_{city_name.lower().replace(' ', '_')}_locations.json"
            )
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data["results"], f, indent=2)
            print(f"      → {len(data['results'])} monitoring stations")

    # Get global country averages
    url = "https://api.openaq.org/v2/countries?limit=200"
    data = download_json_api(url, "Country Summary")

    if data and "results" in data:
        filepath = os.path.join(output_dir, "openaq_countries.csv")
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["country_code", "country_name", "locations", "measurements"])
            for country in data["results"]:
                writer.writerow(
                    [
                        country.get("code", ""),
                        country.get("name", ""),
                        country.get("locations", 0),
                        country.get("count", 0),
                    ]
                )
        print(f"      → {len(data['results'])} countries")

    # Create citations
    with open(os.path.join(output_dir, "CITATIONS.md"), "w", encoding="utf-8") as f:
        f.write(
            """# Air Quality Data Citations

## OpenAQ
```bibtex
@misc{openaq,
  author = {OpenAQ},
  title = {Open Air Quality Data},
  url = {https://openaq.org/}
}
```

## Parameters
- PM2.5: Fine particulate matter (ug/m3)
- WHO Guideline: 15 ug/m3 (annual mean)

## Thailand Data Sources
For more detailed Thailand data, check:
- Pollution Control Department: http://air4thai.pcd.go.th/
- (Note: API may be unreliable)
"""
        )
    print("   ✅ Created CITATIONS.md")


# =============================================================================
# FRED: Economic Health Indicators
# =============================================================================


def download_fred_data():
    """Download economic indicators (without API key, use alternative)."""
    print("\n" + "=" * 50)
    print("💰 DOWNLOADING ECONOMIC HEALTH DATA")
    print("=" * 50)

    output_dir = os.path.join(DATA_ROOT, "economic_health")
    os.makedirs(output_dir, exist_ok=True)

    # For FRED, we'll use World Bank as alternative (no API key needed)
    # Key economic health indicators

    indicators = {
        "FD.AST.PRVT.GD.ZS": "private_credit_gdp",  # Private credit to GDP
        "GC.DOD.TOTL.GD.ZS": "government_debt_gdp",  # Government debt to GDP
        "BN.CAB.XOKA.GD.ZS": "current_account_gdp",  # Current account balance
        "NE.TRD.GNFS.ZS": "trade_gdp",  # Trade % of GDP
        "FM.LBL.BMNY.GD.ZS": "broad_money_gdp",  # Broad money (M2) to GDP
        "NY.GDP.MKTP.KD.ZG": "gdp_growth",  # GDP growth annual %
        "FP.CPI.TOTL.ZG": "inflation",  # Inflation rate
    }

    base_url = "http://api.worldbank.org/v2/country/all/indicator"

    for indicator_code, filename in indicators.items():
        url = f"{base_url}/{indicator_code}?format=json&per_page=15000&date=2000:2023"
        data = download_json_api(url, filename)

        if data and len(data) > 1 and data[1]:
            filepath = os.path.join(output_dir, f"econ_{filename}.csv")
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["country_code", "country_name", "year", "value"])

                count = 0
                for record in data[1]:
                    if record["value"] is not None:
                        writer.writerow(
                            [
                                record["country"]["id"],
                                record["country"]["value"],
                                record["date"],
                                record["value"],
                            ]
                        )
                        count += 1
            print(f"      → Saved {count} records")

    # Create UET Economic Health formula explanation
    with open(os.path.join(output_dir, "UET_ECONOMIC_HEALTH.md"), "w", encoding="utf-8") as f:
        f.write(
            """# UET Economic Health Index

## Traditional vs UET Ranking

### Traditional GDP Ranking
```
Rank by: Total GDP or GDP per capita
Problem: Ignores debt, inequality, sustainability
```

### UET Health Index (k)
```
k = sqrt(Productivity / Debt_Ratio) × Employment_Factor

Where:
- Productivity = GDP_per_capita / Cost_of_Living
- Debt_Ratio = (Private_Debt + Gov_Debt) / GDP
- Employment_Factor = 1 - Unemployment_Rate

Interpretation:
- k > 1.5: Very Healthy (sustainable growth)
- k = 1.0: Balanced (equilibrium)  
- k < 0.7: Stressed (unsustainable)
- k < 0.3: Crisis (collapse risk)
```

## Example Calculation
```python
# Thailand 2023 (estimated)
gdp_per_capita = 7000  # USD
cost_of_living = 800   # USD/month
productivity = 7000 / (800*12)  # = 0.73

private_debt_gdp = 0.90  # 90%
gov_debt_gdp = 0.62      # 62%
debt_ratio = 0.90 + 0.62  # = 1.52

unemployment = 0.01  # 1%
employment_factor = 0.99

k = sqrt(0.73 / 1.52) * 0.99
k = 0.69  # Stressed but stable
```
"""
        )

    # Create citations
    with open(os.path.join(output_dir, "CITATIONS.md"), "w", encoding="utf-8") as f:
        f.write(
            """# Economic Health Data Citations

## World Bank
```bibtex
@misc{worldbank_wdi,
  author = {World Bank},
  title = {World Development Indicators},
  url = {https://databank.worldbank.org/source/world-development-indicators}
}
```

## Key Indicators for UET Analysis
- Private Credit to GDP: Financial system depth
- Government Debt to GDP: Fiscal sustainability
- Current Account: External balance
- Trade to GDP: Economic openness
- Inflation: Price stability
- GDP Growth: Economic momentum
"""
        )
    print("   ✅ Created CITATIONS.md and UET_ECONOMIC_HEALTH.md")


# =============================================================================
# GAPMINDER: Hans Rosling's Data
# =============================================================================


def download_gapminder_data():
    """Download Gapminder data (life expectancy, population, GDP)."""
    print("\n" + "=" * 50)
    print("🌍 DOWNLOADING GAPMINDER DATA")
    print("=" * 50)

    output_dir = os.path.join(DATA_ROOT, "gapminder")
    os.makedirs(output_dir, exist_ok=True)

    # Gapminder data is available from their GitHub
    datasets = {
        "population": "https://raw.githubusercontent.com/open-numbers/ddf--gapminder--systema_globalis/master/countries-etc-datapoints/ddf--datapoints--population_total--by--geo--time.csv",
        "life_expectancy": "https://raw.githubusercontent.com/open-numbers/ddf--gapminder--systema_globalis/master/countries-etc-datapoints/ddf--datapoints--life_expectancy_years--by--geo--time.csv",
        "gdp_per_capita": "https://raw.githubusercontent.com/open-numbers/ddf--gapminder--systema_globalis/master/countries-etc-datapoints/ddf--datapoints--gdppercapita_us_inflation_adjusted--by--geo--time.csv",
    }

    for name, url in datasets.items():
        try:
            print(f"   Downloading {name}...", end=" ")
            filepath = os.path.join(output_dir, f"gapminder_{name}.csv")
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=60) as response:
                content = response.read().decode("utf-8")
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                lines = content.count("\n")
                print(f"✅ {lines} rows")
        except Exception as e:
            print(f"❌ {e}")

    # Create citations
    with open(os.path.join(output_dir, "CITATIONS.md"), "w", encoding="utf-8") as f:
        f.write(
            """# Gapminder Data Citations

## Gapminder Foundation
```bibtex
@misc{gapminder,
  author = {Gapminder Foundation},
  title = {Gapminder Data},
  url = {https://www.gapminder.org/data/}
}
```

## Hans Rosling
```bibtex
@book{rosling2018factfulness,
  author = {Rosling, Hans and Rosling, Ola and Rosling Ronnlund, Anna},
  title = {Factfulness: Ten Reasons We're Wrong About the World},
  year = {2018},
  publisher = {Flatiron Books}
}
```

## Datasets
- Population: Total population by country
- Life Expectancy: Years at birth
- GDP per capita: Inflation-adjusted USD
"""
        )
    print("   ✅ Created CITATIONS.md")


# =============================================================================
# MAIN
# =============================================================================


def download_all_economic():
    """Download all economic and inequality data."""
    print("\n" + "=" * 60)
    print("📥 DOWNLOADING INEQUALITY & ECONOMIC HEALTH DATA")
    print("=" * 60)
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    download_worldbank_data()
    download_openaq_data()
    download_fred_data()
    download_gapminder_data()

    print("\n" + "=" * 60)
    print("✅ ALL DOWNLOADS COMPLETE!")
    print("=" * 60)
    print("\nNew categories added:")
    print("  📊 inequality/      - Gini, poverty, income shares")
    print("  🌬️ air_quality/    - PM2.5, OpenAQ data")
    print("  💰 economic_health/ - Debt, trade, growth indicators")
    print("  🌍 gapminder/       - Life expectancy, population")


if __name__ == "__main__":
    download_all_economic()
