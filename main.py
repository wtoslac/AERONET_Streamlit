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

    # Matching wavelengths to positions
    st.text("\nNow set start date to 2024/10/01 you can see three different data clusters for 10/01. Now Match the wavelength to its position:")
    positions = ["Top", "Middle", "Bottom"]

    # Dropdown menus for user input with no default selection
    user_matches = {}
    for pos in positions:
        user_matches[pos] = st.selectbox(f"Wavelength for {pos} position:", 
                                         options=["Select an option", "450 nm", "500 nm", "870 nm"], 
                                         key=pos)

    # Define color mapping
    color_mapping = {
        "450 nm": "purple",
        "500 nm": "green",
        "870 nm": "red"
    }

    # Allow user to proceed without showing correctness
    if st.button("Submit"):
        st.text("Your selections have been recorded. Take a screenshot and submit your answer! You can proceed to the next step.")

        # Plot data with the selected colors
        plt.figure(figsize=(10, 6))

        # Loop over the user selections and plot corresponding wavelengths
        for pos, wavelength in user_matches.items():
            if wavelength != "Select an option":  # Only plot if the user has selected a valid option
                color = color_mapping.get(wavelength, 'black')  # Default to black if no color is found
                column_name = f"AOD_{wavelength.replace(' ', '').replace('nm', '')}"  # Create column name based on the selected wavelength
                if column_name in df.columns:  # Check if the column exists
                    plt.plot(df.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), column_name].resample(SampleRate).mean(),
                             color=color, label=f"AOD {wavelength}")
                else:
                    st.warning(f"Column {column_name} not found in the dataset.")

        # Set plot aesthetics
        plt.gcf().autofmt_xdate()
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1, tz='US/Pacific'))
        plt.gca().xaxis.set_minor_locator(mdates.HourLocator(interval=12, tz='US/Pacific'))
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        plt.ylim(AOD_min, AOD_max)
        plt.legend()
        st.pyplot(plt.gcf())
