"""
📥 Download IQAir Air Quality Data
===================================

IQAir provides real-time air quality data for Thailand provinces.

REQUIRES API KEY (Free tier available):
1. Go to: https://www.iqair.com/th-en/dashboard/api
2. Create free account
3. Get API key
4. Set below: IQAIR_API_KEY = "your-key-here"

Free tier: 10,000 calls/month
"""

import os
import urllib.request
import json
import csv
from datetime import datetime

DATA_ROOT = os.path.dirname(__file__)

# =============================================================================
# SET YOUR API KEY HERE
# =============================================================================
IQAIR_API_KEY = ""  # Get from https://www.iqair.com/dashboard/api
# =============================================================================


def get_iqair_data(endpoint, params=""):
    """Call IQAir API."""
    if not IQAIR_API_KEY:
        return None

    base_url = "http://api.airvisual.com/v2"
    url = f"{base_url}/{endpoint}?key={IQAIR_API_KEY}{params}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"   ❌ {e}")
        return None


def download_thailand_provinces():
    """Download air quality for Thailand provinces/cities."""
    print("\n" + "=" * 50)
    print("🌬️ DOWNLOADING IQAIR THAILAND DATA")
    print("=" * 50)

    if not IQAIR_API_KEY:
        print("\n❌ API KEY REQUIRED!")
        print("   1. Go to: https://www.iqair.com/th-en/dashboard/api")
        print("   2. Create free account")
        print("   3. Get API key")
        print("   4. Edit this file and set IQAIR_API_KEY")
        return False

    output_dir = os.path.join(DATA_ROOT, "air_quality")
    os.makedirs(output_dir, exist_ok=True)

    # Thailand cities with monitoring stations
    thailand_cities = [
        ("Bangkok", "Bangkok"),
        ("Chiang Mai", "Chiang Mai"),
        ("Chiang Rai", "Chiang Rai"),
        ("Phuket", "Phuket"),
        ("Khon Kaen", "Khon Kaen"),
        ("Hat Yai", "Songkhla"),
        ("Nakhon Ratchasima", "Nakhon Ratchasima"),
        ("Udon Thani", "Udon Thani"),
        ("Pattaya", "Chon Buri"),
        ("Lampang", "Lampang"),
    ]

    results = []

    for city, state in thailand_cities:
        print(f"   Fetching {city}...", end=" ")
        data = get_iqair_data("city", f"&city={city}&state={state}&country=Thailand")

        if data and data.get("status") == "success":
            pollution = data["data"]["current"]["pollution"]
            weather = data["data"]["current"]["weather"]

            results.append(
                {
                    "city": city,
                    "state": state,
                    "aqi_us": pollution.get("aqius", "N/A"),
                    "main_pollutant": pollution.get("mainus", "N/A"),
                    "pm25": pollution.get("p2", {}).get("conc", "N/A"),
                    "temperature": weather.get("tp", "N/A"),
                    "humidity": weather.get("hu", "N/A"),
                    "timestamp": pollution.get("ts", "N/A"),
                }
            )
            print(f"✅ AQI={pollution.get('aqius', 'N/A')}")
        else:
            print("❌")

    if results:
        # Save to CSV
        filepath = os.path.join(
            output_dir, f"iqair_thailand_{datetime.now().strftime('%Y%m%d')}.csv"
        )
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
        print(f"\n   ✅ Saved: {filepath}")

        # Summary
        print(f"\n📊 Summary ({len(results)} cities):")
        for r in sorted(
            results, key=lambda x: x["aqi_us"] if isinstance(x["aqi_us"], int) else 0, reverse=True
        ):
            aqi = r["aqi_us"]
            status = (
                "🟢 Good"
                if aqi <= 50
                else (
                    "🟡 Moderate"
                    if aqi <= 100
                    else "🟠 Unhealthy-S" if aqi <= 150 else "🔴 Unhealthy"
                )
            )
            print(f"      {r['city']:20} AQI: {aqi:3} {status}")

    return True


