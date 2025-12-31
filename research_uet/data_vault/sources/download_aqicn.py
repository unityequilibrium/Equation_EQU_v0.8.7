"""
📥 Download Air Quality Data from AQICN (WAQI)
==============================================

Source: World Air Quality Index Project
URL: https://aqicn.org/
API: Free, token available without registration for basic data

NO API KEY REQUIRED for basic endpoints!
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
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode())
            print("✅")
            return data
    except Exception as e:
        print(f"❌ {e}")
        return None


def download_aqicn_data():
    """Download air quality from AQICN (free, no key needed for feed)."""
    print("\n" + "=" * 50)
    print("🌬️ DOWNLOADING AQICN AIR QUALITY DATA")
    print("=" * 50)

    output_dir = os.path.join(DATA_ROOT, "air_quality")
    os.makedirs(output_dir, exist_ok=True)

    # AQICN provides free JSON feeds for major cities
    # Format: https://api.waqi.info/feed/{city}/?token=demo
    # "demo" token works for basic requests

    cities = [
        # Thailand
        ("bangkok", "Bangkok", "Thailand"),
        ("chiangmai", "Chiang Mai", "Thailand"),
        ("chiangrai", "Chiang Rai", "Thailand"),
        ("phuket", "Phuket", "Thailand"),
        ("khonkaen", "Khon Kaen", "Thailand"),
        # Asia comparison
        ("beijing", "Beijing", "China"),
        ("delhi", "Delhi", "India"),
        ("tokyo", "Tokyo", "Japan"),
        ("seoul", "Seoul", "Korea"),
        ("singapore", "Singapore", "Singapore"),
        # Global reference
        ("london", "London", "UK"),
        ("newyork", "New York", "USA"),
        ("losangeles", "Los Angeles", "USA"),
        ("paris", "Paris", "France"),
        ("sydney", "Sydney", "Australia"),
    ]

    results = []

    for city_id, city_name, country in cities:
        url = f"https://api.waqi.info/feed/{city_id}/?token=demo"
        data = download_json(url, f"{city_name}")

        if data and data.get("status") == "ok":
            d = data["data"]
            results.append(
                {
                    "city": city_name,
                    "country": country,
                    "aqi": d.get("aqi", "N/A"),
                    "pm25": d.get("iaqi", {}).get("pm25", {}).get("v", "N/A"),
                    "pm10": d.get("iaqi", {}).get("pm10", {}).get("v", "N/A"),
                    "o3": d.get("iaqi", {}).get("o3", {}).get("v", "N/A"),
                    "no2": d.get("iaqi", {}).get("no2", {}).get("v", "N/A"),
                    "so2": d.get("iaqi", {}).get("so2", {}).get("v", "N/A"),
                    "co": d.get("iaqi", {}).get("co", {}).get("v", "N/A"),
                    "temperature": d.get("iaqi", {}).get("t", {}).get("v", "N/A"),
                    "humidity": d.get("iaqi", {}).get("h", {}).get("v", "N/A"),
                    "station": d.get("city", {}).get("name", "N/A"),
                    "time": d.get("time", {}).get("s", "N/A"),
                }
            )

    if results:
        # Save to CSV
        filepath = os.path.join(output_dir, f"aqicn_global_{datetime.now().strftime('%Y%m%d')}.csv")
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
        print(f"\n   ✅ Saved: {filepath}")

        # Summary
        print(f"\n📊 Air Quality Summary ({len(results)} cities):")
        print("-" * 60)

        # Sort by AQI
        sorted_results = sorted(
            results, key=lambda x: int(x["aqi"]) if str(x["aqi"]).isdigit() else 0, reverse=True
        )

        for r in sorted_results:
            aqi = r["aqi"]
            if isinstance(aqi, int) or (isinstance(aqi, str) and aqi.isdigit()):
                aqi = int(aqi)
                if aqi <= 50:
                    status = "🟢"
                elif aqi <= 100:
                    status = "🟡"
                elif aqi <= 150:
                    status = "🟠"
                elif aqi <= 200:
                    status = "🔴"
                else:
                    status = "🟣"
            else:
                status = "⚪"
                aqi = "N/A"

            pm25 = r["pm25"] if r["pm25"] != "N/A" else "-"
            print(
                f"   {status} {r['city']:15} ({r['country']:10}) AQI: {str(aqi):>4}  PM2.5: {str(pm25):>5}"
            )

    return results


def download_thailand_stations():
    """Download all Thailand monitoring stations."""
    print("\n" + "=" * 50)
    print("🇹🇭 DOWNLOADING THAILAND STATIONS")
    print("=" * 50)

    output_dir = os.path.join(DATA_ROOT, "air_quality")

    # Get Thailand map data
    url = "https://api.waqi.info/v2/map/bounds?latlng=5.5,97.5,20.5,105.5&token=demo"
    data = download_json(url, "Thailand map bounds")

    if data and data.get("status") == "ok":
        stations = data["data"]

        # Filter Thailand only (rough bounds)
        thai_stations = [
            s for s in stations if s.get("lat") and 5 < s["lat"] < 21 and 97 < s["lon"] < 106
        ]

        print(f"   Found {len(thai_stations)} stations in Thailand area")

        # Save
        filepath = os.path.join(
            output_dir, f"aqicn_thailand_stations_{datetime.now().strftime('%Y%m%d')}.json"
        )
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(thai_stations, f, indent=2, ensure_ascii=False)
        print(f"   ✅ Saved: {filepath}")

        # Also save as CSV
        if thai_stations:
            csv_path = os.path.join(
                output_dir, f"aqicn_thailand_stations_{datetime.now().strftime('%Y%m%d')}.csv"
            )
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["uid", "station", "aqi", "lat", "lon"])
                for s in thai_stations:
                    writer.writerow(
                        [
                            s.get("uid", ""),
                            s.get("station", {}).get("name", ""),
                            s.get("aqi", ""),
                            s.get("lat", ""),
                            s.get("lon", ""),
                        ]
                    )
            print(f"   ✅ Saved: {csv_path}")

        return thai_stations

    return None


def create_citations():
    """Create citations file."""
    output_dir = os.path.join(DATA_ROOT, "air_quality")

    filepath = os.path.join(output_dir, "CITATIONS.md")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(
            """# Air Quality Data Citations

