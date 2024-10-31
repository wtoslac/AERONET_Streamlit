import streamlit as st
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

siteName="Turlock CA USA"
SampleRate = "1h"
StartDate = st.date_input("StartDate", datetime.date(2023, 1, 6))
EndDate = st.date_input("EndDate", datetime.date(2023, 1, 6))
#DateTime s = ...;
TimeSpan ts = new TimeSpan(00, 00, 00);
#s = s.Date + ts;
StartDate= StartDate+ts
#EndDate=EndDate+'23:59:59'
AOD_min = 0.0
AOD_max = 0.3

file = st.file_uploader("Please choose a file")
df = pd.read_csv(file,skiprows = 6, parse_dates={'datetime':[0,1]})
datetime_utc=pd.to_datetime(df["datetime"], format='%d:%m:%Y %H:%M:%S')
datetime_pac= pd.to_datetime(datetime_utc).dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
df.set_index(datetime_pac, inplace = True)

#plt.figure(figsize=(20*graphScale,10*graphScale))
#plt.plot(df.loc[StartDate:EndDate,"AOD_675nm"].resample(SampleRate).mean(),'.r',label="AOD_675nm-AOD")
plt.plot(df.loc[StartDate:EndDate,"AOD_500nm"].resample(SampleRate).mean(),'.k',label="AOD_500nm-AOD")
#plt.plot(df.loc[StartDate:EndDate,"AOD_440nm"].resample(SampleRate).mean(),'.b',label="AOD_440nm-AOD")

plt.gcf().autofmt_xdate()
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1, tz='US/Pacific'))
plt.gca().xaxis.set_minor_locator(mdates.HourLocator(interval=12, tz='US/Pacific'))
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
#Change the range on Y here if needed
plt.ylim(AOD_min,AOD_max)
plt.legend()
st.pyplot(plt.gcf())
