# Air Quality Data Citations

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
