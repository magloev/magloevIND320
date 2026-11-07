This repository contains the project for **IND320 – Data to Decision**.

The goal of the project is to develop a data pipeline for collecting, processing, storing, analyzing, and visualizing energy-related data, making it easier to explore and understand Norwegian and European electricity systems.

The project consists of three main components:

1. **Norwegian Reservoir Data (NVE):** Processing and visualizing historical reservoir filling levels across different geographical areas in Norway.
2. **European Electricity Transfers (ENTSO-E):** Retrieving and processing cross-border electricity flow data, using Apache Spark and Cassandra for data processing and storage, MongoDB for application data access, and Streamlit for visualization.
3. **Weather and Statistical Analysis (Open-Meteo):** Collecting and aggregating historical ERA5 temperature and precipitation data, applying DCT/SPC and LOF for anomaly detection, and STL and STFT for reservoir time-series analysis.

The interactive Streamlit application provides visualizations of reservoir filling levels, electricity transfers, weather anomalies, and time-series patterns, allowing users to explore selected areas, connections, and time periods.

For this project I have used: Python, Pandas, PySpark, Cassandra, MongoDB, Streamlit, NumPy, SciPy, Scikit-learn, Statsmodels, and Open-Meteo.
