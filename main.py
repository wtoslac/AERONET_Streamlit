import streamlit as st
import datetime
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

    # Let user select columns to plot on the y-axis
    y_axis_options = ["AOD_380nm", "AOD_500nm", "AOD_870nm"]
    selected_y_axes = st.multiselect("Select data to plot on the Y-axis:", y_axis_options, default=y_axis_options)

    # Plot selected data
    for column in selected_y_axes:
        plt.plot(
            df.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), column]
            .resample(SampleRate)
            .mean(),
            label=column
        )

    plt.gcf().autofmt_xdate()
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1, tz='US/Pacific'))
    plt.gca().xaxis.set_minor_locator(mdates.HourLocator(interval=12, tz='US/Pacific'))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    plt.ylim(AOD_min, AOD_max)
    plt.legend()
    st.pyplot(plt.gcf())

# Matching wavelengths to positions
st.text("\nNow set the start date to 2024/10/01. You can see three different data clusters for 10/01. Now match the wavelength to its position:")
positions = ["Top", "Middle", "Bottom"]

# Dropdown menus for user input with no default selection
user_matches = {}
for pos in positions:
    user_matches[pos] = st.selectbox(f"wavelength for {pos} position:", 
                                     options=["Select an option", "450 nm", "500 nm", "870 nm"], 
                                     key=pos)

# Allow user to proceed without showing correctness
if st.button("Submit"):
    st.text("Your selections have been recorded. Take a screenshot and submit your answer! You can proceed to the next step.")
