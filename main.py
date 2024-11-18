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

# User inputs for Y-axis limits
AOD_min = st.number_input("Set minimum Y-axis value:", value=0.0, step=0.1)
AOD_max = st.number_input("Set maximum Y-axis value:", value=0.4, step=0.1)

# Upload file
file = st.file_uploader("Upload the Level 1.5 Data from AERONET")
if file is not None:
    df = pd.read_csv(file, skiprows=6, parse_dates={'datetime': [0, 1]})
    datetime_utc = pd.to_datetime(df["datetime"], format='%d:%m:%Y %H:%M:%S')
    datetime_pac = pd.to_datetime(datetime_utc).dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
    df.set_index(datetime_pac, inplace=True)

    # Plot initial black-and-white graph
    st.subheader("Initial Black-and-White Graph")
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(
        df.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_380nm"]
        .resample(SampleRate)
        .mean(),
        '.k',
    )
    ax.plot(
        df.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_500nm"]
        .resample(SampleRate)
        .mean(),
        '.k',
    )
    ax.plot(
        df.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_870nm"]
        .resample(SampleRate)
        .mean(),
        '.k',
    )

    ax.gcf().autofmt_xdate()
    ax.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1, tz='US/Pacific'))
    ax.gca().xaxis.set_minor_locator(mdates.HourLocator(interval=12, tz='US/Pacific'))
    ax.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    ax.set_ylim(AOD_min, AOD_max)
    ax.legend(["AOD_380nm", "AOD_500nm", "AOD_870nm"])
    st.pyplot(fig)

    # Matching wavelengths to positions
    st.text("\nNow set the start date to 2024/10/01. You can see three different data clusters for 10/01. Now match the wavelength to its position:")
    positions = ["Top", "Middle", "Bottom"]

    # Dropdown menus for user input with no default selection
    user_matches = {}
    for pos in positions:
        user_matches[pos] = st.selectbox(
            f"wavelength for {pos} position:", options=["Select an option", "450 nm", "500 nm", "870 nm"], key=pos
        )

    # Allow user to proceed and display colored graph after submission
    if st.button("Submit"):
        st.text("Your selections have been recorded. The colored graph is displayed below!")

        # Plot colored graph
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(
            df.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_380nm"]
            .resample(SampleRate)
            .mean(),
            marker='o', linestyle='', color='purple', label="AOD_380nm"  # Purple dots only
        )
        ax.plot(
            df.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_500nm"]
            .resample(SampleRate)
            .mean(),
            marker='o', linestyle='', color='green', label="AOD_500nm"  # Green dots only
        )
        ax.plot(
            df.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_870nm"]
            .resample(SampleRate)
            .mean(),
            marker='o', linestyle='', color='red', label="AOD_870nm"  # Red dots only
        )

        ax.gcf().autofmt_xdate()
        ax.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1, tz='US/Pacific'))
        ax.gca().xaxis.set_minor_locator(mdates.HourLocator(interval=12, tz='US/Pacific'))
        ax.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        ax.set_ylim(AOD_min, AOD_max)
        ax.legend()
        st.pyplot(fig)
        import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 
import matplotlib.dates as mdates
import matplotlib.patches as mpatches

# Files to be used (You can change these filenames when you have the actual data)
filename = '20190101_20191231_Modesto (1).tot_lev20'
windfile = 'Modesto_Wind_2019_Jan_Dec_72492623258.csv'  # Wind data file

# Load the AERONET data (AOD data) and convert datetime to US/Pacific time
df = pd.read_csv(filename, skiprows=6, parse_dates={'datetime': [0, 1]})
datetime_utc = pd.to_datetime(df["datetime"], format='%d:%m:%Y %H:%M:%S')
datetime_pac = pd.to_datetime(datetime_utc).dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
df.set_index(datetime_pac, inplace=True)

# Replace invalid AOD values with NaN
df['AOD_380nm-Total'].replace(-999.0, np.nan, inplace=True)
df['AOD_440nm-Total'].replace(-999.0, np.nan, inplace=True)
df['AOD_500nm-Total'].replace(-999.0, np.nan, inplace=True)
df['AOD_675nm-Total'].replace(-999.0, np.nan, inplace=True)

