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

# File upload
file = st.file_uploader("Upload the Level 1.5 Data from AERONET")
if file is not None:
    # Read the data
    df = pd.read_csv(file, skiprows=6, parse_dates={'datetime': [0, 1]})
    df['datetime'] = pd.to_datetime(df['datetime'], format='%d:%m:%Y %H:%M:%S')
    df = df.set_index('datetime')
    df.index = df.index.tz_localize('UTC').tz_convert('US/Pacific')  # Localize and convert timezone

    # Plot initial graph in black and white
    plt.figure(figsize=(10, 5))
    plt.plot(
        df.loc[StartDateTime:EndDateTime, "AOD_380nm"].resample(SampleRate).mean(),
        '.k',
        label="AOD 380 nm"
    )
    plt.plot(
        df.loc[StartDateTime:EndDateTime, "AOD_500nm"].resample(SampleRate).mean(),
        '.k',
        label="AOD 500 nm"
    )
    plt.plot(
        df.loc[StartDateTime:EndDateTime, "AOD_870nm"].resample(SampleRate).mean(),
        '.k',
        label="AOD 870 nm"
    )

    # Format the initial plot
    plt.gcf().autofmt_xdate()
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1))
    plt.gca().xaxis.set_minor_locator(mdates.HourLocator(interval=12))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    plt.ylim(AOD_min, AOD_max)
    plt.legend()
    st.pyplot(plt.gcf())

    # Ask user to match wavelengths to positions
    st.text("\nMatch the wavelengths to the positions on the graph:")

    # Dropdown menus for user input with no default selection
    positions = ["Top", "Middle", "Bottom"]

    # Create user input dropdowns
    user_matches = {}
    for pos in positions:
        user_matches[pos] = st.selectbox(
            f"What Wavelength will be located on the {pos} position on the graph?",
            options=["Select an option", "380 nm", "500 nm", "870 nm"],
            key=pos
        )

    # Allow user to submit and display feedback
    if st.button("Submit"):
        st.text("Your selections have been recorded. Take a screenshot and submit your answer!")

        # Create a second graph with predefined colors for the wavelengths
        wavelength_colors = {
            "380 nm": "b",  # Blue
            "500 nm": "g",  # Green
            "870 nm": "r"   # Red
        }

        # Create the second graph
        plt.figure(figsize=(10, 5))
        plt.plot(
            df.loc[StartDateTime:EndDateTime, "AOD_380nm"].resample(SampleRate).mean(),
            '.',
            color=wavelength_colors["380 nm"],
            label="AOD 380 nm"
        )
        plt.plot(
            df.loc[StartDateTime:EndDateTime, "AOD_500nm"].resample(SampleRate).mean(),
            '.',
            color=wavelength_colors["500 nm"],
            label="AOD 500 nm"
        )
        plt.plot(
            df.loc[StartDateTime:EndDateTime, "AOD_870nm"].resample(SampleRate).mean(),
            '.',
            color=wavelength_colors["870 nm"],
            label="AOD 870 nm"
        )

        # Format the second plot
        plt.gcf().autofmt_xdate()
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1))
        plt.gca().xaxis.set_minor_locator(mdates.HourLocator(interval=12))
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        plt.ylim(AOD_min, AOD_max)
        plt.legend()
        st.pyplot(plt.gcf())
