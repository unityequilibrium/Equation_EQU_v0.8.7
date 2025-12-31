# IQAir Air Quality Data Guide

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