## AQICN / WAQI
```bibtex
@misc{aqicn,
  author = {World Air Quality Index Project},
  title = {Real-time Air Quality Index},
  url = {https://aqicn.org/},
  note = {Data from government monitoring stations worldwide}
}
```

## Data Sources
The AQICN project aggregates data from:
- Thailand: Pollution Control Department (PCD)
- China: MEP (Ministry of Environmental Protection)
- USA: EPA AirNow
- Europe: EEA
- And many more government sources

## AQI Scale (US EPA)
| AQI | Level | Health Impact |
|:----|:------|:--------------|
| 0-50 | 🟢 Good | Air quality is satisfactory |
| 51-100 | 🟡 Moderate | Acceptable; some risk for sensitive |
| 101-150 | 🟠 Unhealthy-S | Unhealthy for sensitive groups |
| 151-200 | 🔴 Unhealthy | Everyone may experience effects |
| 201-300 | 🟣 Very Unhealthy | Health alert |
| 301-500 | ⬛ Hazardous | Emergency conditions |

## Thailand Data
- Official source: http://air4thai.pcd.go.th/
- AQICN shows real-time data from PCD stations

## Usage Notes
- Data is real-time, not historical
- For historical data, check IQAir World Air Quality Report (annual PDFs)
- Demo token has rate limits
"""
        )
    print(f"\n✅ Created: {filepath}")


def main():
    """Main download function."""
    print("\n" + "=" * 60)
    print("📥 AQICN AIR QUALITY DATA DOWNLOAD")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n⚠️ NO API KEY REQUIRED - Using public demo token")

    download_aqicn_data()
    download_thailand_stations()
    create_citations()

    print("\n" + "=" * 60)
    print("✅ DOWNLOAD COMPLETE!")
    print("=" * 60)


if __name__ == "__main__":
    main()
