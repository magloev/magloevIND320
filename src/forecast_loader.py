import json
from pathlib import Path

import pandas as pd
import openmeteo_requests
import requests_cache
from retry_requests import retry


# Project directories
PROJECT_ROOT = Path(__file__).resolve().parent.parent
FORECAST_WEATHER_DIR = PROJECT_ROOT / "data" / "forecast_weather"
WEATHER_DIR = PROJECT_ROOT / "data" / "weather"


# Initialize Open-Meteo API client
cache_session = requests_cache.CachedSession(
    str(PROJECT_ROOT / ".cache"),
    expire_after=3600
)

retry_session = retry(
    cache_session,
    retries=5,
    backoff_factor=0.2
)

openmeteo = openmeteo_requests.Client(session=retry_session)


# Load sampled coordinates
with open(WEATHER_DIR / "zone_coordinates.json", "r", encoding="utf-8") as f:
    zone_coordinates = json.load(f)


def download_forecast_weather(region, start_date, end_date):
    """
    Download daily ERA5 weather data for all sampled coordinates
    in a region, saving each completed batch as a CSV file.
    """

    # Look up sampled coordinates for the selected region
    coordinates = zone_coordinates[region]
    url = "https://archive-api.open-meteo.com/v1/archive"

    batch_size = 50
    weather_data = []

    # Create folder for the selected region and time interval
    folder = FORECAST_WEATHER_DIR / f"daily_{region.replace(' ', '')}_{start_date}_{end_date}"
    folder.mkdir(parents=True, exist_ok=True)

    coordinates = zone_coordinates[region][:100]
    
    # Loop through coordinates in batches of 50
    for i in range(0, len(coordinates), batch_size):

        batch = coordinates[i:i + batch_size]
        batch_file = folder / f"batch_{i:04d}.csv"

        # Load previously downloaded batches
        if batch_file.exists():
            print(f"Loading saved batch {i}")
            df = pd.read_csv(batch_file, parse_dates=["date"])
            weather_data.append(df)
            continue

        # Extract latitude and longitude lists
        longitudes = [lon for lon, lat in batch]
        latitudes = [lat for lon, lat in batch]

        params = {
            "latitude": latitudes,
            "longitude": longitudes,
            "start_date": start_date,
            "end_date": end_date,
            "daily": ["temperature_2m_mean", "precipitation_sum"],
            "models": "era5",
            "timezone": "GMT"
        }

        # Download weather data for the batch
        responses = openmeteo.weather_api(url, params=params)

        batch_data = []

        # Process each location in the batch
        for j, response in enumerate(responses):

            daily = response.Daily()

            temperature = daily.Variables(0).ValuesAsNumpy()
            precipitation = daily.Variables(1).ValuesAsNumpy()

            # Construct DataFrame
            df = pd.DataFrame({
                "date": pd.date_range(
                    start=pd.to_datetime(daily.Time(), unit="s", utc=True),
                    end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
                    freq=pd.Timedelta(seconds=daily.Interval()),
                    inclusive="left"
                ),
                "temperature_2m_mean": temperature,
                "precipitation_sum": precipitation
            })

            # Add location information
            lon, lat = batch[j]

            df["region"] = region
            df["location_id"] = i + j
            df["latitude"] = lat
            df["longitude"] = lon

            batch_data.append(df)

        # Combine data from the current batch
        df_batch = pd.concat(batch_data, ignore_index=True)

        # Save completed batch as CSV
        df_batch.to_csv(batch_file, index=False)

        weather_data.append(df_batch)

        print(
            f"Saved {min(i + batch_size, len(coordinates))} "
            f"/ {len(coordinates)} locations"
        )

    # Combine all batches into one DataFrame
    return pd.concat(weather_data, ignore_index=True)



def aggregate_forecast_weather(region, start_date, end_date, allow_download=False):
    """
    Load and combine existing daily regional averages.
    Download missing data only if allowed.
    """

    output_dir = FORECAST_WEATHER_DIR / "average"
    output_dir.mkdir(parents=True, exist_ok=True)

    start = pd.Timestamp(start_date, tz="UTC")
    end = pd.Timestamp(end_date, tz="UTC")

    # Find existing aggregated CSV files for this region
    files = list(output_dir.glob(f"{region}_*_daily_average.csv"))

    weather_data = []

    for file in files:
        df = pd.read_csv(file, parse_dates=["date"])

        # Keep only dates within the requested interval
        df = df[(df["date"] >= start) & (df["date"] <= end)]

        if not df.empty:
            weather_data.append(df)

    if weather_data:
        df_average = (
            pd.concat(weather_data, ignore_index=True)
            .drop_duplicates(subset="date")
            .sort_values("date")
            .reset_index(drop=True)
        )
    else:
        df_average = pd.DataFrame(
            columns=["date", "temperature_2m_mean", "precipitation_sum"]
        )

    # Check which dates are missing
    expected_dates = pd.date_range(start, end, freq="D")
    missing_dates = expected_dates.difference(df_average["date"])

    if len(missing_dates) > 0:
        if not allow_download:
            raise FileNotFoundError(
                f"Missing {len(missing_dates)} days of weather data."
            )

        # Download and aggregate missing date intervals
        missing_groups = (
            pd.Series(missing_dates)
            .groupby((pd.Series(missing_dates).diff().dt.days != 1).cumsum())
        )

        for _, dates in missing_groups:
            missing_start = dates.iloc[0].strftime("%Y-%m-%d")
            missing_end = dates.iloc[-1].strftime("%Y-%m-%d")

            df = download_forecast_weather(
                region, missing_start, missing_end
            )

            df_new = (
                df.groupby("date")[["temperature_2m_mean", "precipitation_sum"]]
                .mean()
                .reset_index()
            )

            # Save only newly downloaded data
            filename = f"{region}_{missing_start}_{missing_end}_daily_average.csv"
            df_new.to_csv(output_dir / filename, index=False)

            df_average = pd.concat([df_average, df_new], ignore_index=True)

        df_average = (
            df_average.drop_duplicates(subset="date")
            .sort_values("date")
            .reset_index(drop=True)
        )

    return df_average