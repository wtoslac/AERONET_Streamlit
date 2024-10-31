import streamlit as st
import numpy as np
import plotly.express as px
import pandas as pd
from io import StringIO 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
import csv
siteName="Turlock CA USA"
SampleRate = "1h"
WindSampleRate = "3h"
StartDate='2023-10-07 00:00:00'
EndDate='2023-10-15 23:59:59'
AOD_min = 0.0
AOD_max = 0.3

file = st.file_uploader("Please choose a file")
df = pd.read_csv(file,skiprows = 6, parse_dates={'datetime':[0,1]})
datetime_utc=pd.to_datetime(df["datetime"], format='%d:%m:%Y %H:%M:%S')
datetime_pac= pd.to_datetime(datetime_utc).dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
df.set_index(datetime_pac, inplace = True)



#plt.figure(figsize=(20*graphScale,10*graphScale))
plt.plot(df.loc[StartDate:EndDate,"AOD_675nm"].resample(SampleRate).mean(),'.r',label="AOD_675nm-AOD")
plt.plot(df.loc[StartDate:EndDate,"AOD_500nm"].resample(SampleRate).mean(),'.g',label="AOD_500nm-AOD")
plt.plot(df.loc[StartDate:EndDate,"AOD_440nm"].resample(SampleRate).mean(),'.b',label="AOD_440nm-AOD")

#plot = px.line(df, x = 'datetime', y = ['AOD_500nm'])
#st.plotly_chart(plot)
