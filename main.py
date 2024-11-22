import streamlit as st
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

# Set up basic information
siteName = "Turlock CA USA"
SampleRate = "1h"
StartDate = st.date_input("Start Date", datetime.date(2023, 7, 1))
StartDateTime = datetime.datetime.combine(StartDate, datetime.time(0, 0))
EndDate = st.date_input("End Date", datetime.date(2023, 7, 7))
EndDateTime = datetime.datetime.combine(EndDate, datetime.time(23, 59))

# Allow the user to set y-axis limits
st.sidebar.header("Adjust Y-axis Limits")
AOD_min = st.sidebar.slider("Y-Axis Min", min_value=0.0, max_value=1.0, value=0.0, step=0.01)
AOD_max = st.sidebar.slider("Y-Axis Max", min_value=0.0, max_value=1.0, value=0.3, step=0.01)

# Input GitHub URL for the first repository
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

# Load data from the first file
df_1 = load_data(file_url_1)

# Ensure data is loaded and columns are correct
if df_1 is not None:
    if 'AOD_400nm' not in df_1.columns or 'AOD_500nm' not in df_1.columns or 'AOD_675nm' not in df_1.columns:
        st.error(f"Missing expected columns in the dataset. Available columns: {df_1.columns}")

# URL for the wind data file
windfile = 'https://raw.githubusercontent.com/Rsaltos7/AERONET_Streamlit/refs/heads/main/Modesto_Wind_2023%20(2).csv'
windSampleRate = '3h'

# Read the wind data
Wdf = pd.read_csv(windfile, parse_dates={'datetime': [1]}, low_memory=False)
datetime_utc = pd.to_datetime(Wdf["datetime"], format='%d-%m-%Y %H:%M:%S')
datetime_pac = datetime_utc.dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
Wdf.set_index(datetime_pac, inplace=True)

# Streamlit widgets for dynamic date range selection for wind data
start_date = st.date_input("Select Wind Start Date", pd.to_datetime('2023-07-01'))
end_date = st.date_input("Select Wind End Date", pd.to_datetime('2023-07-07'))

# Convert selected dates to strings and filter the data
StartDate = start_date.strftime('%Y-%m-%d 00:00:00')
EndDate = end_date.strftime('%Y-%m-%d 23:59:59')

# Filter by the user-selected date range for wind data
Wdf_filtered = Wdf.loc[StartDate:EndDate]

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

# Plot Temperature Data
st.subheader("Temperature Plot")
Tdf = Wdf.loc[StartDate:EndDate, 'TMP'].str.split(pat=',', expand=True)
Tdf.replace('+9999', np.nan, inplace=True)

# Plot the Temperature graph
fig, ax = plt.subplots(figsize=(16, 9))
ax.set_title(siteName + ' ' + StartDate.strftime('%Y') + ' Temperature')
ax.grid(True)
ax.xaxis.set_major_locator(mdates.DayLocator(interval=1, tz='US/Pacific'))
ax.xaxis.set_minor_locator(mdates.HourLocator(interval=3, tz='US/Pacific'))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))

ax.set_ylabel('Temperature °C')
ax.set_ylim(Tdf[0].loc[StartDate:EndDate].astype(float).resample(SampleRate).mean().div(10).min()//1,
            Tdf[0].loc[StartDate:EndDate].astype(float).resample(SampleRate).mean().div(10).max()//1)  # Auto Calculating
temperatureHandle, = ax.plot(Tdf[0].loc[StartDate:EndDate].astype(float).resample(SampleRate).mean().div(10), '.r-', label='Temperature')

plt.legend(handles=[temperatureHandle], loc='best')
plt.tight_layout()
st.pyplot(fig)

# Plot Wind Data
st.subheader("Wind Vectors (Magnitude and Direction)")
fig, ax = plt.subplots(figsize=(16, 9))

ax.set_title("Wind Vector Plot")
ax.set_xlabel("Time")
ax.set_ylabel("Magnitude m/s")
ax2 = ax.twinx()
ax2.set_ylabel("Wind Direction (°)", color='g')

maxWind = np.sqrt((WNDdf[6].loc[StartDate:EndDate].astype(float).max()/10)**2 +
                  (WNDdf[5].loc[StartDate:EndDate].astype(float).max()/10)**2)
ax.set_ylim(0, maxWind)

# Resample the data according to the wind sample rate and plot the wind vectors
ax.quiver(WNDdf[5].resample(windSampleRate).mean().index, maxWind-1,
          -WNDdf[5].resample(windSampleRate).mean().div(10),
          -WNDdf[6].resample(windSampleRate).mean().div(10),
          color='b', label='Wind Vector')

plt.tight_layout()
st.pyplot(fig)

