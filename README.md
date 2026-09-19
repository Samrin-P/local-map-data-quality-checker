# Local Map Data Quality Checker & Visualization System

A small portfolio project for checking the quality of local location datasets and visualizing usable records on an interactive map.

## Features
- CSV upload
- Required-column validation
- Missing/incomplete field detection
- Latitude/longitude validation
- Duplicate name + address detection
- Interactive map with clustered markers
- Downloadable validated CSV

## Tech stack
Python, Pandas, Streamlit, Folium

## Run locally

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
# source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

Open the local Streamlit URL and upload `sample_map_data.csv`.

## Dataset
The included CSV is a synthetic practice dataset created for demonstrating data-quality checks. It contains deliberately introduced issues so the validation logic can be tested.

## Resume description
**Local Map Data Quality Checker & Visualization System** — Python, Pandas, Streamlit, Folium
- Built a Python application to validate local location datasets and identify incomplete, duplicate, and invalid coordinate records.
- Added an interactive map for visualizing validated locations and a CSV export for cleaned results.
