import streamlit as st
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
pip install gdown
import gdown  # This library allows us to download files from Google Drive

# Set up basic information
siteName = "Turlock CA USA"
SampleRate = "1h"
StartDate = st.date_input("StartDate", datetime.date(2023, 1, 1))
StartDateTime = datetime.datetime.combine(StartDate, datetime.time(0, 0))
EndDate = st.date_input("EndDate", datetime.date(2024, 12, 31))
EndDateTime = datetime.datetime.combine(EndDate, datetime.time(23, 59))

# Allow the user to set y-axis limits
st.sidebar.header("Adjust Y-axis Limits")
AOD_min = st.sidebar.slider("Y-Axis Min", min_value=0.0, max_value=1.0, value=0.0, step=0.01)
AOD_max = st.sidebar.slider("Y-Axis Max", min_value=0.0, max_value=1.0, value=0.3, step=0.01)

# Google Drive file ID (extracted from the URL)
google_drive_file_id = "12qSh5UWpL_cfsIQU7pnIUV8vouEgHB-V"
download_url = f"https://drive.google.com/uc?id={google_drive_file_id}"

# Function to download the file from Google Drive and load into pandas DataFrame
def load_data_from_google_drive(url):
    try:
        # Download the file from Google Drive
        gdown.download(url, "data.csv", quiet=False)  # Downloads as data.csv
        
        # Read the downloaded file into a pandas DataFrame
        df = pd.read_csv("data.csv", skiprows=6, parse_dates={'datetime': [0, 1]})
        return df
    except Exception as e:
        st.error(f"Error loading file from Google Drive: {e}")
        return pd.DataFrame()  # Return an empty DataFrame if there's an error

# Load the data
data = load_data_from_google_drive(download_url)

# Check if the data is loaded successfully
if not data.empty:
    # Debugging: Display the column names
    st.write("Loaded columns:", data.columns)

    # Plot data if the columns exist
    if "AOD_380nm" in data.columns and "AOD_500nm" in data.columns and "AOD_870nm" in data.columns:
        plt.figure(figsize=(10, 6))
        plt.plot(data.loc[StartDateTime:EndDateTime, "AOD_380nm"].resample(SampleRate).mean(), '.k', label="380 nm")
        plt.plot(data.loc[StartDateTime:EndDateTime, "AOD_500nm"].resample(SampleRate).mean(), '.k', label="500 nm")
        plt.plot(data.loc[StartDateTime:EndDateTime, "AOD_870nm"].resample(SampleRate).mean(), '.k', label="870 nm")

        # Format the plot
        plt.gcf().autofmt_xdate()
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1))
        plt.gca().xaxis.set_minor_locator(mdates.HourLocator(interval=12))
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        plt.ylim(AOD_min, AOD_max)
        plt.legend()
        plt.title(f"AOD Measurements for {siteName}")
        plt.xlabel("Date")
        plt.ylabel("AOD")
        st.pyplot(plt.gcf())
    else:
        st.error("Missing required columns: AOD_380nm, AOD_500nm, AOD_870nm")
else:
    st.error("No data loaded, check your Google Drive file.")
