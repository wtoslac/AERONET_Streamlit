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
EndDate = st.date_input("EndDate", datetime.date(2023, 7,7))
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
df_1 = None
if file_url_1:
    df_1 = load_data(file_url_1)

# Ensure data is loaded and columns are correct
if df_1 is not None:
    if 'AOD_400nm' not in df_1.columns or 'AOD_500nm' not in df_1.columns or 'AOD_675nm' not in df_1.columns:
        st.error(f"Missing expected columns in the dataset. Available columns: {df_1.columns}")
    
    # Plot data from the first repository if columns are correct
    if 'AOD_440nm' in df_1.columns and 'AOD_500nm' in df_1.columns and 'AOD_675nm' in df_1.columns:
        
        # Plot AOD_440nm, AOD_500nm, and AOD_675nm as initial plot
        plt.plot(df_1.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_440nm"].resample(SampleRate).mean(), '.k')
        plt.plot(df_1.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_500nm"].resample(SampleRate).mean(), '.k')
        plt.plot(df_1.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_675nm"].resample(SampleRate).mean(), '.k')

        # Format the plot
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

        # Create user input dropdowns for selecting wavelengths
        user_matches = {}
        for pos in positions:
            user_matches[pos] = st.selectbox(f"What Wavelength will be located on the {pos} position on the graph?", 
                                             options=["Select an option", "400 nm", "500 nm", "779 nm"], 
                                             key=pos)

        # Once the user submits, show the second graph (same as the first)
        if st.button("Submit"):
            # Plot the second graph (exact same as the first one)
            plt.plot(df_1.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_440nm"].resample(SampleRate).mean(), '.b', label="440 nm")
            plt.plot(df_1.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_500nm"].resample(SampleRate).mean(), '.g', label="500 nm")
            plt.plot(df_1.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_675nm"].resample(SampleRate).mean(), '.r', label="675 nm")

            # Format the second plot
            plt.gcf().autofmt_xdate()
            plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1, tz='US/Pacific'))
            plt.gca().xaxis.set_minor_locator(mdates.HourLocator(interval=12, tz='US/Pacific'))
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
            plt.ylim(AOD_min, AOD_max)
            plt.legend()
            st.pyplot(plt.gcf())




# Simulated or loaded data
# wind data (as in the previous example)
windfile = 'https://raw.githubusercontent.com/Rsaltos7/AERONET_Streamlit/refs/heads/main/Modesto_Wind_2023%20(2).csv'
windSampleRate = '3h'
Wdf = pd.read_csv(windfile, parse_dates={'datetime': [1]}, low_memory=False)
datetime_utc = pd.to_datetime(Wdf["datetime"], format='%d-%m-%Y %H:%M:%S')
datetime_pac = datetime_utc.dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
Wdf.set_index(datetime_pac, inplace=True)

# AOD Data (simulating with a dataframe, replace with real data)
df_1 = pd.DataFrame({
    'datetime': pd.date_range("2023-07-01", periods=100, freq="H"),
    'AOD_440nm': np.random.rand(100),  # Replace with actual data
    'AOD_500nm': np.random.rand(100),
    'AOD_675nm': np.random.rand(100)
})
df_1.set_index('datetime', inplace=True)

# Streamlit widgets for dynamic date range selection
start_date = st.date_input("Select Start Date", pd.to_datetime('2023-07-01'))
end_date = st.date_input("Select End Date", pd.to_datetime('2023-07-07'))
StartDateTime = pd.to_datetime(start_date)
EndDateTime = pd.to_datetime(end_date)

# Sample Rate
SampleRate = '3h'

# Creating the plot
fig, ax1 = plt.subplots(figsize=(10, 6))

# Plot the first (AOD) graph
ax1.plot(df_1.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_440nm"].resample(SampleRate).mean(),
         '.b', label="440 nm")
ax1.plot(df_1.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_500nm"].resample(SampleRate).mean(),
         '.g', label="500 nm")
ax1.plot(df_1.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_675nm"].resample(SampleRate).mean(),
         '.r', label="675 nm")

# Format the AOD plot (x-axis and limits)
ax1.set_title("AOD and Wind Vectors Overlay")
ax1.set_xlabel("Time")
ax1.set_ylabel("AOD")
ax1.gcf().autofmt_xdate()
ax1.xaxis.set_major_locator(mdates.DayLocator(interval=1, tz='US/Pacific'))
ax1.xaxis.set_minor_locator(mdates.HourLocator(interval=12, tz='US/Pacific'))
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
ax1.set_ylim(AOD_min, AOD_max)  # Adjust based on your AOD data
ax1.legend(loc='upper left')

# Create a second y-axis for the wind vectors
ax2 = ax1.twinx()  # Create a second axis sharing the same x-axis

# Extract wind data (direction and speed) and filter valid observations
WNDdf = Wdf.loc[StartDateTime:EndDateTime, 'WND'].str.split(pat=',', expand=True)
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

# Resample the wind data according to the wind sample rate and plot the wind vectors on the second y-axis
ax2.quiver(
    WNDdf[5].resample(windSampleRate).mean().index,  # X-axis (time)
    np.zeros(WNDdf[5].resample(windSampleRate).mean().shape),  # Y-axis baseline
    WNDdf[5].resample(windSampleRate).mean().div(10),  # X-component of arrows
    WNDdf[6].resample(windSampleRate).mean().div(10),  # Y-component of arrows
    color='b', label='Wind Vector'
)

# Hide the Y-axis for the wind vector plot (optional)
ax2.get_yaxis().set_visible(False)

# Display the combined plot in Streamlit
plt.tight_layout()
st.pyplot(fig)