# Load the wind data (from NOAA or another source)
Wdf = pd.read_csv(windfile, parse_dates={'datetime': [1]}, low_memory=False)
datetime_utc = pd.to_datetime(Wdf["datetime"], format='%d-%m-%Y %H:%M:%S')
datetime_pac = pd.to_datetime(datetime_utc).dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
Wdf.set_index(datetime_pac, inplace=True)

# Filter wind data
StartDate = '2019-06-11 00:00:00'
EndDate = '2019-06-13 23:59:59'
WNDdf = Wdf.loc[StartDate:EndDate, 'WND'].str.split(pat=',', expand=True)

# Convert wind direction (angle) to Cartesian coordinates
Xdata, Ydata = [], []
for _, row in WNDdf.iterrows():
    Xdata.append(np.float64(row[3]) * np.sin(np.float64(row[0]) * (np.pi / 180)))  # Magnitude * sin(angle)
    Ydata.append(np.float64(row[3]) * np.cos(np.float64(row[0]) * (np.pi / 180)))  # Magnitude * cos(angle)
WNDdf[5], WNDdf[6] = Xdata, Ydata  # Add Cartesian coordinates (X, Y)

# Set up temperature data (split and handle missing values)
Tdf = Wdf.loc[StartDate:EndDate, 'TMP'].str.split(pat=',', expand=True)
Tdf.replace('+9999', np.nan, inplace=True)

# Creating Figure and main Axis for the plot
fig, ax = plt.subplots(figsize=(16*.65, 9*.65))  # Aspect ratio 16:9
ax.set_title("Modesto 2019: AOD, Wind Speed, and Temperature")
ax.grid(which='both', axis='both')
ax.xaxis.set_major_locator(mdates.DayLocator(interval=1, tz='US/Pacific'))
ax.xaxis.set_minor_locator(mdates.HourLocator(interval=3, tz='US/Pacific'))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))

# Plotting AOD data (AOD_500nm-Total)
ax.set_ylabel("AOD_500nm-Total")
ax.plot(df.loc[StartDate:EndDate, 'AOD_500nm-Total'].resample('1H').mean(), 'ok-', label='AOD_500nm-Total')

# Adding Temperature as the second axis
ax2 = ax.twinx()
ax2.set_ylabel('Temperature (°C)')
ax2.set_ylim(Tdf[0].loc[StartDate:EndDate].astype(float).resample('1H').mean().div(10).min(),
             Tdf[0].loc[StartDate:EndDate].astype(float).resample('1H').mean().div(10).max())
ax2.plot(Tdf[0].loc[StartDate:EndDate].astype(float).resample('1H').mean().div(10), '.r-', label='Temperature')

# Adding Wind Vectors as the third axis
ax3 = ax.twinx()
ax3.set_ylabel("Wind Magnitude (m/s)")
ax3.set_ylim(WNDdf[3].loc[StartDate:EndDate].astype(float).div(10).min(),
             WNDdf[3].loc[StartDate:EndDate].astype(float).div(10).max())
ax3.quiver(WNDdf[5].resample('1H').mean().index,
           np.sqrt((WNDdf[5].loc[StartDate:EndDate].astype(float).resample('1H').sum() /
                    WNDdf.loc[StartDate:EndDate].resample('1H').size())**2 +
                   (WNDdf[6].loc[StartDate:EndDate].astype(float).resample('1H').sum() /
                    WNDdf.loc[StartDate:EndDate].resample('1H').size())**2) / 10,
           -WNDdf[5].loc[StartDate:EndDate].astype(float).resample('1H').mean().div(10),
           -WNDdf[6].loc[StartDate:EndDate].astype(float).resample('1H').mean().div(10),
           color='b', label='Wind Vector')

# Displaying the legend and adjusting layout
plt.legend(loc='best')
plt.tight_layout()  # Adjust the layout to prevent overlap

# Optionally, save the figure
if False:  # Set to True to save the figure
    filename = 'Modesto_' + pd.Timestamp.now().strftime('%Y-%m-%d_%H%M%S')
    location = 'graphs/Modesto_2019/' + filename
    plt.savefig(location)  # Save the plot

plt.show()

