import streamlit as st
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

# Set up basic information
siteName = "Turlock CA USA"
SampleRate = "1h"
StartDate = st.date_input("StartDate", datetime.date(2023, 7, 1))
StartDateTime = datetime.datetime.combine(StartDate, datetime.time(0, 0))
EndDate = st.date_input("EndDate", datetime.date(2023, 7, 7))
EndDateTime = datetime.datetime.combine(EndDate, datetime.time(23, 59))

# Allow the user to set y-axis limits for AOD
st.sidebar.header("Adjust Y-axis Limits")
AOD_min = st.sidebar.slider("Y-Axis Min", min_value=0.0, max_value=1.0, value=0.0, step=0.01)
AOD_max = st.sidebar.slider("Y-Axis Max", min_value=0.0, max_value=1.0, value=0.3, step=0.01)

# Input GitHub URL for the first repository (AOD data)
file_url_1 = "https://raw.githubusercontent.com/Rsaltos7/AERONET_Streamlit/refs/heads/main/20230101_20241231_Turlock_CA_USA_part1.lev15"

# Function to load data from the given URL
def load_data(file_url):
    try:
        # Read the data from the provided GitHub raw URL
        df = pd.read_csv(file_url, skiprows=6, parse_dates={'datetime': [0, 1]})
        datetime_utc = pd.to_datetime(df["datetime"], format='%d:%m:%Y %H:%M:%S')
        datetime_pac = pd.to_datetime(datetime_utc).dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
        df.set_index(datetime_pac, inplace=True)
        return df
    except Exception as e:
        st.error(f"Failed to process the file from {file_url}: {e}")
        return None

# Load AOD data from the first file
df_1 = load_data(file_url_1)

# Ensure data is loaded and columns are correct
if df_1 is not None:
    if 'AOD_440nm' not in df_1.columns or 'AOD_500nm' not in df_1.columns or 'AOD_675nm' not in df_1.columns:
        st.error(f"Missing expected columns in the dataset. Available columns: {df_1.columns}")
    
    # Plot data from the AOD repository if columns are correct
    if 'AOD_440nm' in df_1.columns and 'AOD_500nm' in df_1.columns and 'AOD_675nm' in df_1.columns:
        
        # Plot AOD_440nm, AOD_500nm, and AOD_675nm as initial plot
        plt.plot(df_1.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_440nm"].resample(SampleRate).mean(), '.b', label="440 nm")
        plt.plot(df_1.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_500nm"].resample(SampleRate).mean(), '.g', label="500 nm")
        plt.plot(df_1.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_675nm"].resample(SampleRate).mean(), '.r', label="675 nm")

        # Format the plot
        plt.gcf().autofmt_xdate()
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1, tz='US/Pacific'))
        plt.gca().xaxis.set_minor_locator(mdates.HourLocator(interval=12, tz='US/Pacific'))
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        plt.ylim(AOD_min, AOD_max)
        plt.legend()
        st.pyplot(plt.gcf())

# Wind Data URL
windfile = 'https://raw.githubusercontent.com/Rsaltos7/AERONET_Streamlit/refs/heads/main/Modesto_Wind_2023%20(2).csv'
windSampleRate = '3h'

# Read the wind data
Wdf = pd.read_csv(windfile, parse_dates={'datetime': [1]}, low_memory=False)
datetime_utc = pd.to_datetime(Wdf["datetime"], format='%d-%m-%Y %H:%M:%S')
datetime_pac = datetime_utc.dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
Wdf.set_index(datetime_pac, inplace=True)

# Filter the wind data based on the same date range as the AOD data
Wdf_filtered = Wdf.loc[StartDateTime:EndDateTime]

# Extract wind data (direction and speed) and filter valid observations
WNDdf = Wdf_filtered['WND'].str.split(pat=',', expand=True)
WNDdf = WNDdf.loc[WNDdf[4] == '5']  # Only valid observations

# Initialize lists for Cartesian components
Xdata, Ydata = [], []

# Calculate Cartesian components of wind vectors
for _, row in WNDdf.iterrows():
    magnitude = np.float64(row[3])  # Wind speed
    direction = np.float64(row[0])  # Wind direction
    Xdata.append(magnitude * np.sin(direction * (np.pi / 180)))
    Ydata.append(magnitude * np.cos(direction * (np.pi / 180)))

# Add Cartesian components to the DataFrame
WNDdf[5], WNDdf[6] = Xdata, Ydata

# Create a plot for wind data
fig, ax = plt.subplots(figsize=(10, 6))
ax.set_title("Wind Vectors (Magnitude and Direction)")
ax.set_xlabel("Time")

# Resample the data according to the wind sample rate and plot the wind vectors
ax.quiver(
    WNDdf[5].resample(windSampleRate).mean().index,  # X-axis (time)
    np.zeros(WNDdf[5].resample(windSampleRate).mean().shape),  # Y-axis baseline
    WNDdf[5].resample(windSampleRate).mean().div(10),  # X-component of arrows
    WNDdf[6].resample(windSampleRate).mean().div(10),  # Y-component of arrows
    color='b',
    label='Wind Vector'
)

# Hide the Y-axis (but still show the arrows)
ax.get_yaxis().set_visible(False)

# Display the legend and adjust layout
ax.legend(loc='best')
plt.tight_layout()

# Display the wind plot in Streamlit
st.pyplot(fig)
