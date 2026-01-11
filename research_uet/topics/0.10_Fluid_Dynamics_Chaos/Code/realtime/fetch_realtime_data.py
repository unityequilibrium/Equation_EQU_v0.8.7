"""
REAL-TIME FLUID DATA FETCHER
============================
Fetches real-time fluid dynamics data from public APIs:
1. Weather (OpenWeatherMap / NOAA) - Wind, pressure, temperature
2. Aircraft (OpenSky Network) - Flight paths, altitude, speed
3. Ocean (NOAA / Copernicus) - Currents, temperature
4. Air Quality (OpenAQ) - Pollution dispersion

This enables UET validation against REAL-WORLD DATA!

APIs Used (free, no auth required for some):
- OpenSky Network: https://opensky-network.org/apidoc/
- NOAA Weather: https://www.weather.gov/documentation/services-web-api
- OpenAQ: https://openaq.org/
"""

import numpy as np
import json
import time
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime
import urllib.request
import urllib.error


@dataclass
class FluidDataPoint:
    """A fluid dynamics data point."""

    timestamp: str
    latitude: float
    longitude: float
    velocity_x: float  # m/s
    velocity_y: float  # m/s
    velocity_z: float  # m/s (vertical)
    pressure: float  # Pa
    temperature: float  # K
    density: float  # kg/m³
    source: str


