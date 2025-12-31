"""
📥 Download Additional Real Data
================================

Downloads:
- Medical: COVID-19 (Johns Hopkins, Our World in Data)
- Climate: Temperature (NASA), CO2 (NOAA)
- Earthquakes: USGS
- Gravitational Waves: LIGO
- Thailand: SET Index
- Crypto: Bitcoin, Ethereum prices

All from official public APIs.
"""

import os
import urllib.request
import json
import csv
from datetime import datetime

DATA_ROOT = os.path.dirname(__file__)


def download_json(url, description=""):
    """Download JSON from URL."""
    print(f"   Downloading {description}...", end=" ")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as response:
            data = json.loads(response.read().decode())
            print("✅")
            return data
    except Exception as e:
        print(f"❌ {e}")
        return None


def download_csv_url(url, filepath, description=""):
    """Download CSV from URL."""
    print(f"   Downloading {description}...", end=" ")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as response:
            content = response.read().decode("utf-8")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            lines = content.count("\n")
            print(f"✅ {lines} rows")
            return True
    except Exception as e:
        print(f"❌ {e}")
        return False


# =============================================================================
# MEDICAL: COVID-19
# =============================================================================


def download_medical_data():
    """Download COVID-19 and medical data."""
    print("\n" + "=" * 50)
    print("🏥 DOWNLOADING MEDICAL DATA")
    print("=" * 50)

    output_dir = os.path.join(DATA_ROOT, "medical")
    os.makedirs(output_dir, exist_ok=True)

    # Our World in Data - COVID-19 (Best maintained dataset)
    owid_url = "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv"
    owid_path = os.path.join(output_dir, "covid19_owid_global.csv")
    download_csv_url(owid_url, owid_path, "COVID-19 Global (OWID)")

    # Johns Hopkins - Time series
    jhu_deaths = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"
    jhu_cases = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"

    download_csv_url(
        jhu_deaths, os.path.join(output_dir, "covid19_jhu_deaths.csv"), "COVID-19 Deaths (JHU)"
    )
    download_csv_url(
        jhu_cases, os.path.join(output_dir, "covid19_jhu_cases.csv"), "COVID-19 Cases (JHU)"
    )

    # Create citations file
    with open(os.path.join(output_dir, "CITATIONS.md"), "w") as f:
        f.write(
            """# Medical Data Citations

## COVID-19 Data

### Our World in Data
```bibtex
@misc{owid2020,
  author = {Ritchie, Hannah and others},
  title = {Coronavirus Pandemic (COVID-19)},
  year = {2020},
  url = {https://ourworldindata.org/coronavirus}
}
```

### Johns Hopkins CSSE
```bibtex
@article{dong2020,
  author = {Dong, Ensheng and Du, Hongru and Gardner, Lauren},
  title = {An interactive web-based dashboard to track COVID-19 in real time},
  journal = {The Lancet Infectious Diseases},
  volume = {20},
  number = {5},
  pages = {533-534},
  year = {2020},
  doi = {10.1016/S1473-3099(20)30120-1}
}
```
"""
        )
    print("   ✅ Created CITATIONS.md")


# =============================================================================
# CLIMATE: NASA, NOAA
# =============================================================================


def download_climate_data():
    """Download climate/environment data."""
    print("\n" + "=" * 50)
    print("🌍 DOWNLOADING CLIMATE DATA")
    print("=" * 50)

    output_dir = os.path.join(DATA_ROOT, "climate")
    os.makedirs(output_dir, exist_ok=True)

    # NASA GISS Global Temperature
    nasa_url = "https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv"
    download_csv_url(
        nasa_url, os.path.join(output_dir, "nasa_global_temperature.csv"), "NASA Global Temperature"
    )

    # NOAA CO2 (Mauna Loa)
    noaa_co2 = "https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_mm_mlo.csv"
    download_csv_url(
        noaa_co2, os.path.join(output_dir, "noaa_co2_mauna_loa.csv"), "NOAA CO2 Mauna Loa"
    )

    # NOAA Sea Level
    noaa_sea = (
        "https://www.star.nesdis.noaa.gov/socd/lsa/SeaLevelRise/slr/slr_sla_gbl_keep_all_66.csv"
    )
    download_csv_url(noaa_sea, os.path.join(output_dir, "noaa_sea_level.csv"), "NOAA Sea Level")

    # Create citations
    with open(os.path.join(output_dir, "CITATIONS.md"), "w") as f:
        f.write(
            """# Climate Data Citations

## NASA GISS Temperature
```bibtex
@misc{nasa_giss,
  author = {NASA Goddard Institute for Space Studies},
  title = {GISS Surface Temperature Analysis (GISTEMP v4)},
  url = {https://data.giss.nasa.gov/gistemp/}
}
```

## NOAA CO2
```bibtex
@misc{noaa_co2,
  author = {NOAA Global Monitoring Laboratory},
  title = {Trends in Atmospheric Carbon Dioxide},
  url = {https://gml.noaa.gov/ccgg/trends/}
}
```
"""
        )
    print("   ✅ Created CITATIONS.md")


