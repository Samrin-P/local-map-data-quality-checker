import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
from io import BytesIO

st.set_page_config(page_title="Local Map Data Quality Checker", page_icon="📍", layout="wide")

REQUIRED = ["record_id","name","category","address","city","state","latitude","longitude"]

@st.cache_data
def load_csv(file):
    return pd.read_csv(file)

def validate(df):
    out = df.copy()
    for c in REQUIRED:
        if c not in out.columns:
            out[c] = None
    out["latitude_num"] = pd.to_numeric(out["latitude"], errors="coerce")
    out["longitude_num"] = pd.to_numeric(out["longitude"], errors="coerce")
    out["missing_fields"] = out[REQUIRED].isna().sum(axis=1)
    out["invalid_coordinates"] = (
        out["latitude_num"].notna() & ((out["latitude_num"] < -90) | (out["latitude_num"] > 90))
    ) | (
        out["longitude_num"].notna() & ((out["longitude_num"] < -180) | (out["longitude_num"] > 180))
    )
    out["duplicate_name_address"] = out.duplicated(
        subset=["name","address"], keep=False
    )
    out["quality_status"] = "Valid"
    out.loc[out["missing_fields"] > 0, "quality_status"] = "Incomplete"
    out.loc[out["invalid_coordinates"], "quality_status"] = "Invalid coordinates"
    out.loc[out["duplicate_name_address"], "quality_status"] = "Duplicate"
    return out

st.title("📍 Local Map Data Quality Checker")
st.caption("A practical data-cleaning and mapping tool for location datasets.")

with st.sidebar:
    st.header("Dataset")
    uploaded = st.file_uploader("Upload a CSV file", type=["csv"])
    st.info("Expected fields: record_id, name, category, address, city, state, latitude, longitude")

if uploaded:
    df = load_csv(uploaded)
else:
    st.warning("No file uploaded. Load the included sample_map_data.csv to test the application.")
    st.stop()

checked = validate(df)

total = len(checked)
valid = int((checked.quality_status == "Valid").sum())
issues = total - valid
duplicates = int(checked.duplicate_name_address.sum())
missing = int((checked.missing_fields > 0).sum())
invalid = int(checked.invalid_coordinates.sum())

c1,c2,c3,c4 = st.columns(4)
c1.metric("Records", total)
c2.metric("Valid", valid)
c3.metric("Records with issues", issues)
c4.metric("Duplicate records", duplicates)

tab1, tab2, tab3 = st.tabs(["Data quality", "Map", "Export"])

with tab1:
    st.subheader("Validation results")
    st.dataframe(
        checked[REQUIRED + ["quality_status","missing_fields","invalid_coordinates","duplicate_name_address"]],
        use_container_width=True, hide_index=True
    )
    st.write(f"**Missing/incomplete:** {missing} | **Invalid coordinates:** {invalid} | **Duplicate entries:** {duplicates}")

with tab2:
    map_df = checked[
        (checked.latitude_num.notna()) & (checked.longitude_num.notna()) &
        (~checked.invalid_coordinates)
    ].copy()
    if len(map_df):
        center = [map_df.latitude_num.mean(), map_df.longitude_num.mean()]
        m = folium.Map(location=center, zoom_start=13, tiles="OpenStreetMap")
        cluster = MarkerCluster().add_to(m)
        for _, r in map_df.iterrows():
            popup = f"<b>{r['name']}</b><br>{r['category']}<br>{r['address']}<br>Status: {r['quality_status']}"
            folium.Marker(
                [r.latitude_num, r.longitude_num],
                popup=popup,
                tooltip=r["name"]
            ).add_to(cluster)
        st_folium(m, width=None, height=550)
    else:
        st.error("No valid coordinates available for mapping.")

with tab3:
    cleaned = checked[REQUIRED].copy()
    cleaned["validation_status"] = checked["quality_status"]
    cleaned_csv = cleaned.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download validated CSV",
        cleaned_csv,
        "validated_map_data.csv",
        "text/csv"
    )
    st.write("The exported file keeps the original fields and adds validation_status.")
