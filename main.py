import streamlit as st
import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Streamlit app title
st.title("AERONET and Wind Data Visualization")

# Inputs for AOD Data
siteName = "Turlock CA USA"
SampleRate = "1h"
StartDate = st.date_input("Start Date", datetime.date(2024, 10, 1))
StartDateTime = datetime.datetime.combine(StartDate, datetime.time(0, 0))
EndDate = st.date_input("End Date", datetime.date(2024, 10, 7))
EndDateTime = datetime.datetime.combine(EndDate, datetime.time(23, 59))

# Y-axis limits for AOD plot
AOD_min = st.number_input("Set minimum Y-axis value:", value=0.0, step=0.1)
AOD_max = st.number_input("Set maximum Y-axis value:", value=0.4, step=0.1)

# Upload AOD data file
aod_file = st.file_uploader("Upload AOD Data File", type=['lev15'])
if aod_file:
    # Read the lev15 file
    df_aod = pd.read_csv(aod_file, skiprows=6, delim_whitespace=True, engine='python')
    
    # Parse the datetime column
    df_aod['datetime'] = pd.to_datetime(
        df_aod['Date(dd:mm:yyyy)'] + " " + df_aod['Time(hh:mm:ss)'],
        format='%d:%m:%Y %H:%M:%S'
    )
    
    # Convert datetime to US/Pacific timezone
    datetime_utc = pd.to_datetime(df_aod['datetime'])
    datetime_pac = datetime_utc.dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
    df_aod.set_index(datetime_pac, inplace=True)
    
    # Plot AOD data
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(
        df_aod.loc[StartDateTime:EndDateTime, "AOD_380nm"].resample(SampleRate).mean(),
        marker='.', linestyle='', color='purple', label="AOD_380nm"
    )
    ax.plot(
        df_aod.loc[StartDateTime:EndDateTime, "AOD_500nm"].resample(SampleRate).mean(),
        marker='.', linestyle='', color='green', label="AOD_500nm"
    )
    ax.plot(
        df_aod.loc[StartDateTime:EndDateTime, "AOD_870nm"].resample(SampleRate).mean(),
        marker='.', linestyle='', color='red', label="AOD_870nm"
    )
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1, tz='US/Pacific'))
    ax.xaxis.set_minor_locator(mdates.HourLocator(interval=12, tz='US/Pacific'))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    ax.set_ylim(AOD_min, AOD_max)
    ax.set_title("AOD Data")
    ax.legend()
    plt.tight_layout()
    st.pyplot(fig)

# Inputs for Wind Data
wind_file = st.file_uploader("Upload Wind Data File", type=['csv'])
if wind_file:
    wind_df = pd.read_csv(wind_file, parse_dates={'datetime': [1]}, low_memory=False)
    datetime_utc = pd.to_datetime(wind_df["datetime"], format='%d-%m-%Y %H:%M:%S')
    datetime_pac = datetime_utc.dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
    wind_df.set_index(datetime_pac, inplace=True)

    # Split the WND column into components
    WNDdf = wind_df.loc[StartDateTime:EndDateTime, 'WND'].str.split(pat=',', expand=True)
    
    # Debugging output
    st.write("Split WND DataFrame:", WNDdf.head())

    # Ensure WNDdf has enough columns
    if len(WNDdf.columns) >= 5:
        WNDdf = WNDdf.loc[WNDdf[4] == '5']  # Filter valid observations

        # Convert polar to Cartesian components
        Xdata, Ydata = [], []
        for _, row in WNDdf.iterrows():
            try:
                magnitude = float(row[3])  # Wind speed
                direction = float(row[0])  # Wind direction
                Xdata.append(magnitude * np.sin(np.radians(direction)))
                Ydata.append(magnitude * np.cos(np.radians(direction)))
            except ValueError:
                Xdata.append(np.nan)
                Ydata.append(np.nan)

        WNDdf['X'], WNDdf['Y'] = Xdata, Ydata

        # Resample data
        X_resampled = WNDdf['X'].resample(SampleRate).mean()
        Y_resampled = WNDdf['Y'].resample(SampleRate).mean()

        # Plot wind vectors
        fig, ax = plt.subplots(figsize=(10, 6))
        time_index = X_resampled.index
        ax.quiver(
            time_index, np.zeros_like(X_resampled),
            X_resampled.div(10), Y_resampled.div(10),
            angles='xy', scale_units='xy', scale=1, color='b'
        )
        ax.set_title("Wind Vectors")
        ax.set_xlabel("Time")
        ax.set_ylabel("Wind Magnitude (scaled)")
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=1, tz='US/Pacific'))
        ax.xaxis.set_minor_locator(mdates.HourLocator(interval=12, tz='US/Pacific'))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.error("The wind data format does not match the expected structure.")