# =============================================================================
# EARTHQUAKES: USGS
# =============================================================================


def download_earthquake_data():
    """Download earthquake data from USGS."""
    print("\n" + "=" * 50)
    print("🌋 DOWNLOADING EARTHQUAKE DATA")
    print("=" * 50)

    output_dir = os.path.join(DATA_ROOT, "earthquakes")
    os.makedirs(output_dir, exist_ok=True)

    # USGS Significant Earthquakes (past 30 days)
    usgs_url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_month.csv"
    download_csv_url(
        usgs_url,
        os.path.join(output_dir, "usgs_significant_30days.csv"),
        "USGS Significant (30 days)",
    )

    # USGS All M4.5+ (past 30 days)
    usgs_m45 = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_month.csv"
    download_csv_url(
        usgs_m45, os.path.join(output_dir, "usgs_m45_30days.csv"), "USGS M4.5+ (30 days)"
    )

    # USGS All M2.5+ (past 7 days)
    usgs_m25 = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_week.csv"
    download_csv_url(
        usgs_m25, os.path.join(output_dir, "usgs_m25_7days.csv"), "USGS M2.5+ (7 days)"
    )

    # Create citations
    with open(os.path.join(output_dir, "CITATIONS.md"), "w") as f:
        f.write(
            """# Earthquake Data Citations

## USGS Earthquake Hazards Program
```bibtex
@misc{usgs_earthquakes,
  author = {U.S. Geological Survey},
  title = {Earthquake Hazards Program},
  url = {https://earthquake.usgs.gov/}
}
```
"""
        )
    print("   ✅ Created CITATIONS.md")


# =============================================================================
# GRAVITATIONAL WAVES: LIGO
# =============================================================================


def download_gw_data():
    """Download gravitational wave event catalog."""
    print("\n" + "=" * 50)
    print("🌌 DOWNLOADING GRAVITATIONAL WAVE DATA")
    print("=" * 50)

    output_dir = os.path.join(DATA_ROOT, "gravitational_waves")
    os.makedirs(output_dir, exist_ok=True)

    # GWTC-3 Catalog (all confirmed events)
    gwtc_url = "https://gwosc.org/eventapi/csv/GWTC/"
    download_csv_url(gwtc_url, os.path.join(output_dir, "gwtc_all_events.csv"), "GWTC All Events")

    # Create citations
    with open(os.path.join(output_dir, "CITATIONS.md"), "w") as f:
        f.write(
            """# Gravitational Wave Data Citations

## GWTC Catalog
```bibtex
@article{gwtc3,
  author = {Abbott, R. and others},
  title = {GWTC-3: Compact Binary Coalescences Observed by LIGO and Virgo During the Second Part of the Third Observing Run},
  journal = {Physical Review X},
  volume = {13},
  pages = {041039},
  year = {2023},
  doi = {10.1103/PhysRevX.13.041039}
}
```

## GWOSC
```bibtex
@misc{gwosc,
  author = {LIGO Scientific Collaboration and Virgo Collaboration and KAGRA Collaboration},
  title = {Gravitational Wave Open Science Center},
  url = {https://gwosc.org/}
}
```
"""
        )
    print("   ✅ Created CITATIONS.md")


# =============================================================================
# THAILAND: SET Index
# =============================================================================


