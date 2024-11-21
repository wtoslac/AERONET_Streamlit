import streamlit as st
import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 
import matplotlib.dates as mdates

# Streamlit interface to upload files
st.title("AOD and Wind Data Visualization")

# File uploaders for AERONET and Wind Data
aeronet_file = st.file_uploader("Upload AERONET Data File (CSV)", type=["csv"])
wind_file = st.file_uploader("Upload Wind Data File (CSV)", type=["csv"])

# Date range picker for the plot
start_date = st.date_input("Start Date", pd.to_datetime('2019-06-11'))
end_date = st.date_input("End Date", pd.to_datetime('2019-06-13'))

# Sample rate selection for wind data
sample_rate = st.selectbox("Select Wind Sample Rate", ['1h', '6h', '12h', '24h'])
wind_sample_rate = sample_rate

# Check if both files are uploaded
if aeronet_file and wind_file:
    # Load AERONET data and convert to US/Pacific time
    df = pd.read_csv(aeronet_file, skiprows=6, parse_dates={'datetime': [0, 1]})
    datetime_utc = pd.to_datetime(df["datetime"], format='%d:%m:%Y %H:%M:%S')
    datetime_pac = pd.to_datetime(datetime_utc).dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
    df.set_index(datetime_pac, inplace=True)

    # Replace -999 values with NaN for AOD columns
    df['AOD_380nm-Total'].replace(-999.0, np.nan, inplace=True)
    df['AOD_440nm-Total'].replace(-999.0, np.nan, inplace=True)
    df['AOD_500nm-Total'].replace(-999.0, np.nan, inplace=True)
    df['AOD_675nm-Total'].replace(-999.0, np.nan, inplace=True)

    # Load wind data and convert to US/Pacific time
    Wdf = pd.read_csv(wind_file, parse_dates={'datetime': [1]}, low_memory=False)
    datetime_utc = pd.to_datetime(Wdf["datetime"], format='%d-%m-%Y %H:%M:%S')
    datetime_pac = pd.to_datetime(datetime_utc).dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
    Wdf.set_index(datetime_pac, inplace=True)

    # Process wind data: split the 'WND' column into components and filter for valid data
    WNDdf = Wdf.loc[start_date:end_date, 'WND'].str.split(pat=',', expand=True)
    WNDdf = WNDdf.loc[WNDdf[4] == '5']  # Valid observations
    WNDdf = WNDdf.loc[WNDdf[1] == '5']  # Further filter

    # Convert polar coordinates to Cartesian (X, Y components for wind)
    Xdata, Ydata = [], []
    for _, row in WNDdf.iterrows():
        Xdata.append(np.float64(row[3]) * np.sin(np.float64(row[0]) * (np.pi / 180)))  # Magnitude * sin(Theta)
        Ydata.append(np.float64(row[3]) * np.cos(np.float64(row[0]) * (np.pi / 180)))  # Magnitude * cos(Theta)

    WNDdf[5], WNDdf[6] = Xdata, Ydata  # Append Cartesian coordinates to the DataFrame

    # Create a figure with a single axis
    fig, ax = plt.subplots(figsize=(16 * 0.65, 9 * 0.65))

    # Format the x-axis with dates
    fig.autofmt_xdate()
    ax.set_title("Modesto 2019: AOD and Wind Speed")
    ax.grid(which='both', axis='both')
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1, tz='US/Pacific'))
    ax.xaxis.set_minor_locator(mdates.HourLocator(interval=3, tz='US/Pacific'))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))

    # Plot AOD data (AOD_500nm-Total)
    ax.set_ylabel("AOD_500nm-Total")
    ax.plot(df.loc[start_date:end_date, 'AOD_500nm-Total'].resample(wind_sample_rate).mean(), 'ok-', label='AOD_500nm-Total', figure=fig)

    # Add a second y-axis for the wind data
    ax2 = ax.twinx()
    ax2.spines['right'].set_position(('axes', 1.05))  # Adjust the position of the second y-axis
    ax2.set_ylabel('Wind Speed (m/s)')
    ax2.set_ylim(WNDdf[3].loc[start_date:end_date].astype(float).div(10).min() // 1, WNDdf[3].loc[start_date:end_date].astype(float).div(10).max() // 1)  # Auto scale based on wind speed
    ax2.set_ylim(1, 8)  # Manual scaling for the wind speed (optional)

    ax2.quiver(WNDdf[5].resample(wind_sample_rate).mean().index,
               np.sqrt((WNDdf[5].loc[start_date:end_date].astype(float).resample(wind_sample_rate).sum() /
                        WNDdf.loc[start_date:end_date].resample(wind_sample_rate).size()) ** 2 +
                       (WNDdf[6].loc[start_date:end_date].astype(float).resample(wind_sample_rate).sum() /
                        WNDdf.loc[start_date:end_date].resample(wind_sample_rate).size()) ** 2) / 10,
               -WNDdf[5].loc[start_date:end_date].astype(float).resample(wind_sample_rate).mean().div(10),
               -WNDdf[6].loc[start_date:end_date].astype(float).resample(wind_sample_rate).mean().div(10),
               color='b', label='Wind Vector')

    # Display legend and adjust the layout
    plt.legend(loc='best')
    plt.tight_layout()  # Ensures everything fits within the plot area

    # Render the plot in Streamlit
    st.pyplot(fig)

else:
    st.warning("Please upload both the AERONET and Wind Data CSV files.")
