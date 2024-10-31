import pandas as pd
import streamlit as st
from mitosheet.streamlit.v1 import spreadsheet

# Create a dataframe with pandas (you can pass any pandas dataframe)
dataframe = pd.DataFrame({'A': [1, 2, 3]})

# Display the dataframe in a Mito spreadsheet
final_dfs, code = spreadsheet(dataframe)

# Display the final dataframes created by editing the Mito component
# This is a dictionary from dataframe name -> dataframe
st.write(final_dfs)

# Display the code that corresponds to the script
st.code(code)
