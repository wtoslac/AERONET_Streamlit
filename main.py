import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

# File URL and parameters
windfile = 'https://raw.githubusercontent.com/Rsaltos7/AERONET_Streamlit/refs/heads/main/Modesto_Wind_2023%20(2).csv'
StartDate = '2023-07-01 00:00:00'
EndDate = '2023-07-05 23:59:59'
windSampleRate = '1h'

# Read the wind data
Wdf = pd.read_csv(windfile, parse_dates={'datetime': [1]}, low_memory=False)
datetime_utc = pd.to_datetime(Wdf["datetime"], format='%d-%m-%Y %H:%M:%S')
datetime_pac = datetime_utc.dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
Wdf.set_index(datetime_pac, inplace=True)

# Filter by date range
Wdf = Wdf.loc[StartDate:EndDate]

# Extract wind data (direction and speed) and filter valid observations
WNDdf = Wdf['WND'].str.split(pat=',', expand=True)
WNDdf = WNDdf.loc[WNDdf[4] == '5']  # Only valid observations

# Initialize lists for Cartesian components
Xdata, Ydata = [], []

# Calculate Cartesian components of wind vectors
for _, row in WNDdf.iterrows():
    magnitude = np.float64(row[3])  # Wind speed
    direction = np.float64(row[0])  # Wind direction
    Xdata.append(magnitude * np.sin(direction * (np.pi / 180)))
    Ydata.append(magnitude * np.cos(direction * (np.pi / 180)))

# Add Cartesian components to the DataFrame
WNDdf[5], WNDdf[6] = Xdata, Ydata

# Create a plot
fig, ax = plt.subplots(figsize=(10, 6))
ax.set_title("Wind Vectors (Magnitude and Direction)")
ax.set_xlabel("Time")
ax.set_ylabel("Magnitude (m/s)")

# Resample the data according to the wind sample rate and plot the wind vectors
ax.quiver(
    WNDdf[5].resample(windSampleRate).mean().index,  # X-axis (time)
    np.zeros(WNDdf[5].resample(windSampleRate).mean().shape),  # Y-axis baseline
    WNDdf[5].resample(windSampleRate).mean().div(10),  # X-component of arrows
    WNDdf[6].resample(windSampleRate).mean().div(10),  # Y-component of arrows
    color='b',
    label='Wind Vector'
)

ax.legend(loc='best')
plt.tight_layout()

# Display the plot in Streamlit
st.pyplot(fig)
