import streamlit as st
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Set up basic information
siteName = "Turlock CA USA"
SampleRate = "1h"
StartDate = st.date_input("StartDate", datetime.date(2024, 10, 1))
StartDateTime = datetime.datetime.combine(StartDate, datetime.time(0, 0))
EndDate = st.date_input("EndDate", datetime.date(2024, 10, 7))
EndDateTime = datetime.datetime.combine(EndDate, datetime.time(23, 59))
AOD_min = 0.0
AOD_max = 0.4

# Upload file
file = st.file_uploader("Upload the Level 1.5 Data from AERONET")
if file is not None:
    df = pd.read_csv(file, skiprows=6, parse_dates={'datetime': [0, 1]})
    datetime_utc = pd.to_datetime(df["datetime"], format='%d:%m:%Y %H:%M:%S')
    datetime_pac = pd.to_datetime(datetime_utc).dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
    df.set_index(datetime_pac, inplace=True)

    # Plot data
    plt.plot(df.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_380nm"].resample(SampleRate).mean(), '.b', label="AOD_380nm")
    plt.plot(df.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_500nm"].resample(SampleRate).mean(), '.g', label="AOD_500nm")
    plt.plot(df.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_870nm"].resample(SampleRate).mean(), '.r', label="AOD_870nm")

    plt.gcf().autofmt_xdate()
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1, tz='US/Pacific'))
    plt.gca().xaxis.set_minor_locator(mdates.HourLocator(interval=12, tz='US/Pacific'))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    plt.ylim(AOD_min, AOD_max)
    plt.legend()
    st.pyplot(plt.gcf())

# Matching wavelengths to positions
st.text("\nMatch the wavelength to its position:")
positions = ["Top", "Middle", "Bottom"]
correct_matches = {"Top": "450 nm", "Middle": "500 nm", "Bottom": "870 nm"}

# Dropdown menus for user input
user_matches = {}
for pos in positions:
    user_matches[pos] = st.selectbox(f"Select the wavelength for {pos} position:", options=["450 nm", "500 nm", "870 nm"], key=pos)

# Evaluate user inputs
correct_count = 0
st.text("\nResults:")
for pos, user_wavelength in user_matches.items():
    if user_wavelength == correct_matches[pos]:
        st.text(f"Correct! {pos} corresponds to {user_wavelength}.")
        correct_count += 1
    else:
        st.text(f"Wrong. {pos} does not correspond to {user_wavelength}. The correct answer is {correct_matches[pos]}.")

st.text(f"\nYou got {correct_count}/{len(positions)} correct!")

