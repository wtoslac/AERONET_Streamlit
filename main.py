if aod_file is not None and wind_file is not None:
    # Read AOD data
    df_aod = pd.read_csv(aod_file, skiprows=6, parse_dates={'datetime': [0, 1]})
    datetime_utc = pd.to_datetime(df_aod["datetime"], format='%d:%m:%Y %H:%M:%S')
    datetime_pac = pd.to_datetime(datetime_utc).dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
    df_aod.set_index(datetime_pac, inplace=True)

    # Read Wind data and check column names
    df_wind = pd.read_csv(wind_file)
    st.write("Wind data columns:", df_wind.columns)  # Debug: Display column names
    if 'datetime' in df_wind.columns:
        df_wind['datetime'] = pd.to_datetime(df_wind['datetime']).dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
        df_wind.set_index('datetime', inplace=True)
    else:
        st.error("No 'datetime' column found in the wind data file.")

    # Plot AOD and wind data
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Plot AOD data on the primary y-axis
    ax1.plot(
        df_aod.loc[StartDateTime:EndDateTime, "AOD_380nm"].resample(SampleRate).mean(), 
        '.k', label="AOD_380nm"
    )
    ax1.plot(
        df_aod.loc[StartDateTime:EndDateTime, "AOD_500nm"].resample(SampleRate).mean(), 
        '.r', label="AOD_500nm"
    )
    ax1.plot(
        df_aod.loc[StartDateTime:EndDateTime, "AOD_870nm"].resample(SampleRate).mean(), 
        '.b', label="AOD_870nm"
    )
    ax1.set_ylim(AOD_min, AOD_max)
    ax1.set_ylabel("AOD")
    ax1.legend(loc="upper left")

    # Add secondary y-axis for wind data
    ax2 = ax1.twinx()
    ax2.plot(
        df_wind.loc[StartDateTime:EndDateTime, "wind_speed"].resample(SampleRate).mean(), 
        '-g', label="Wind Speed"
    )
    ax2.set_ylabel("Wind Speed (m/s)", color='green')
    ax2.tick_params(axis='y', colors='green')
    ax2.legend(loc="upper right")

    # Format x-axis
    ax1.xaxis.set_major_locator(mdates.DayLocator(interval=1, tz=pacific_tz))
    ax1.xaxis.set_minor_locator(mdates.HourLocator(interval=12, tz=pacific_tz))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    plt.gcf().autofmt_xdate()

    st.pyplot(fig)
