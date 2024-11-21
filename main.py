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

# GitHub raw file URLs
raw_file_1 = "https://github.com/Rsaltos7/AERONET_Streamlit/blob/main/first_half.csv"
raw_file_2 = "https://github.com/Rsaltos7/AERONET_Streamlit/blob/main/second_half.csv"

try:
    # Read the data from GitHub
    df1 = pd.read_csv(raw_file_1, skiprows=6)
    df2 = pd.read_csv(raw_file_2, skiprows=6)

    # Debugging: Display sample data
    st.write("First file sample:")
    st.write(df1.head())
    st.write("Second file sample:")
    st.write(df2.head())

    # Check datetime columns
    if "datetime" not in df1.columns:
        st.error("The 'datetime' column is missing. Check the file structure.")
    else:
        st.success("The 'datetime' column was found!")

    # Parse dates and set index
    df1["datetime"] = pd.to_datetime(df1["datetime"], errors='coerce')
    df2["datetime"] = pd.to_datetime(df2["datetime"], errors='coerce')

    # Concatenate the data
    data = pd.concat([df1, df2], ignore_index=True)
    data.set_index("datetime", inplace=True)

    # Plot initial graph
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
    st.pyplot(plt.gcf())

except Exception as e:
    st.error(f"Error loading data: {e}")
