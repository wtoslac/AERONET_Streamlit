import streamlit as st
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

# Streamlit Inputs
siteName = "Turlock CA USA"
SampleRate = "1h"
StartDate = st.date_input("StartDate", datetime.date(2024, 10, 1))
StartDateTime = datetime.datetime.combine(StartDate, datetime.time(0, 0))
EndDate = st.date_input("EndDate", datetime.date(2024, 10, 7))
EndDateTime = datetime.datetime.combine(EndDate, datetime.time(23, 59))

# AOD Y-axis limits
AOD_min = st.number_input("Set minimum Y-axis value (AOD):", value=0.0, step=0.1)
AOD_max = st.number_input("Set maximum Y-axis value (AOD):", value=0.4, step=0.1)

# File uploads
aodfile = st.file_uploader("Upload AOD Data (e.g., AERONET Level 1.5):")
windfile = st.file_uploader("Upload Wind Data (NOAA CSV format):")

if aodfile:
    # Parse the AOD file
    df_aod = pd.read_csv(aodfile, skiprows=6, parse_dates={'datetime': [0, 1]})
    df_aod['datetime'] = pd.to_datetime(df_aod['datetime'], format='%d:%m:%Y %H:%M:%S')
    datetime_pac_aod = df_aod['datetime'].dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
    df_aod.set_index(datetime_pac_aod, inplace=True)

    # Filter AOD data for the selected range
    aod_filtered = df_aod.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S')]

if windfile:
    # Parse wind data
    Wdf = pd.read_csv(windfile, parse_dates={'datetime': [1]}, low_memory=False)
    datetime_utc_wind = pd.to_datetime(Wdf["datetime"], format='%d-%m-%Y %H:%M:%S')
    datetime_pac_wind = datetime_utc_wind.dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
    Wdf.set_index(datetime_pac_wind, inplace=True)

    # Extract wind data and process valid observations
    WNDdf = Wdf.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), 'WND'].str.split(pat=',', expand=True)
    WNDdf = WNDdf.loc[WNDdf[4] == '5']  # Only valid observations

    # Calculate Cartesian wind components
    Xdata, Ydata = [], []
    for _, row in WNDdf.iterrows():
        magnitude = np.float64(row[3])  # Wind speed
        direction = np.float64(row[0])  # Wind direction
        Xdata.append(magnitude * np.sin(direction * (np.pi / 180)))
        Ydata.append(magnitude * np.cos(direction * (np.pi / 180)))

    WNDdf[5], WNDdf[6] = Xdata, Ydata

# Plot combined data
fig, ax = plt.subplots(figsize=(12, 8))

if aodfile:
    # Plot AOD data
    for column, color, label in zip(["AOD_380nm", "AOD_500nm", "AOD_870nm"], ['purple', 'green', 'red'], ["AOD_380nm", "AOD_500nm", "AOD_870nm"]):
        if column in aod_filtered.columns:
            ax.plot(
                aod_filtered[column].resample(SampleRate).mean(),
                marker='.',
                linestyle='',
                color=color,
                label=label
            )

if windfile:
    # Plot wind vectors
    ax.quiver(
        WNDdf[5].resample(SampleRate).mean().index,  # Time index
        np.zeros(WNDdf[5].resample(SampleRate).mean().shape),  # Baseline Y-axis
        WNDdf[5].resample(SampleRate).mean().div(10),  # X-component (scaled)
        WNDdf[6].resample(SampleRate).mean().div(10),  # Y-component (scaled)
        color='blue',
        label='Wind Vector'
    )

# Customize plot
ax.set_title(f"AOD and Wind Data for {siteName}")
ax.set_xlabel("Date")
ax.set_ylabel("AOD / Wind Vector Magnitude")
ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
ax.xaxis.set_minor_locator(mdates.HourLocator(interval=12))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
ax.set_ylim(AOD_min, AOD_max)
ax.legend()
plt.grid()

# Display plot
st.pyplot(fig)
