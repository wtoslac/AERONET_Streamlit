import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import streamlit as st
import datetime

# Set up Streamlit inputs
siteName = "Turlock CA USA"
SampleRate = "1h"
StartDate = st.date_input("StartDate", datetime.date(2024, 10, 1))
StartDateTime = datetime.datetime.combine(StartDate, datetime.time(0, 0)).astimezone(datetime.timezone.utc).astimezone(datetime.timezone(datetime.timedelta(hours=-8)))  # US/Pacific timezone
EndDate = st.date_input("EndDate", datetime.date(2024, 10, 7))
EndDateTime = datetime.datetime.combine(EndDate, datetime.time(23, 59)).astimezone(datetime.timezone.utc).astimezone(datetime.timezone(datetime.timedelta(hours=-8)))  # US/Pacific timezone
AOD_min = 0.0
AOD_max = 0.4

# Upload AERONET and Wind data files
aeronet_file = st.file_uploader("Upload AERONET Level 1.5 Data")
wind_file = st.file_uploader("Upload Wind Data")

if aeronet_file and wind_file:
    # Process AERONET data
    df = pd.read_csv(aeronet_file, skiprows=6, parse_dates={'datetime': [0, 1]})
    datetime_utc = pd.to_datetime(df["datetime"], format='%d:%m:%Y %H:%M:%S')
    datetime_pac = datetime_utc.dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
    df.set_index(datetime_pac, inplace=True)

    # Process Wind Data
    wind_df = pd.read_csv(wind_file, parse_dates={'datetime': [1]}, low_memory=False)

    # Print the column names and inspect the first few rows for debugging
    st.write(wind_df.columns)
    st.write(wind_df.head())

    # Ensure 'WND' column exists and contains expected data
    if 'WND' in wind_df.columns:
        # Extract wind speed and direction
        wind_speed = wind_df['WND'].str.split(',', expand=True)[3].astype(float) / 10.0
        wind_direction = wind_df['WND'].str.split(',', expand=True)[0].astype(float)

        # Convert wind data to Cartesian coordinates
        wind_x = wind_speed * np.sin(np.radians(wind_direction))
        wind_y = wind_speed * np.cos(np.radians(wind_direction))
    else:
        st.error("The 'WND' column is not found in the wind data file.")
        wind_x, wind_y = [], []

    # Convert Wind Data index to timezone-aware (US/Pacific)
    wind_datetime_utc = pd.to_datetime(wind_df["datetime"], format='%d-%m-%Y %H:%M:%S')
    wind_datetime_pac = wind_datetime_utc.dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
    wind_df.set_index(wind_datetime_pac, inplace=True)

    # Slice wind data for the selected date range
    wind_df = wind_df.loc[StartDateTime:EndDateTime]

    # Create the plot
    fig, ax = plt.subplots(figsize=(12, 6))

    # Plot AOD data
    ax.plot(
        df.loc[StartDateTime:EndDateTime, "AOD_500nm"].resample(SampleRate).mean(),
        label="AOD_500nm",
        marker="o",
        linestyle="-",
        color="black",
    )
    ax.set_ylabel("AOD (500 nm)")
    ax.set_ylim(AOD_min, AOD_max)

    # Add temperature data
    temp_ax = ax.twinx()
    temp_data = wind_df['TMP'].str.split(',', expand=True)[0].astype(float) / 10.0
    temp_ax.plot(
        temp_data.resample(SampleRate).mean(),
        label="Temperature",
        linestyle="--",
        color="red",
    )
    temp_ax.set_ylabel("Temperature (°C)", color="red")
    temp_ax.tick_params(axis='y', labelcolor="red")

    # Add wind quiver
    quiver_ax = ax.twinx()
    quiver_ax.spines["right"].set_position(("axes", 1.1))  # Offset for better visualization
    quiver_ax.quiver(
        wind_x.index, np.zeros_like(wind_x),
        wind_x.resample(SampleRate).mean(), wind_y.resample(SampleRate).mean(),
        angles="xy", scale_units="xy", scale=1, color="blue", label="Wind Vector"
    )
    quiver_ax.set_ylabel("Wind (m/s)", color="blue")
    quiver_ax.tick_params(axis='y', labelcolor="blue")

    # Formatting and legend
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1, tz='US/Pacific'))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    ax.grid(True, which="both", linestyle="--", linewidth=0.5)
    fig.autofmt_xdate()

    # Legend for all data
    lines, labels = ax.get_legend_handles_labels()
    lines2, labels2 = temp_ax.get_legend_handles_labels()
    lines3, labels3 = quiver_ax.get_legend_handles_labels()
    ax.legend(lines + lines2 + lines3, labels + labels2 + labels3, loc="best")

    st.pyplot(fig)
