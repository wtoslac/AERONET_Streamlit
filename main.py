import streamlit as st
import numpy as np
import plotly.express as px
import pandas as pd
from io import StringIO 
import numpy as np
import plotly.express as px

file = st.file_uploader("Please choose a file")
df= pd.read_csv(file)
plot = px.line(df, x = 'datetime', y = ['AOD_500nm'])
st.plotly_chart(plot)
 
plot = px.line(df, x = 'x', y = ['func1', 'func2', 'func3'])

st.plotly_chart(plot)