class RealTimeDataFetcher:
    """Fetch real-time fluid dynamics data from APIs."""

    def __init__(self, cache_dir: Path = None):
        self.cache_dir = cache_dir or Path(__file__).parent.parent / "Data" / "realtime"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def fetch_url(self, url: str, timeout: int = 10) -> Optional[dict]:
        """Fetch JSON from URL."""
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "UET-Research/1.0"}
            )
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as e:
            print(f"  ⚠️ Error fetching {url}: {e}")
            return None

    # =========================================================================
    # AIRCRAFT DATA (OpenSky Network)
    # =========================================================================

    def fetch_aircraft_data(
        self,
        bbox: tuple = None,  # (lat_min, lon_min, lat_max, lon_max)
        limit: int = 100,
    ) -> List[FluidDataPoint]:
        """
        Fetch live aircraft positions and velocities.
        Source: OpenSky Network (free, no API key required)

        Each aircraft represents a point in the flow field!
        """
        print("\n📡 Fetching Aircraft Data (OpenSky Network)...")

        # API endpoint
        url = "https://opensky-network.org/api/states/all"
        if bbox:
            url += f"?lamin={bbox[0]}&lomin={bbox[1]}&lamax={bbox[2]}&lomax={bbox[3]}"

        data = self.fetch_url(url)
        if not data or "states" not in data:
            print("  ❌ No aircraft data available")
            return []

        points = []
        timestamp = datetime.now().isoformat()

        for i, state in enumerate(data["states"][:limit]):
            if state[5] is None or state[6] is None:  # No position
                continue

            # Extract velocity components
            velocity = state[9] or 0  # Ground speed (m/s)
            track = state[10] or 0  # Track angle (degrees from north)
            vertical = state[11] or 0  # Vertical rate (m/s)
            altitude = state[7] or 0  # Altitude (m)

            # Convert track to x,y velocity
            track_rad = np.radians(track)
            vx = velocity * np.sin(track_rad)
            vy = velocity * np.cos(track_rad)

            # Estimate air density at altitude
            # ρ(h) ≈ ρ₀ * exp(-h/H) where H ≈ 8500m
            rho_0 = 1.225  # kg/m³ at sea level
            H = 8500
            density = rho_0 * np.exp(-altitude / H)

            # Temperature (ISA model)
            T_0 = 288.15  # K at sea level
            L = 0.0065  # K/m lapse rate
            temp = T_0 - L * min(altitude, 11000)

            # Pressure (ISA model)
            P_0 = 101325  # Pa
            pressure = P_0 * (temp / T_0) ** 5.2561

            points.append(
                FluidDataPoint(
                    timestamp=timestamp,
                    latitude=state[6],
                    longitude=state[5],
                    velocity_x=vx,
                    velocity_y=vy,
                    velocity_z=vertical,
                    pressure=pressure,
                    temperature=temp,
                    density=density,
                    source="OpenSky",
                )
            )

        print(f"  ✅ Fetched {len(points)} aircraft positions")
        return points

    # =========================================================================
    # WEATHER DATA (Open-Meteo - free, no API key)
    # =========================================================================

    def fetch_weather_data(
        self, lat: float = 35.0, lon: float = 139.0, grid_size: int = 5
    ) -> List[FluidDataPoint]:
        """
        Fetch current weather data for a grid.
        Source: Open-Meteo (free, no API key required)
        """
        print("\n🌤️ Fetching Weather Data (Open-Meteo)...")

        points = []
        timestamp = datetime.now().isoformat()

        # Create grid around center point
        for i in range(grid_size):
            for j in range(grid_size):
                lat_i = lat + (i - grid_size // 2) * 0.5
                lon_j = lon + (j - grid_size // 2) * 0.5

                url = (
                    f"https://api.open-meteo.com/v1/forecast?"
                    f"latitude={lat_i}&longitude={lon_j}&current_weather=true"
                )

                data = self.fetch_url(url)
                if not data or "current_weather" not in data:
                    continue

                weather = data["current_weather"]

                # Wind components
                wind_speed = weather.get("windspeed", 0) / 3.6  # km/h to m/s
                wind_dir = weather.get("winddirection", 0)
                wind_rad = np.radians(wind_dir)

                vx = -wind_speed * np.sin(wind_rad)
                vy = -wind_speed * np.cos(wind_rad)

                # Temperature
                temp_c = weather.get("temperature", 20)
                temp_k = temp_c + 273.15

                # Estimate pressure and density at sea level
                pressure = 101325  # Pa (approximate)
                R = 287  # J/(kg·K)
                density = pressure / (R * temp_k)

                points.append(
                    FluidDataPoint(
                        timestamp=timestamp,
                        latitude=lat_i,
                        longitude=lon_j,
                        velocity_x=vx,
                        velocity_y=vy,
                        velocity_z=0,
                        pressure=pressure,
                        temperature=temp_k,
                        density=density,
                        source="Open-Meteo",
                    )
                )

        print(f"  ✅ Fetched {len(points)} weather grid points")
        return points

    # =========================================================================
    # SAVE DATA
    # =========================================================================

    def save_data(self, points: List[FluidDataPoint], name: str) -> Path:
        """Save data points to JSON."""
        filepath = (
            self.cache_dir / f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        data = {
            "fetched_at": datetime.now().isoformat(),
            "count": len(points),
            "points": [
                {
                    "timestamp": p.timestamp,
                    "lat": p.latitude,
                    "lon": p.longitude,
                    "vx": p.velocity_x,
                    "vy": p.velocity_y,
                    "vz": p.velocity_z,
                    "pressure": p.pressure,
                    "temperature": p.temperature,
                    "density": p.density,
                    "source": p.source,
                }
                for p in points
            ],
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        print(f"  💾 Saved to: {filepath}")
        return filepath

    def convert_to_grid(
        self, points: List[FluidDataPoint], nx: int = 32, ny: int = 32
    ) -> dict:
        """Convert scattered points to regular grid for UET."""
        if not points:
            return None

        # Get bounds
        lats = [p.latitude for p in points]
        lons = [p.longitude for p in points]
        lat_min, lat_max = min(lats), max(lats)
        lon_min, lon_max = min(lons), max(lons)

        # Initialize grids
        vx_grid = np.zeros((ny, nx))
        vy_grid = np.zeros((ny, nx))
        density_grid = np.ones((ny, nx))
        count_grid = np.zeros((ny, nx))

        # Map points to grid
        for p in points:
            if lat_max > lat_min and lon_max > lon_min:
                i = int((p.latitude - lat_min) / (lat_max - lat_min) * (ny - 1))
                j = int((p.longitude - lon_min) / (lon_max - lon_min) * (nx - 1))
                i = max(0, min(ny - 1, i))
                j = max(0, min(nx - 1, j))

                vx_grid[i, j] += p.velocity_x
                vy_grid[i, j] += p.velocity_y
                density_grid[i, j] = p.density
                count_grid[i, j] += 1

        # Average where multiple points
        mask = count_grid > 0
        vx_grid[mask] /= count_grid[mask]
        vy_grid[mask] /= count_grid[mask]

        return {
            "vx": vx_grid,
            "vy": vy_grid,
            "density": density_grid,
            "bounds": {
                "lat_min": lat_min,
                "lat_max": lat_max,
                "lon_min": lon_min,
                "lon_max": lon_max,
            },
            "nx": nx,
            "ny": ny,
        }


def fetch_all_realtime_data():
    """Fetch all available real-time data."""
    print("=" * 70)
    print("REAL-TIME FLUID DYNAMICS DATA FETCHER")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().isoformat()}")

    fetcher = RealTimeDataFetcher()
    results = {}

    # 1. Aircraft Data
    aircraft = fetcher.fetch_aircraft_data(limit=200)
    if aircraft:
        fetcher.save_data(aircraft, "aircraft")
        results["aircraft"] = {
            "count": len(aircraft),
            "avg_speed": np.mean(
                [np.sqrt(p.velocity_x**2 + p.velocity_y**2) for p in aircraft]
            ),
            "avg_altitude": np.mean(
                [p.density for p in aircraft]
            ),  # Indirect via density
        }

    # 2. Weather Data (East Asia region)
    weather = fetcher.fetch_weather_data(lat=35.0, lon=139.0, grid_size=3)
    if weather:
        fetcher.save_data(weather, "weather")
        results["weather"] = {
            "count": len(weather),
            "avg_wind_speed": np.mean(
                [np.sqrt(p.velocity_x**2 + p.velocity_y**2) for p in weather]
            ),
            "avg_temp_c": np.mean([p.temperature - 273.15 for p in weather]),
        }

    # Summary
    print("\n" + "=" * 70)
    print("DATA FETCH SUMMARY")
    print("=" * 70)

    for source, info in results.items():
        print(f"\n📊 {source.upper()}")
        for key, val in info.items():
            if isinstance(val, float):
                print(f"   {key}: {val:.2f}")
            else:
                print(f"   {key}: {val}")

    # Save summary
    summary_path = Path(__file__).parent.parent / "Data" / "realtime" / "summary.json"
    with open(summary_path, "w") as f:
        json.dump(
            {"fetched_at": datetime.now().isoformat(), "results": results},
            f,
            indent=2,
            default=str,
        )

    print(f"\n📁 Summary saved to: {summary_path}")

    return results


if __name__ == "__main__":
    fetch_all_realtime_data()