def download_world_ranking():
    """Get world's most polluted cities."""
    print("\n" + "=" * 50)
    print("🌍 DOWNLOADING WORLD POLLUTION RANKING")
    print("=" * 50)

    if not IQAIR_API_KEY:
        print("   ❌ Skipped (no API key)")
        return False

    output_dir = os.path.join(DATA_ROOT, "air_quality")
    os.makedirs(output_dir, exist_ok=True)

    # Get ranking (requires paid API for full list, free gives sample)
    print("   Note: Full ranking requires paid API tier")
    print("   Free tier shows sample cities")

    # Alternative: Use countries endpoint
    print("   Fetching supported countries...", end=" ")
    data = get_iqair_data("countries")

    if data and data.get("status") == "success":
        countries = data["data"]
        print(f"✅ {len(countries)} countries")

        filepath = os.path.join(output_dir, "iqair_countries.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(countries, f, indent=2)

    return True


def create_manual_guide():
    """Create guide for manual data download."""
    output_dir = os.path.join(DATA_ROOT, "air_quality")
    os.makedirs(output_dir, exist_ok=True)

    guide_path = os.path.join(output_dir, "IQAIR_GUIDE.md")
    with open(guide_path, "w", encoding="utf-8") as f:
        f.write(
            """# IQAir Air Quality Data Guide

## Getting API Key (Free)

1. Go to: https://www.iqair.com/th-en/dashboard/api
2. Click "Get Started"
3. Create account (email verification required)
4. Get your API key
5. Free tier: 10,000 calls/month

## API Endpoints

### Get City Data
```
GET http://api.airvisual.com/v2/city?city=Bangkok&state=Bangkok&country=Thailand&key=YOUR_KEY
```

### Get States in Country
```
GET http://api.airvisual.com/v2/states?country=Thailand&key=YOUR_KEY
```

### Get Cities in State
```
GET http://api.airvisual.com/v2/cities?state=Bangkok&country=Thailand&key=YOUR_KEY
```

## Alternative: Manual Download

If API doesn't work, you can manually get data from:

1. **IQAir Website**: https://www.iqair.com/thailand
   - Historical data available
   - Province breakdown

2. **AQICN**: https://aqicn.org/map/thailand/
   - Real-time monitoring
   - Historical available

3. **Air4Thai**: http://air4thai.pcd.go.th/
   - Official Thai government data
   - API unreliable but web data available

## Thailand Provinces with Monitoring

Top pollution areas (winter season):
1. Chiang Mai - Northern burning season
2. Chiang Rai - Northern burning season  
3. Lampang - Industrial + burning
4. Bangkok - Traffic + industry
5. Samut Prakan - Industrial

## Data Fields

| Field | Description |
|:------|:------------|
| aqius | US EPA AQI (0-500) |
| aqicn | China AQI |
| mainus | Main pollutant (p2=PM2.5, p1=PM10, etc) |
| p2 | PM2.5 concentration (ug/m3) |
| tp | Temperature (Celsius) |
| hu | Humidity (%) |
| ws | Wind speed (m/s) |

## AQI Scale

| AQI | Level | Health |
|:----|:------|:-------|
| 0-50 | 🟢 Good | Satisfactory |
| 51-100 | 🟡 Moderate | Acceptable |
| 101-150 | 🟠 Unhealthy for Sensitive | Risk for sensitive groups |
| 151-200 | 🔴 Unhealthy | Everyone may feel effects |
| 201-300 | 🟣 Very Unhealthy | Health alert |
| 301-500 | ⬛ Hazardous | Emergency |

## Citation

```bibtex
@misc{iqair,
  author = {IQAir},
  title = {World Air Quality Report},
  url = {https://www.iqair.com/}
}
```
"""
        )
    print(f"\n✅ Created: {guide_path}")


def main():
    """Main download function."""
    print("\n" + "=" * 60)
    print("📥 IQAIR AIR QUALITY DATA DOWNLOAD")
    print("=" * 60)
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Always create guide
    create_manual_guide()

    if IQAIR_API_KEY:
        download_thailand_provinces()
        download_world_ranking()
        print("\n✅ Download complete!")
    else:
        print("\n" + "=" * 50)
        print("⚠️ NO API KEY SET")
        print("=" * 50)
        print("\nTo download data:")
        print("1. Get free API key from: https://www.iqair.com/th-en/dashboard/api")
        print("2. Edit this file")
        print("3. Set IQAIR_API_KEY = 'your-key-here'")
        print("4. Run again")
        print("\nAlternatively, see IQAIR_GUIDE.md for manual download options.")


if __name__ == "__main__":
    main()
