import streamlit as st
import pandas as pd
import plotly.express as px

# PAGE CONFIG #
st.set_page_config(page_title="Traffic Dashboard", layout="wide")

# LOAD DATA #
@st.cache_data
def load_data():
    df = pd.read_csv("cleaned_data.csv")
    return df

df = load_data()

# SAMPLE DATA #
df = df.sample(500000)

# TITLE #
st.title("🚦 Traffic Violations Analytics Dashboard")
st.markdown("""
  Use the filters on the left to explore traffic patterns, identify hotspots, and analyze violations.
""")
st.divider()
# SIDEBAR FILTERS #
st.sidebar.header("Filters")

# Gender filter
gender = st.sidebar.multiselect(
    "Gender",
    df['Gender'].dropna().unique(),
    default=df['Gender'].dropna().unique()
)
# Vehicle filter
vehicle = st.sidebar.multiselect(
    "Vehicle Type",
    df['VehicleType'].dropna().unique(),
    default=df['VehicleType'].dropna().unique()
)
# Race filter
race = st.sidebar.multiselect(
    "Race",
    df['Race'].dropna().unique(),
    default=df['Race'].dropna().unique()
)

# Date filter
df['Date Of Stop'] = pd.to_datetime(df['Date Of Stop'], errors='coerce')

start_date = st.sidebar.date_input("Start Date", df['Date Of Stop'].min())
end_date = st.sidebar.date_input("End Date", df['Date Of Stop'].max())

# Violation filter
violation = st.sidebar.multiselect(
    "Violation Type",
    df['Description'].dropna().unique(),
    default=[]
)

# FILTER DATA #
filtered_df = df[
    (df['Gender'].isin(gender)) &
    (df['VehicleType'].isin(vehicle)) &
    (df['Race'].isin(race))
]
# date filter #
filtered_df = filtered_df[
    (filtered_df['Date Of Stop'] >= pd.to_datetime(start_date)) &
    (filtered_df['Date Of Stop'] <= pd.to_datetime(end_date))
]

# violation filter #
if violation:
    filtered_df = filtered_df[
        filtered_df['Description'].isin(violation)
    ]
# KPI CARDS #
col1, col2, col3 = st.columns(3)

col1.metric("Total Violations", len(filtered_df))

col2.metric(
    "⚠️ Accidents",
    int(filtered_df['Accident'].astype(str).str.lower().map({'yes':1, 'no':0}).sum()) if 'Accident' in filtered_df else 0
)

col3.metric(
    "🕒 Peak Hour",
    int(filtered_df['Hour'].mode()[0]) if not filtered_df.empty else 0
)
st.divider()
# CHARTS #

# REPEAT OFFENDERS #
st.subheader("🚨 Repeat Offenders Analysis")

# Filter repeat offenders
repeat_df = filtered_df[filtered_df['Violation_Count'] > 1]

# Total unique repeat offenders
total_repeat = repeat_df['SeqID'].nunique()

st.metric("## 🔁 Repeat Offenders", total_repeat)

# Top repeat offenders (IDs with most violations)
top_repeat = (
    repeat_df.groupby('SeqID')
    .size()
    .sort_values(ascending=False)
    .head(10)
)

st.subheader("Top Repeat Offenders")

st.bar_chart(top_repeat)

# VEHICLE MAKE ANALYSIS #
st.markdown("---")
st.subheader("Vehicle Makes Involved in Violations")

top_make = filtered_df['Make'].value_counts().head(10)

fig_make = px.bar(
    x=top_make.values,
    y=top_make.index,
    orientation='h',
    title="Top 10 Vehicle Makes"
)

st.plotly_chart(fig_make, width='stretch')

st.subheader("Vehicle Models")

top_model = filtered_df['Model'].value_counts().head(10)

fig_model = px.bar(
    x=top_model.values,
    y=top_model.index,
    orientation='h',
    title="Top 10 Vehicle Models"
)

st.plotly_chart(fig_model, width='stretch')
st.divider()

# Top Violations #
st.subheader("Top Violations")
top_violation = filtered_df['Description'].value_counts().head(10)

fig1 = px.bar(
    x=top_violation.values,
    y=top_violation.index,
    orientation='h'
)
st.plotly_chart(fig1, width='stretch')
st.divider()

# Violations by Hour #
st.subheader("Violations by Hour")
hour_data = filtered_df['Hour'].value_counts().sort_index()

fig2 = px.line(
    x=hour_data.index,
    y=hour_data.values
)
st.plotly_chart(fig2, width='stretch')
st.divider()

# Vehicle Distribution #
st.subheader("Vehicle Distribution")
vehicle_data = filtered_df['VehicleType'].value_counts().head(5)

fig3 = px.pie(
    values=vehicle_data.values,
    names=vehicle_data.index
)
st.plotly_chart(fig3, width='stretch')
st.divider()

# Gender Distribution #
st.subheader("Gender Distribution")
gender_data = filtered_df['Gender'].value_counts()

fig4 = px.bar(
    x=gender_data.index,
    y=gender_data.values
)
st.plotly_chart(fig4, width='stretch')
st.divider()

# MAP #
st.subheader("📍 Traffic Violation Hotspots")
map_df = filtered_df[['Latitude', 'Longitude']].dropna()

if not map_df.empty:
    fig = px.density_mapbox(
        map_df,
        lat='Latitude',
        lon='Longitude',
        radius=8,
        center=dict(
            lat=map_df['Latitude'].mean(),
            lon=map_df['Longitude'].mean()
        ),
        zoom=9,
        mapbox_style="open-street-map",
        title="Violation Density Heatmap"
    )

    st.plotly_chart(fig, width='stretch', height="stretch")
else:
    st.write("No location data available")
st.divider()

# AI INSIGHT (SIMPLE) #
st.subheader("🤖 Quick Insights")

if not filtered_df.empty:
    peak_hour = filtered_df['Hour'].mode()[0]
    top_violation = filtered_df['Description'].value_counts().idxmax()

    st.info(f"""
    🔹 Peak violation time: {peak_hour}:00 hrs  
    🔹 Most common violation: {top_violation}  
    🔹 Total records analyzed: {len(filtered_df)}
    """)

# FOOTER #
st.markdown("---")