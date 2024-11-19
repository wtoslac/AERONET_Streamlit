import streamlit as st
import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Page setup
st.set_page_config(page_title="Environmental Data Analysis", layout="wide")
st.title("Environmental Data Analysis Tool")

# Sidebar navigation
st.sidebar.header("Navigation")
selected_tool = st.sidebar.radio("Choose a tool:", ["Wind Vector Analysis", "AOD Analysis"])

# Common sample rate
SampleRate = "1h"

if selected_tool == "Wind Vector Analysis":
    # Wind Vector Analysis Section
    st.header("Wind Vector Analysis")
    
    # File upload for wind data
    windfile = st.file_uploader("Upload Wind Data (CSV format)", type="csv")
    
    if windfile is not None:
        StartDate = st.date_input("Start Date", datetime.date(2019, 6, 11))
        EndDate = st.date_input("End Date", datetime.date(2019, 6, 13))
        windSampleRate = "1h"

        # Load NOAA wind data
        Wdf = pd.read_csv(windfile, parse_dates={'datetime': [1]}, low_memory=False)
        datetime_utc = pd.to_datetime(Wdf["datetime"], format='%d-%m-%Y %H:%M:%S')
        datetime_pac = datetime_utc.dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
        Wdf.set_index(datetime_pac, inplace=True)

        # Extract wind data and filter valid observations
        WNDdf = Wdf.loc[str(StartDate):str(EndDate), 'WND'].str.split(pat=',', expand=True)
        WNDdf = WNDdf.loc[WNDdf[4] == '5']  # Only valid observations

        # Convert polar to Cartesian coordinates for wind direction and magnitude
        Xdata, Ydata = [], []
        for _, row in WNDdf.iterrows():
            magnitude = np.float64(row[3])  # Wind speed
            direction = np.float64(row[0])  # Wind direction
            Xdata.append(magnitude * np.sin(direction * (np.pi / 180)))
            Ydata.append(magnitude * np.cos(direction * (np.pi / 180)))

        WNDdf[5], WNDdf[6] = Xdata, Ydata  # Add Cartesian components to the DataFrame

        # Create plot
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.set_title("Wind Vectors (Magnitude and Direction)")
        ax.set_xlabel("Time")
        ax.set_ylabel("Magnitude (m/s)")

        try:
            ax.quiver(
                WNDdf[5].resample(windSampleRate).mean().index,  # X-axis (time)
                np.zeros(WNDdf[5].resample(windSampleRate).mean().shape),  # Y-axis baseline
                WNDdf[5].resample(windSampleRate).mean().div(10),  # X-component of arrows
                WNDdf[6].resample(windSampleRate).mean().div(10),  # Y-component of arrows
                color='b',
                label='Wind Vector'
            )
            # Add legend
            ax.legend(loc='best')

            # Display the plot
            st.pyplot(fig)
        except ValueError:
            st.error("No data available for the selected date range.")

elif selected_tool == "AOD Analysis":
    # AOD Analysis Section
    st.header("Aerosol Optical Depth (AOD) Analysis")
    
    siteName = "Turlock CA USA"
    StartDate = st.date_input("Start Date", datetime.date(2024, 10, 1))
    StartDateTime = datetime.datetime.combine(StartDate, datetime.time(0, 0))
    EndDate = st.date_input("End Date", datetime.date(2024, 10, 7))
    EndDateTime = datetime.datetime.combine(EndDate, datetime.time(23, 59))

    # User inputs for Y-axis limits
    AOD_min = st.number_input("Set minimum Y-axis value:", value=0.0, step=0.1)
    AOD_max = st.number_input("Set maximum Y-axis value:", value=0.4, step=0.1)

    # Upload AOD file
    file = st.file_uploader(
        "Upload the Level 1.5 Data from AERONET. "
        "Click this [link](https://drive.google.com/file/d/12qSh5UWpL_cfsIQU7pnIUV8vouEgHB-V/view?usp=sharing) for sample data.",
        type="csv",
    )

    if file is not None:
        df = pd.read_csv(file, skiprows=6, parse_dates={'datetime': [0, 1]})
        datetime_utc = pd.to_datetime(df["datetime"], format='%d:%m:%Y %H:%M:%S')
        datetime_pac = pd.to_datetime(datetime_utc).dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
        df.set_index(datetime_pac, inplace=True)

        # Plot initial black-and-white graph
        plt.plot(
            df.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_380nm"]
            .resample(SampleRate)
            .mean(),
            '.k',
        )
        plt.plot(
            df.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_500nm"]
            .resample(SampleRate)
            .mean(),
            '.k',
        )
        plt.plot(
            df.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_870nm"]
            .resample(SampleRate)
            .mean(),
            '.k',
        )

        plt.gcf().autofmt_xdate()
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1, tz='US/Pacific'))
        plt.gca().xaxis.set_minor_locator(mdates.HourLocator(interval=12, tz='US/Pacific'))
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        plt.ylim(AOD_min, AOD_max)
        plt.legend()
        st.pyplot(plt.gcf())

        # Dropdown menus for user input
        st.text("\nNow set the start date to 2024/10/01. Match the wavelength to its position:")
        positions = ["Top", "Middle", "Bottom"]

        user_matches = {}
        for pos in positions:
            user_matches[pos] = st.selectbox(
                f"Wavelength for {pos} position:", options=["Select an option", "380 nm", "500 nm", "870 nm"], key=pos
            )

        # Display colored graph after submission
        if st.button("Submit"):
            st.text("Your selections have been recorded. The colored graph is displayed below!")

            # Plot colored graph
            plt.plot(
                df.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_380nm"]
                .resample(SampleRate)
                .mean(),
                marker='.', linestyle='', color='purple', label="AOD_380nm"
            )
            plt.plot(
                df.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_500nm"]
                .resample(SampleRate)
                .mean(),
                marker='.', linestyle='', color='green', label="AOD_500nm"
            )
            plt.plot(
                df.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_870nm"]
                .resample(SampleRate)
                .mean(),
                marker='.', linestyle='', color='red', label="AOD_870nm"
            )

            plt.gcf().autofmt_xdate()
            plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1, tz='US/Pacific'))
            plt.gca().xaxis.set_minor_locator(mdates.HourLocator(interval=12, tz='US/Pacific'))
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
            plt.ylim(AOD_min, AOD_max)
            plt.legend()
            st.pyplot(plt.gcf())

