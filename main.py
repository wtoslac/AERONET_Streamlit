import streamlit as st
import numpy as np
import plotly.express as px
import pandas as pd
from io import StringIO 

file = st.file_uploader("Please choose a file")
df = pd.read_csv(file,skiprows = 6, parse_dates={'datetime':[0,1]})
datetime_utc=pd.to_datetime(df["datetime"], format='%d:%m:%Y %H:%M:%S')
datetime_pac= pd.to_datetime(datetime_utc).dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
df.set_index(datetime_pac, inplace = True)

plot = px.line(df, x = 'datetime', y = ['AOD_500nm'])
st.plotly_chart(plot)
