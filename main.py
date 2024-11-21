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

# Input GitHub raw file URLs
st.header("Load Data from GitHub Repository")
file_url_1 = st.text_input(
    "Enter the raw URL of the first .lev15 file from the GitHub repository:",
    "https://raw.githubusercontent.com/Rsaltos7/AERONET_Streamlit/refs/heads/main/20230101_20241231_Turlock_CA_USA_part1.lev15"  # Default URL
)
file_url_2 = st.text_input(
    "Enter the raw URL of the second .lev15 file from the GitHub repository:",
    "https://raw.githubusercontent.com/Rsaltos7/AERONET_Streamlit/refs/heads/main/20230101_20241231_Turlock_CA_USA_part2.lev15"  # Default URL
)

# Check if both URLs are provided
if file_url_1 and file_url_2:
    try:
        # Read the data from the provided GitHub raw URLs
        df_1 = pd.read_csv(file_url_1, skiprows=6, parse_dates={'datetime': [0, 1]})
        df_2 = pd.read_csv(file_url_2, skiprows=6, parse_dates={'datetime': [0, 1]})

        # Convert datetime columns to datetime objects (timezone naive)
        datetime_utc_1 = pd.to_datetime(df_1["datetime"], format='%d:%m:%Y %H:%M:%S')
        datetime_utc_2 = pd.to_datetime(df_2["datetime"], format='%d:%m:%Y %H:%M:%S')

        # Ensure both datetime columns are timezone naive first, then localize to UTC
        datetime_utc_1 = datetime_utc_1.dt.tz_localize('UTC', ambiguous='NaT')  # Ensure naive datetime becomes UTC aware
        datetime_utc_2 = datetime_utc_2.dt.tz_localize('UTC', ambiguous='NaT')

        # Convert both to Pacific Time after they are localized to UTC
        datetime_pac_1 = datetime_utc_1.dt.tz_convert('US/Pacific')
        datetime_pac_2 = datetime_utc_2.dt.tz_convert('US/Pacific')

        # Set the datetime columns as index for both dataframes
        df_1.set_index(datetime_pac_1, inplace=True)
        df_2.set_index(datetime_pac_2, inplace=True)

        # Combine both dataframes into one (if you want to stack them)
        df_combined = pd.concat([df_1, df_2])

        # Plot initial graph in black and white (no color coding)
        plt.plot(df_combined.loc[StartDateTime:EndDateTime, "AOD_380nm"].resample(SampleRate).mean(), '.k', label="380 nm")
        plt.plot(df_combined.loc[StartDateTime:EndDateTime, "AOD_500nm"].resample(SampleRate).mean(), '.k', label="500 nm")
        plt.plot(df_combined.loc[StartDateTime:EndDateTime, "AOD_870nm"].resample(SampleRate).mean(), '.k', label="870 nm")

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
                "380 nm": "b",  # Blue
                "500 nm": "g",  # Green
                "870 nm": "r"   # Red
            }

            # Create the second graph independently of user input
            plt.plot(df_combined.loc[StartDateTime:EndDateTime, "AOD_380nm"].resample(SampleRate).mean(), '.b', label="380 nm")
            plt.plot(df_combined.loc[StartDateTime:EndDateTime, "AOD_500nm"].resample(SampleRate).mean(), '.g', label="500 nm")
            plt.plot(df_combined.loc[StartDateTime:EndDateTime, "AOD_870nm"].resample(SampleRate).mean(), '.r', label="870 nm")

            # Format the second plot
            plt.gcf().autofmt_xdate()
            plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1, tz='US/Pacific'))
            plt.gca().xaxis.set_minor_locator(mdates.HourLocator(interval=12, tz='US/Pacific'))
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
            plt.ylim(AOD_min, AOD_max)
            plt.legend()
            st.pyplot(plt.gcf())

    except Exception as e:
        st.error(f"Failed to process the files: {e}")
