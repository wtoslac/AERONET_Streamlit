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

# File uploads
file1 = st.file_uploader("Upload the first CSV file (first_half.csv)")
file2 = st.file_uploader("Upload the second CSV file (second_half.csv)")

if file1 and file2:
    try:
        # Load both files
        df1 = pd.read_csv(file1, skiprows=6, parse_dates={'datetime': [0, 1]})
        df2 = pd.read_csv(file2, skiprows=6, parse_dates={'datetime': [0, 1]})

        # Debugging: Display sample data
        st.write("First file sample:")
        st.write(df1.head())
        st.write("Second file sample:")
        st.write(df2.head())

        # Concatenate the data
        df = pd.concat([df1, df2], ignore_index=True)

        # Parse and set datetime as index
        df["datetime"] = pd.to_datetime(df["datetime"], errors='coerce')
        df.set_index("datetime", inplace=True)

        # Plot data
        plt.figure(figsize=(10, 6))
        plt.plot(df.loc[StartDateTime:EndDateTime, "AOD_380nm"].resample(SampleRate).mean(), '.k', label="380 nm")
        plt.plot(df.loc[StartDateTime:EndDateTime, "AOD_500nm"].resample(SampleRate).mean(), '.k', label="500 nm")
        plt.plot(df.loc[StartDateTime:EndDateTime, "AOD_870nm"].resample(SampleRate).mean(), '.k', label="870 nm")

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

    
