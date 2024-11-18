import streamlit as st
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

siteName="Turlock CA USA"
SampleRate = "1h"
StartDate = st.date_input("StartDate", datetime.date(2024, 10, 1))
StartDateTime = datetime.datetime.combine(StartDate, datetime.time(0,0))
EndDate = st.date_input("EndDate", datetime.date(2024, 10, 7))
EndDateTime = datetime.datetime.combine(EndDate, datetime.time(23,59))
AOD_min = 0.0
AOD_max = 0.4

file = st.file_uploader("Upload the Level 1.5 Data Downloaded from: https://aeronet.gsfc.nasa.gov/cgi-bin/webtool_aod_v3?stage=3&region=United_States_West&state=California&site=Turlock_CA_USA")
df = pd.read_csv(file,skiprows = 6, parse_dates={'datetime':[0,1]})
datetime_utc=pd.to_datetime(df["datetime"], format='%d:%m:%Y %H:%M:%S')
datetime_pac= pd.to_datetime(datetime_utc).dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
df.set_index(datetime_pac, inplace = True)
plt.plot(df.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'),"AOD_380nm"].resample(SampleRate).mean(),'.b',label="AOD_380nm")
plt.plot(df.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'),"AOD_500nm"].resample(SampleRate).mean(),'.g',label="AOD_500nm")
plt.plot(df.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'),"AOD_870nm"].resample(SampleRate).mean(),'.r',label="AOD_870nm")

plt.gcf().autofmt_xdate()
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1, tz='US/Pacific'))
plt.gca().xaxis.set_minor_locator(mdates.HourLocator(interval=12, tz='US/Pacific'))
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
#Change the range on Y here if needed
plt.ylim(AOD_min,AOD_max)
plt.legend()
st.pyplot(plt.gcf())

import streamlit as st

# Define Position and wavelengths
Position = ["Top", "Middle", "Bottom"]
wavelengths = [380, 500, 870]

# Create a dictionary to map correct matches
correct_matches = {
    "Top": 380,
    "Middle": 500,
    "Bottom": 870
}

# Display question
st.text("Match the following wavelength (nm) with there [redicted place on the graph")
st.text("Options: 500, 870, 380")

# Collect user responses
user_matches = {}
for position in potisions:
    error_message_shown = False  # Track if an error message has been shown
    while True:
        wavelength = st.number_input(f"What is the wavelength of {position}?", min_value=0, step=1, key=color)
        if wavelength == 0:  # Default state for `st.number_input`, waiting for user input
            continue
        if wavelength in wavelengths:
            user_matches[position] = wavelength
            st.text(f"Great job! This is correct: {position} = {correct_matches[position]} nm")
            break
        elif not error_message_shown:
            st.text(f"Invalid choice for {position}. Please choose one of 380, 500, or 870.")
            error_message_shown = True

# Check and display results
correct_count = 0
st.text("\nResults:")
for position, user_wavelength in user_matches.items():
    if user_wavelength == correct_matches[position]:
        st.text(f"Correct! {position.capitalize()} corresponds to {user_wavelength} nm.")
        correct_count += 1
    else:
        st.text(f"Wrong. {position.capitalize()} does not correspond to {user_wavelength} nm. The correct answer is {correct_matches[color]} nm.")

st.text(f"\nYou got {correct_count}/{len(position)} correct!")

