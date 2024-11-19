import pandas as pd
import streamlit as st

# File upload
file = st.file_uploader("Upload the Level 1.5 Data from AERONET")
if file is not None:
    # Load the data
    df = pd.read_csv(file, skiprows=6)

    # Extract the column names corresponding to wavelengths
    wavelength_columns = [col for col in df.columns if "AOD_" in col]

    # Count non-NaN entries for each wavelength
    data_counts = {col: df[col].count() for col in wavelength_columns}

    # Determine the wavelength with the most data
    max_wavelength = max(data_counts, key=data_counts.get)
    max_count = data_counts[max_wavelength]

    # Display results
    st.write("Wavelength Data Counts:")
    st.write(data_counts)
    st.write(f"The wavelength with the most data is **{max_wavelength}** with **{max_count}** valid data points.")

