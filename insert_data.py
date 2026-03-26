import pandas as pd
from sqlalchemy import create_engine

# Load data
df = pd.read_csv("cleaned_data.csv")

# Rename columns
df.rename(columns={
    'Date Of Stop': 'Date_of_Stop'
}, inplace=True)

# Connect DB
engine = create_engine("mysql+mysqlconnector://traffic_user:1234@localhost:3306/traffic_db")

# 🔥 IMPORTANT: Use chunks (VERY IMPORTANT for large data)
df.to_sql(
    "traffic_data",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=10000
)

print("Data inserted successfully")
