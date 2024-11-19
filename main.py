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
    plt.plot(df.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_380nm"].resample(SampleRate).mean(), '.k')
    plt.plot(df.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_500nm"].resample(SampleRate).mean(), '.k')
    plt.plot(df.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_870nm"].resample(SampleRate).mean(), '.k')

    plt.gcf().autofmt_xdate()
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1, tz='US/Pacific'))
    plt.gca().xaxis.set_minor_locator(mdates.HourLocator(interval=12, tz='US/Pacific'))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    plt.ylim(AOD_min, AOD_max)
    plt.legend()
    st.pyplot(plt.gcf())

# Matching wavelengths to positions
st.text("\nNow set start date to 2024/10/01. You can see three different data clusters for 10/01. Now match the wavelength to its position:")
positions = ["Top", "Middle", "Bottom"]

# Dropdown menus for user input with no default selection
user_matches = {}
for pos in positions:
    user_matches[pos] = st.selectbox(f"Wavelength for {pos} position:", 
                                     options=["Select an option", "450 nm", "500 nm", "870 nm"], 
                                     key=pos)

# Allow user to proceed without showing correctness
if st.button("Submit"):
    st.text("Your selections have been recorded. Take a screenshot and submit your answer! You can proceed to the next step.")

    # Create the plot with user color preferences based on wavelength
    colors = {
        "450 nm": "purple",
        "500 nm": "green",
        "870 nm": "red"
    }
    
    # Define wavelength data mapping based on user selections
    wavelength_map = {
        "Top": user_matches["Top"],
        "Middle": user_matches["Middle"],
        "Bottom": user_matches["Bottom"]
    }
    
    # Plot data with appropriate colors for each wavelength
    plt.figure(figsize=(10, 6))
    for position, wavelength in wavelength_map.items():
        if wavelength != "Select an option":
            if wavelength == "450 nm":
                plt.plot(df.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_450nm"].resample(SampleRate).mean(), color=colors[wavelength], label=f"AOD {wavelength}")
            elif wavelength == "500 nm":
                plt.plot(df.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_500nm"].resample(SampleRate).mean(), color=colors[wavelength], label=f"AOD {wavelength}")
            elif wavelength == "870 nm":
                plt.plot(df.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_870nm"].resample(SampleRate).mean(), color=colors[wavelength], label=f"AOD {wavelength}")
    
    plt.gcf().autofmt_xdate()
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1, tz='US/Pacific'))
    plt.gca().xaxis.set_minor_locator(mdates.HourLocator(interval=12, tz='US/Pacific'))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    plt.ylim(AOD_min, AOD_max)
    plt.legend()
    st.pyplot(plt.gcf())
