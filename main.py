import streamlit as st
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Set up basic information
siteName = "Turlock CA USA"
SampleRate = "1h"
StartDate = st.date_input("Start Date", datetime.date(2024, 10, 1))
StartDateTime = datetime.datetime.combine(StartDate, datetime.time(0, 0))
EndDate = st.date_input("End Date", datetime.date(2024, 10, 7))
EndDateTime = datetime.datetime.combine(EndDate, datetime.time(23, 59))

# Allow the user to set y-axis limits
st.sidebar.header("Adjust Y-axis Limits")
AOD_min = st.sidebar.slider("Y-Axis Min", min_value=0.0, max_value=1.0, value=0.0, step=0.01)
AOD_max = st.sidebar.slider("Y-Axis Max", min_value=0.0, max_value=1.0, value=0.3, step=0.01)

# Predefined file paths for GitHub repository files
st.header("Select Data File from GitHub Repository")
file_choice = st.selectbox(
    "Choose a file to load:",
    options=[
        "https://github.com/Rsaltos7/AERONET_Streamlit/blob/main/20230101_20241231_Turlock_CA_USA_part1.lev15",
        "https://github.com/Rsaltos7/AERONET_Streamlit/blob/main/20230101_20241231_Turlock_CA_USA_part2.lev15"
    ],
)

if file_choice:
    try:
        # Read the data from the GitHub raw URL
        df = pd.read_csv(file_choice, skiprows=6, parse_dates={'datetime': [0, 1]})
        datetime_utc = pd.to_datetime(df["datetime"], format='%d:%m:%Y %H:%M:%S')
        datetime_pac = pd.to_datetime(datetime_utc).dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
        df.set_index(datetime_pac, inplace=True)

        # Plot initial graph in black and white (no color coding)
        plt.plot(df.loc[StartDateTime:EndDateTime, "AOD_380nm"].resample(SampleRate).mean(), '.k', label="380 nm")
        plt.plot(df.loc[StartDateTime:EndDateTime, "AOD_500nm"].resample(SampleRate).mean(), '.k', label="500 nm")
        plt.plot(df.loc[StartDateTime:EndDateTime, "AOD_870nm"].resample(SampleRate).mean(), '.k', label="870 nm")

        # Format the initial plot
        plt.gcf().autofmt_xdate()
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1, tz='US/Pacific'))
        plt.gca().xaxis.set_minor_locator(mdates.HourLocator(interval=12, tz='US/Pacific'))
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        plt.ylim(AOD_min, AOD_max)
        plt.legend()
        st.pyplot(plt.gcf())
    except Exception as e:
        st.error(f"Failed to process the file: {e}")

