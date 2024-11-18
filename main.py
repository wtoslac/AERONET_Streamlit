import streamlit as st
import datetime
import pytz
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Set up basic information
siteName = "Turlock CA USA"
SampleRate = "1h"
StartDate = st.date_input("StartDate", datetime.date(2024, 10, 1))
EndDate = st.date_input("EndDate", datetime.date(2024, 10, 7))

# Convert StartDate and EndDate into timezone-aware datetime objects
pacific_tz = pytz.timezone('US/Pacific')
StartDateTime = datetime.datetime.combine(StartDate, datetime.time(0, 0)).replace(tzinfo=datetime.timezone.utc).astimezone(pacific_tz)
EndDateTime = datetime.datetime.combine(EndDate, datetime.time(23, 59)).replace(tzinfo=datetime.timezone.utc).astimezone(pacific_tz)

AOD_min = 0.0
AOD_max = 0.4

# Upload files
aod_file = st.file_uploader("Upload the Level 1.5 Data from AERONET")
wind_file = st.file_uploader("Upload Wind Data (CSV)")

if aod_file is not None and wind_file is not None:
    # Read AOD data
    df_aod = pd.read_csv(aod_file, skiprows=6, parse_dates={'Date': [0, 1]})
    datetime_utc = pd.to_datetime(df_aod["Date"], format='%d:%m:%Y %H:%M:%S')
    datetime_pac = pd.to_datetime(datetime_utc).dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
    df_aod.set_index(datetime_pac, inplace=True)

    # Read Wind data
    df_wind = pd.read_csv(wind_file, parse_dates=['Datetime'])
    df_wind['datetime'] = pd.to_datetime(df_wind['Datetime']).dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
    df_wind.set_index('Datetime', inplace=True)

    # Plot AOD and wind data
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Plot AOD data on the primary y-axis
    ax1.plot(
        df_aod.loc[StartDateTime:EndDateTime, "AOD_380nm"].resample(SampleRate).mean(), 
        '.k', label="AOD_380nm"
    )
    ax1.plot(
        df_aod.loc[StartDateTime:EndDateTime, "AOD_500nm"].resample(SampleRate).mean(), 
        '.r', label="AOD_500nm"
    )
    ax1.plot(
        df_aod.loc[StartDateTime:EndDateTime, "AOD_870nm"].resample(SampleRate).mean(), 
        '.b', label="AOD_870nm"
    )
    ax1.set_ylim(AOD_min, AOD_max)
    ax1.set_ylabel("AOD")
    ax1.legend(loc="upper left")

    # Add secondary y-axis for wind data
    ax2 = ax1.twinx()
    ax2.plot(
        df_wind.loc[StartDateTime:EndDateTime, "wind_speed"].resample(SampleRate).mean(), 
        '-g', label="Wind Speed"
    )
    ax2.set_ylabel("Wind Speed (m/s)", color='green')
    ax2.tick_params(axis='y', colors='green')
    ax2.legend(loc="upper right")

    # Format x-axis
    ax1.xaxis.set_major_locator(mdates.DayLocator(interval=1, tz=pacific_tz))
    ax1.xaxis.set_minor_locator(mdates.HourLocator(interval=12, tz=pacific_tz))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    plt.gcf().autofmt_xdate()

    st.pyplot(fig)

# Matching wavelengths to positions
st.text("\nNow set start date to 2024/10/01 you can see three different data clusters for 10/01. Now match the wavelength to its position:")
positions = ["Top", "Middle", "Bottom"]

# Dropdown menus for user input with no default selection
user_matches = {}
for pos in positions:
    user_matches[pos] = st.selectbox(f"wavelength for {pos} position:", 
                                     options=["Select an option", "450 nm", "500 nm", "870 nm"], 
                                     key=pos)

# Allow user to proceed without showing correctness
if st.button("Submit"):
    st.text("Your selections have been recorded. Take a screenshot and submit the answer! You can proceed to the next step.")

