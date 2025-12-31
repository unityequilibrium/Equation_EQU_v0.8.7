# 🌬️ Air Quality Data - How to Get REAL Data

## Problem
Demo token ให้ข้อมูลเหมือนกันหมด (rate limited)

## Solution: Get FREE API Token (5 minutes)

### Step 1: Go to AQICN Token Page
```
https://aqicn.org/data-platform/token/
```

### Step 2: Fill Form
- Email: your email
- Project: "Research project" or "Personal use"
- Submit

### Step 3: Check Email
- Token sent immediately
- Format: `xxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

### Step 4: Use Token
Edit `download_air_stations.py`:
```python
# Change this line:
url = f"https://api.waqi.info/feed/@{station_id}/?token=YOUR_TOKEN_HERE"
```

Or create environment variable:
```powershell
$env:AQICN_TOKEN = "your-token-here"
```

---

## Alternative: Manual Download

### AQICN Website
1. Go to: https://aqicn.org/map/thailand/
2. Click on any station
3. See real-time data

### Air4Thai (Official Thai Gov)
1. Go to: http://air4thai.pcd.go.th/webV3/
2. Data available but API unreliable
3. Can download CSV manually

### IQAir Historical Reports
1. Go to: https://www.iqair.com/world-air-quality-report
2. Download annual PDF reports
3. Has country/city rankings

---

## Current Data Files

We have stations listed, just need real AQI values:

```
air_quality/
├── thailand_stations_*.csv    (10 stations, demo data)
├── aqicn_global_*.csv         (global cities, demo data)  
├── CITATIONS.md               (references)
└── IQAIR_GUIDE.md             (this file)
```

---

## Thailand Monitoring Stations

| Station ID | Location |
|:-----------|:---------|
| 10564 | Bangkok - US Embassy |
| 6577 | Bangkok - Din Daeng |
| 6576 | Bangkok - Klong Chan |
| 6580 | Bangkok - Yannawa |
| 6695 | Chiang Mai |
| 10866 | Chiang Rai |
| 6700 | Lampang |
| 6687 | Khon Kaen |
| 6692 | Nakhon Ratchasima |
| 6694 | Hat Yai |

---

## Citation

```bibtex
@misc{aqicn,
  author = {World Air Quality Index Project},
  title = {Real-time Air Quality Index},
  url = {https://aqicn.org/}
}
```