def download_thailand_data():
    """Download Thailand-specific data."""
    print("\n" + "=" * 50)
    print("🇹🇭 DOWNLOADING THAILAND DATA")
    print("=" * 50)

    output_dir = os.path.join(DATA_ROOT, "thailand")
    os.makedirs(output_dir, exist_ok=True)

    try:
        import yfinance as yf

        # SET Index
        print("   Downloading SET Index...", end=" ")
        set_data = yf.download("^SET.BK", start="2010-01-01", end="2024-12-31", progress=False)
        if len(set_data) > 0:
            set_data.to_csv(os.path.join(output_dir, "SET_index_yahoo.csv"))
            print(f"✅ {len(set_data)} days")

        # PTT (largest Thai company)
        print("   Downloading PTT...", end=" ")
        ptt_data = yf.download("PTT.BK", start="2010-01-01", end="2024-12-31", progress=False)
        if len(ptt_data) > 0:
            ptt_data.to_csv(os.path.join(output_dir, "PTT_stock_yahoo.csv"))
            print(f"✅ {len(ptt_data)} days")

        # Thai Baht / USD
        print("   Downloading THB/USD...", end=" ")
        thb_data = yf.download("THB=X", start="2010-01-01", end="2024-12-31", progress=False)
        if len(thb_data) > 0:
            thb_data.to_csv(os.path.join(output_dir, "THB_USD_yahoo.csv"))
            print(f"✅ {len(thb_data)} days")

    except ImportError:
        print("   ❌ Need: pip install yfinance")

    # Create info file for manual data
    with open(os.path.join(output_dir, "MANUAL_SOURCES.md"), "w", encoding="utf-8") as f:
        f.write(
            """# Thailand Manual Data Sources

## Official Government Data
- **data.go.th** - Open Government Data Portal
  - COVID-19 Thailand
  - Population statistics
  - Economic indicators
  
- **National Statistical Office (NSO)**
  - https://www.nso.go.th/
  
- **Department of Disease Control (DDC)**
  - https://ddc.moph.go.th/
  
- **Bank of Thailand (BOT)**
  - https://www.bot.or.th/
  
## Stock Data
- Downloaded SET Index from Yahoo Finance
- For detailed data, use SET website: https://www.set.or.th/
"""
        )
    print("   ✅ Created MANUAL_SOURCES.md")


# =============================================================================
# CRYPTO
# =============================================================================


def download_crypto_data():
    """Download cryptocurrency data."""
    print("\n" + "=" * 50)
    print("🪙 DOWNLOADING CRYPTO DATA")
    print("=" * 50)

    output_dir = os.path.join(DATA_ROOT, "crypto")
    os.makedirs(output_dir, exist_ok=True)

    # CoinGecko API (free, no key needed)
    coins = {
        "bitcoin": "bitcoin",
        "ethereum": "ethereum",
        "binancecoin": "bnb",
    }

    for coin_id, name in coins.items():
        try:
            print(f"   Downloading {name}...", end=" ")
            url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days=max"
            data = download_json(url, "")

            if data and "prices" in data:
                filepath = os.path.join(output_dir, f"{name}_coingecko.csv")
                with open(filepath, "w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(["timestamp", "price_usd"])
                    for point in data["prices"]:
                        ts = datetime.fromtimestamp(point[0] / 1000).strftime("%Y-%m-%d")
                        writer.writerow([ts, point[1]])
                print(f"✅ {len(data['prices'])} days")
        except Exception as e:
            print(f"❌ {e}")

    # Create citations
    with open(os.path.join(output_dir, "CITATIONS.md"), "w") as f:
        f.write(
            """# Crypto Data Citations

## CoinGecko
```bibtex
@misc{coingecko,
  author = {CoinGecko},
  title = {Cryptocurrency Prices, Charts and Market Capitalizations},
  url = {https://www.coingecko.com/}
}
```
"""
        )


# =============================================================================
# MAIN
# =============================================================================


def download_all_additional():
    """Download all additional datasets."""
    print("\n" + "=" * 60)
    print("📥 DOWNLOADING ADDITIONAL REAL DATA")
    print("=" * 60)
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    download_medical_data()
    download_climate_data()
    download_earthquake_data()
    download_gw_data()
    download_thailand_data()
    download_crypto_data()

    print("\n" + "=" * 60)
    print("✅ ALL DOWNLOADS COMPLETE!")
    print("=" * 60)
    print("\nNew categories added:")
    print("  🏥 medical/     - COVID-19 global data")
    print("  🌍 climate/     - NASA temperature, NOAA CO2")
    print("  🌋 earthquakes/ - USGS earthquake data")
    print("  🌌 gravitational_waves/ - LIGO/Virgo events")
    print("  🇹🇭 thailand/   - SET Index, THB/USD")
    print("  🪙 crypto/      - Bitcoin, Ethereum prices")


if __name__ == "__main__":
    download_all_additional()
