import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# User Inputs
filename = input("Enter the filename for AOD data: ")
windfile = input("Enter the filename for wind data: ")
StartDate = input("Enter the start date (YYYY-MM-DD HH:MM:SS): ")
EndDate = input("Enter the end date (YYYY-MM-DD HH:MM:SS): ")
sampleRate = input("Enter the sampling rate (e.g., '1h', '1d'): ")

# Load AOD Data
df = pd.read_csv(filename, skiprows=6, parse_dates={'datetime': [0, 1]})
datetime_utc = pd.to_datetime(df["datetime"], format='%d:%m:%Y %H:%M:%S')
datetime_pac = datetime_utc.dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
df.set_index(datetime_pac, inplace=True)

# Process AOD Data
AODTotalColumns = range(3, 173, 8)
df['AOD_500nm-Total'].replace(-999.0, np.nan, inplace=True)

# Load Wind Data
Wdf = pd.read_csv(windfile, parse_dates={'datetime': [1]}, low_memory=False)
datetime_utc = pd.to_datetime(Wdf["datetime"], format='%d-%m-%Y %H:%M:%S')
datetime_pac = datetime_utc.dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
Wdf.set_index(datetime_pac, inplace=True)
WNDdf = Wdf.loc[StartDate:EndDate, 'WND'].str.split(pat=',', expand=True)

# Extract and Convert Wind Data to Cartesian Coordinates
WNDdf[3] = pd.to_numeric(WNDdf[3], errors='coerce')  # Wind speed
WNDdf[0] = pd.to_numeric(WNDdf[0], errors='coerce')  # Wind direction (degrees)
WNDdf['x'] = WNDdf[3] * np.sin(np.radians(WNDdf[0]))  # x-component
WNDdf['y'] = WNDdf[3] * np.cos(np.radians(WNDdf[0]))  # y-component

# Load Temperature Data
Tdf = Wdf.loc[StartDate:EndDate, 'TMP'].str.split(pat=',', expand=True)
Tdf.replace('+9999', np.nan, inplace=True)

# Black-and-White Graph
fig, ax = plt.subplots(figsize=(10, 6))
fig.autofmt_xdate()
ax.set_title("AOD and Wind Data (Black & White)")
ax.set_ylabel("AOD_500nm-Total")
ax.plot(df.loc[StartDate:EndDate, 'AOD_500nm-Total']
        .resample(sampleRate).mean(), 'ok-', label='AOD_500nm-Total')

# Wind Arrows (B&W)
ax.quiver(
    WNDdf.index,
    np.zeros_like(WNDdf['x']),
    -WNDdf['x'].resample(sampleRate).mean(),
    -WNDdf['y'].resample(sampleRate).mean(),
    color='black', label='Wind Vector'
)
ax.legend()
plt.tight_layout()
plt.show()

# Colored Graph
fig, ax = plt.subplots(figsize=(10, 6))
fig.autofmt_xdate()
ax.set_title("AOD, Temperature, and Wind Data (Colored)")
ax.set_ylabel("AOD_500nm-Total")
ax.plot(df.loc[StartDate:EndDate, 'AOD_500nm-Total']
        .resample(sampleRate).mean(), 'o-', color='blue', label='AOD_500nm-Total')

# Temperature Data
ax2 = ax.twinx()
ax2.set_ylabel('Temperature (°C)')
ax2.plot(Tdf[0].astype(float).resample(sampleRate).mean() / 10, '.-', color='red', label='Temperature')

# Wind Arrows (Colored)
ax.quiver(
    WNDdf.index,
    np.zeros_like(WNDdf['x']),
    -WNDdf['x'].resample(sampleRate).mean(),
    -WNDdf['y'].resample(sampleRate).mean(),
    color='green', label='Wind Vector'
)

ax.legend(loc='upper left')
plt.tight_layout()
plt.show()
