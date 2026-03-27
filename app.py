import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

# ================= DB CONNECTION =================
engine = create_engine("mysql+mysqlconnector://traffic_user:1234@localhost:3306/traffic_db")

st.set_page_config(page_title="Traffic Dashboard", layout="wide")

st.title("🚦 Traffic Violations Dashboard")
st.divider()

# ================= SIDEBAR FILTERS =================
st.sidebar.header("🔍 Filters")

# Gender
gender_options = ['M', 'F']

gender = st.sidebar.multiselect(
    "Gender",
    options=gender_options,
    default=gender_options
)

# Vehicle
vehicle_options = pd.read_sql(
    "SELECT DISTINCT VehicleType FROM traffic_data",
    engine
)['VehicleType'].dropna().tolist()

vehicle = st.sidebar.multiselect(
    "Vehicle Type",
    options=vehicle_options,
    default=vehicle_options
)

# Race
race_options = pd.read_sql(
    "SELECT DISTINCT Race FROM traffic_data",
    engine
)['Race'].dropna().tolist()

race = st.sidebar.multiselect(
    "Race",
    options=race_options,
    default=race_options
)
# ================= BASE QUERY =================
base_query = "SELECT * FROM traffic_data WHERE 1=1"

if set(gender) != set(gender_options):
    base_query += f" AND Gender IN ({','.join([f'\"{g}\"' for g in gender])})"

if set(vehicle) != set(vehicle_options):
    base_query += f" AND VehicleType IN ({','.join([f'\"{v}\"' for v in vehicle])})"

if set(race) != set(race_options):
    base_query += f" AND Race IN ({','.join([f'\"{r}\"' for r in race])})"

# LIMIT for performance
base_query += " LIMIT 500000"
# ================= KPI =================
total = pd.read_sql(f"""
    SELECT COUNT(*) as count
    FROM ({base_query}) AS filtered
""", engine)

st.metric("Total Violations", int(total['count']))
st.divider()

# ================= TOP VIOLATIONS =================
st.subheader("Top Violations")

top_violation = pd.read_sql(f"""
    SELECT Description, COUNT(*) as count
    FROM ({base_query}) AS filtered
    GROUP BY Description
    ORDER BY count DESC
    LIMIT 10
""", engine)

fig1 = px.bar(top_violation, x="count", y="Description", orientation='h')
st.plotly_chart(fig1, use_container_width=True)
st.divider()

# ================= HOUR ANALYSIS =================
st.subheader("Violations by Hour")

hour_data = pd.read_sql(f"""
    SELECT Hour as hour, COUNT(*) as count
    FROM ({base_query}) AS filtered
    WHERE Hour IS NOT NULL
    GROUP BY Hour
    ORDER BY Hour
""", engine)

st.write("Hour Data Preview:", hour_data.head())  # debug

fig2 = px.line(hour_data, x="hour", y="count")
st.plotly_chart(fig2, use_container_width=True)
st.divider()

# ================= VEHICLE DISTRIBUTION =================
st.subheader("Vehicle Distribution")

vehicle_df = pd.read_sql(f"""
    SELECT VehicleType, COUNT(*) as count
    FROM ({base_query}) AS filtered
    GROUP BY VehicleType
    ORDER BY count DESC
    LIMIT 5
""", engine)

fig3 = px.pie(vehicle_df, values="count", names="VehicleType")
st.plotly_chart(fig3, use_container_width=True)
st.divider()

# ================= REPEAT OFFENDERS =================
st.subheader("Repeat Offenders")

repeat = pd.read_sql(f"""
    SELECT SeqID, COUNT(*) as violation_count
    FROM ({base_query}) AS filtered
    GROUP BY SeqID
    HAVING COUNT(*) > 1
    ORDER BY violation_count DESC
    LIMIT 10
""", engine)

st.bar_chart(repeat.set_index('SeqID'))
st.divider()

# ================= HEATMAP =================
st.subheader("Hotspot Heatmap")

map_df = pd.read_sql(f"""
    SELECT Latitude, Longitude
    FROM ({base_query}) AS filtered
    WHERE Latitude IS NOT NULL AND Longitude IS NOT NULL
""", engine)

fig_map = px.density_mapbox(
    map_df,
    lat='Latitude',
    lon='Longitude',
    radius=8,
    center=dict(
        lat=map_df['Latitude'].mean(),
        lon=map_df['Longitude'].mean()
    ),
    zoom=9,
    mapbox_style="open-street-map"
)

st.plotly_chart(fig_map, use_container_width=True)
