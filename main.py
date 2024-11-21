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

# Allow the user to set y-axis limits
st.sidebar.header("Adjust Y-axis Limits")
AOD_min = st.sidebar.slider("Y-Axis Min", min_value=0.0, max_value=1.0, value=0.0, step=0.01)
AOD_max = st.sidebar.slider("Y-Axis Max", min_value=0.0, max_value=1.0, value=0.3, step=0.01)

# GitHub raw file URL input
st.header("Load Data from GitHub Repository")
file_url = st.text_input(
    "Enter the raw URL of the .lev15 file from the GitHub repository:",
    "https://raw.githubusercontent.com/Rsaltos7/AERONET_Streamlit/refs/heads/main/20230101_20241231_Turlock_CA_USA_part1.lev15"
)

if file_url:
    try:
        # Read the data from the provided GitHub raw URL
        df = pd.read_csv(file_url, skiprows=6, parse_dates={'datetime': [0, 1]})
        datetime_utc = pd.to_datetime(df["datetime"], format='%d:%m:%Y %H:%M:%S')
        datetime_pac = pd.to_datetime(datetime_utc).dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
        df.set_index(datetime_pac, inplace=True)

        # Plot initial graph in black and white (no color coding)
        plt.plot(df.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_380nm"].resample(SampleRate).mean(), '.k', label="380 nm")
        plt.plot(df.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_500nm"].resample(SampleRate).mean(), '.k', label="500 nm")
        plt.plot(df.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_870nm"].resample(SampleRate).mean(), '.k', label="870 nm")

        # Format the initial plot
        plt.gcf().autofmt_xdate()
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1, tz='US/Pacific'))
        plt.gca().xaxis.set_minor_locator(mdates.HourLocator(interval=12, tz='US/Pacific'))
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
            user_matches[pos] = st.selectbox(f"What Wavelength will be located on the {pos} position on the graph?", 
                                             options=["Select an option", "400 nm", "500 nm", "779 nm"], 
                                             key=pos)

        # Allow user to submit and display feedback
        if st.button("Submit"):
            st.text("Your selections have been recorded. Take a screenshot and submit your answer!")

            # Create a second graph with predefined colors for the wavelengths (independent of user's input)
            wavelength_colors = {
                "380 nm": "b",  # Red
                "500 nm": "g",  # Green
                "870 nm": "r"   # Blue
            }

            # Create the second graph independently of user input
            plt.plot(df.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_380nm"].resample(SampleRate).mean(), '.b', color=wavelength_colors["380 nm"], label="380 nm")
            plt.plot(df.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_500nm"].resample(SampleRate).mean(), '.g', color=wavelength_colors["500 nm"], label="500 nm")
            plt.plot(df.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_870nm"].resample(SampleRate).mean(), '.r', color=wavelength_colors["870 nm"], label="870 nm")

            # Format the second plot
            plt.gcf().autofmt_xdate()
            plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1, tz='US/Pacific'))
            plt.gca().xaxis.set_minor_locator(mdates.HourLocator(interval=12, tz='US/Pacific'))
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
            plt.ylim(AOD_min, AOD_max)
            plt.legend()
            st.pyplot(plt.gcf())

    except Exception as e:
        st.error(f"Failed to process the file: {e}")
