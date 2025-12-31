"""
📥 Download Air Quality - Direct Station Data
=============================================

Using specific station IDs that work with demo token.
"""

import os
import urllib.request
import json
import csv
from datetime import datetime

DATA_ROOT = os.path.dirname(__file__)


def get_station_data(station_id):
    """Get data for specific station."""
    url = f"https://api.waqi.info/feed/@{station_id}/?token=demo"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode())
    except:
        return None


def main():
    print("\n" + "=" * 60)
    print("📥 AIR QUALITY - STATION DATA")
    print("=" * 60)

    output_dir = os.path.join(DATA_ROOT, "air_quality")
    os.makedirs(output_dir, exist_ok=True)

    # Known working station IDs for Thailand
    # From https://aqicn.org/map/thailand/
    stations = {
        # Bangkok area
        10564: "Bangkok - US Embassy",
        6577: "Bangkok - Din Daeng",
        6576: "Bangkok - Klong Chan",
        6580: "Bangkok - Yannawa",
        # Northern Thailand
        6695: "Chiang Mai",
        10866: "Chiang Rai",
        6700: "Lampang",
        # Other major cities
        6687: "Khon Kaen",
        6692: "Nakhon Ratchasima",
        6694: "Hat Yai",
    }

    results = []

    for station_id, name in stations.items():
        print(f"   Fetching {name} (ID: {station_id})...", end=" ")
        data = get_station_data(station_id)

        if data and data.get("status") == "ok":
            d = data["data"]
            aqi = d.get("aqi", "N/A")

            if isinstance(aqi, int) or (isinstance(aqi, str) and aqi.isdigit()):
                results.append(
                    {
                        "station_id": station_id,
                        "station_name": name,
                        "aqi": aqi,
                        "pm25": d.get("iaqi", {}).get("pm25", {}).get("v", "N/A"),
                        "pm10": d.get("iaqi", {}).get("pm10", {}).get("v", "N/A"),
                        "o3": d.get("iaqi", {}).get("o3", {}).get("v", "N/A"),
                        "temperature": d.get("iaqi", {}).get("t", {}).get("v", "N/A"),
                        "humidity": d.get("iaqi", {}).get("h", {}).get("v", "N/A"),
                        "time": d.get("time", {}).get("s", "N/A"),
                    }
                )
                print(f"✅ AQI: {aqi}")
            else:
                print(f"⚠️ No data (demo limit)")
        else:
            print("❌")

    if results:
        filepath = os.path.join(
            output_dir, f"thailand_stations_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        )
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
        print(f"\n✅ Saved: {filepath}")
        print(f"   Got {len(results)} stations with real data")
    else:
        print("\n⚠️ Demo token rate limited - try again in 1 minute")
        print("   Or get free API key from: https://aqicn.org/data-platform/token/")


if __name__ == "__main__":
    main()
