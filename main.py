import streamlit as st
import numpy as np
import plotly.express as px
import pandas as pd
 
x = np.linspace(0, 5)
 
y1 = np.sin(x - 1) + np.cos(x)
y2 = np.sin(x * x) * np.exp(-0.1 *  x * x)
y3 = np.cos(x * x) * np.exp(0.1 * x)
 
df = pd.DataFrame(dict(x = x, func1 = y1, func2 = y2, func3 = y3))
 
plot = px.line(df, x = 'x', y = ['func1', 'func2', 'func3'])

st.plotly_chart(plot)
