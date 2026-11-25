# IND320 – Data to Decision

## Project introduction

This project was developed as part of the IND320 – Data to Decision course at NMBU.

The project investigates Norwegian reservoir filling levels, electricity transfers and meteorological conditions. The aim is to combine data from different sources and develop an interactive application for data exploration, statistical analysis and forecasting.

## Data sources

- **NVE Magasinstatistikk:** Historical weekly reservoir filling levels.
- **ENTSO-E Transparency Platform:** Electricity transfers between Norwegian and European bidding zones.
- **Open-Meteo:** Historical temperature and precipitation data.
- **Norges Bank:** Historical exchange-rate data investigated in Task 4.

## Project development

### Part 1 – Reservoir data

Retrieval, preparation and visualisation of Norwegian reservoir data from NVE. Initial development and deployment of the Streamlit application.

### Part 2 – Electricity transfers

Retrieval and processing of electricity transfer data from ENTSO-E. Used PySpark, Cassandra and MongoDB for data processing and storage.

### Part 3 – Time series analysis

Integration of meteorological data from Open-Meteo and implementation of statistical methods for time series analysis and anomaly detection, including STL decomposition, spectrograms, SATV/SPC and Local Outlier Factor.

### Part 4 – Interactive analysis and forecasting

Further development of the Streamlit application with:

- Interactive geographical map.
- Shared geographical and temporal selections.
- Weather data management and incremental downloads.
- Interactive Plotly visualisations.
- Sliding Window Correlation between weather and reservoir filling changes.
- Configurable recursive reservoir forecasting using River.
- Animated forecast visualisation.
- Improved waiting time through caching and reuse of previously downloaded data.

## Application structure

| Section | Pages |
|---|---|
| Introduction | Home, Interactive Map |
| Data Overview | Reservoir Data, Electricity Transfers, Weather Data |
| Data Analysis | Anomaly Detection, Time Series Analysis, Sliding Window Correlation |
| Prediction | Reservoir Forecasting |

## Technologies

Python, Pandas, NumPy, SciPy, Scikit-learn, Statsmodels, River, PySpark, Cassandra, MongoDB, Streamlit, Plotly and GeoJSON.

## Running the application locally

Install the application dependencies:

```bash
pip install -r requirements.txt
```

Run the Streamlit application:

```bash
streamlit run app.py
```

Access to the electricity transfer data requires MongoDB credentials configured in `.streamlit/secrets.toml`.

## Limitations

Weather data availability depends on the publication delay of Open-Meteo's historical data. Meteorological analysis is currently limited to Norwegian electricity price areas.

The forecasting model is sensitive to the selected parameters and training period. Predictions should therefore be considered exploratory rather than operational forecasts.
