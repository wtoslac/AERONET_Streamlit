import streamlit as st
import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Page setup
st.set_page_config(page_title="Environmental Data Analysis", layout="wide")
st.title("Environmental Data Analysis Tool")

# Sidebar inputs
st.sidebar.header("Settings")
SampleRate = "1h"
StartDate = st.sidebar.date_input("Start Date", datetime.date(2019, 6, 11))
EndDate = st.sidebar.date_input("End Date", datetime.date(2019, 6, 13))
StartDateTime = datetime.datetime.combine(StartDate, datetime.time(0, 0))
EndDateTime = datetime.datetime.combine(EndDate, datetime.time(23, 59))
AOD_min = st.sidebar.number_input("Set minimum AOD value:", value=0.0, step=0.1)
AOD_max = st.sidebar.number_input("Set maximum AOD value:", value=0.4, step=0.1)

# File uploaders
windfile = st.file_uploader("Upload Wind Data (CSV format)", type="csv")
aodfile = st.file_uploader("Upload AOD Data (CSV format)", type="csv")

if windfile is not None and aodfile is not None:
    # Load Wind Data
    Wdf = pd.read_csv(windfile, parse_dates={'datetime': [1]}, low_memory=False)
    datetime_utc = pd.to_datetime(Wdf["datetime"], format='%d-%m-%Y %H:%M:%S')
    datetime_pac = datetime_utc.dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
    Wdf.set_index(datetime_pac, inplace=True)
    
    # Process Wind Data
    WNDdf = Wdf.loc[str(StartDate):str(EndDate), 'WND'].str.split(pat=',', expand=True)
    WNDdf = WNDdf.loc[WNDdf[4] == '5']  # Only valid observations
    Xdata, Ydata = [], []
    for _, row in WNDdf.iterrows():
        magnitude = np.float64(row[3])  # Wind speed
        direction = np.float64(row[0])  # Wind direction
        Xdata.append(magnitude * np.sin(direction * (np.pi / 180)))
        Ydata.append(magnitude * np.cos(direction * (np.pi / 180)))
    WNDdf[5], WNDdf[6] = Xdata, Ydata  # Add Cartesian components

    # Load AOD Data
    df = pd.read_csv(aodfile, skiprows=6, parse_dates={'datetime': [0, 1]})
    datetime_utc = pd.to_datetime(df["datetime"], format='%d:%m:%Y %H:%M:%S')
    datetime_pac = datetime_utc.dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
    df.set_index(datetime_pac, inplace=True)

    # Create combined plot
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Plot AOD data
    ax1.set_title("AOD and Wind Vectors")
    ax1.set_xlabel("Time")
    ax1.set_ylabel("AOD", color="purple")
    ax1.plot(
        df.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_380nm"]
        .resample(SampleRate)
        .mean(),
        '.-', color="purple", label="AOD_380nm"
    )
    ax1.plot(
        df.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_500nm"]
        .resample(SampleRate)
        .mean(),
        '.-', color="green", label="AOD_500nm"
    )
    ax1.plot(
        df.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_870nm"]
        .resample(SampleRate)
        .mean(),
        '.-', color="red", label="AOD_870nm"
    )
    ax1.set_ylim(AOD_min, AOD_max)
    ax1.legend(loc="upper left")
    ax1.tick_params(axis="y", labelcolor="purple")

    # Add Wind Vectors on a secondary axis
    ax2 = ax1.twinx()
    ax2.set_ylabel("Wind Vectors", color="blue")
    try:
        ax2.quiver(
            WNDdf[5].resample(SampleRate).mean().index,  # Time
            np.zeros(WNDdf[5].resample(SampleRate).mean().shape),  # Y-axis baseline
            WNDdf[5].resample(SampleRate).mean().div(10),  # X-component (scaled)
            WNDdf[6].resample(SampleRate).mean().div(10),  # Y-component (scaled)
            color="blue",
            label="Wind Vectors",
        )
    except ValueError:
        st.error("No valid wind vector data in the selected range.")
    ax2.tick_params(axis="y", labelcolor="blue")

    # Format x-axis
    ax1.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    ax1.xaxis.set_minor_locator(mdates.HourLocator(interval=12))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    fig.autofmt_xdate()

    # Display plot
    st.pyplot(fig)
else:
    st.info("Please upload both wind data and AOD data to generate the combined plot.")
