import pandas as pd
import numpy as np

# ================= LOAD CSV =================
df = pd.read_csv("Traffic_Violations.csv", low_memory=False)

print("Original shape:", df.shape)

print(df.columns)
# ================= 1. REMOVE DUPLICATES =================
df = df.drop_duplicates()

# ================= 2. DATE-TIME CLEAN =================
df['Date Of Stop'] = pd.to_datetime(df['Date Of Stop'], errors='coerce')

df['Time Of Stop'] = df['Time Of Stop'].astype(str).str.replace('.', ':', regex=False)

df['Datetime'] = pd.to_datetime(
    df['Date Of Stop'].astype(str) + ' ' + df['Time Of Stop'],
    errors='coerce'
)

# ================= 3. CATEGORICAL CLEAN =================
df['Gender'] = df['Gender'].replace({'M': 'Male', 'F': 'Female'})
df['Race'] = df['Race'].astype(str).str.upper().str.strip()
df['VehicleType'] = df['VehicleType'].astype(str).str.upper().str.strip()

# ================= 4. GEO CLEAN =================
df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')

df.loc[(df['Latitude'] == 0) | (df['Latitude'] > 90), 'Latitude'] = np.nan
df.loc[(df['Longitude'] == 0) | (df['Longitude'] < -180), 'Longitude'] = np.nan

# ================= 5. HANDLE MISSING =================
df.fillna({
    'Gender': 'Unknown',
    'Race': 'Unknown',
    'VehicleType': 'Unknown'
}, inplace=True)

# ================= 6. YEAR CLEAN =================
df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
df = df[(df['Year'] >= 1960) & (df['Year'] <= 2025)]

# ================= 7. BOOLEAN CLEAN =================
bool_cols = ['Accident', 'Belts', 'Personal Injury', 'Property Damage', 'Fatal']

for col in bool_cols:
    df[col] = df[col].astype(str).str.lower().map({
        'yes': True, 'no': False, 'y': True, 'n': False
    })

# ================= 8. FEATURE ENGINEERING =================
df['Hour'] = df['Datetime'].dt.hour
df['DayOfWeek'] = df['Datetime'].dt.day_name()
df['Month'] = df['Datetime'].dt.month

df['Violation_Count'] = df.groupby('SeqID')['SeqID'].transform('count')

# ================= SAVE =================
df.to_csv("cleaned_data.csv", index=False)

print("Cleaned shape:", df.shape)
print("Cleaning done ✅")