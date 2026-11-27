import json
from pathlib import Path
import pandas as pd
import openmeteo_requests
import requests_cache
from retry_requests import retry
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WEATHER_DIR = PROJECT_ROOT / "data" / "weather"
FORECAST_WEATHER_DIR = PROJECT_ROOT / "data" / "forecast_weather"

# Initialize Open-Meteo API client
cache_session = requests_cache.CachedSession(
    str(PROJECT_ROOT / ".cache"),
    expire_after=3600
)
retry_session = retry(cache_session, retries=2, backoff_factor=0.5)
openmeteo = openmeteo_requests.Client(session=retry_session)

with open(PROJECT_ROOT / "data" / "weather" / "zone_coordinates.json", "r") as f:
    zone_coordinates = json.load(f)

def download_weather(region, start_date, end_date,
                     resolution="hourly", n_locations=None):

    # Select coordinates
    all_coordinates = zone_coordinates[region]

    if resolution not in ["hourly", "daily"]:
        raise ValueError("Resolution must be hourly or daily.")

    if n_locations is None:
        n_locations = 100 if resolution == "daily" else len(all_coordinates)

    if not 0 < n_locations <= len(all_coordinates):
        raise ValueError("Invalid number of sampling locations.")

    coordinates = all_coordinates[:n_locations]

    url = "https://archive-api.open-meteo.com/v1/archive"

    # Settings based on temporal resolution
    if resolution == "hourly":
        variables = ["temperature_2m", "precipitation"]
        batch_size = 100
    else:
        variables = ["temperature_2m_mean", "precipitation_sum"]
        batch_size = 50

    # Preserve existing storage structure
    region_name = region.replace(" ", "")

    if resolution == "hourly" and n_locations == len(all_coordinates):
        folder = WEATHER_DIR / f"{region_name}_{start_date}_{end_date}"

    elif resolution == "daily" and n_locations == 100:
        folder = FORECAST_WEATHER_DIR / f"daily_{region_name}_{start_date}_{end_date}"

    else:
        folder = WEATHER_DIR / f"{resolution}_{n_locations}_{region_name}_{start_date}_{end_date}"

    folder.mkdir(parents=True, exist_ok=True)

    weather_data = []

    # Download coordinates in batches
    for i in range(0, len(coordinates), batch_size):

        batch = coordinates[i:i + batch_size]
        batch_file = folder / f"batch_{i:04d}.csv"

        # Reuse previously downloaded batches
        if batch_file.exists():
            print(f"Loading saved batch {i}")
            df = pd.read_csv(batch_file, parse_dates=["date"])
            weather_data.append(df)
            continue

        longitudes = [lon for lon, lat in batch]
        latitudes = [lat for lon, lat in batch]

        params = {
            "latitude": latitudes,
            "longitude": longitudes,
            "start_date": start_date,
            "end_date": end_date,
            resolution: variables,
            "models": "era5",
            "timezone": "GMT"
        }

        responses = openmeteo.weather_api(
            url,
            params=params,
            timeout=120
        )

        batch_data = []

        # Process each location
        for j, response in enumerate(responses):

            if resolution == "hourly":
                data = response.Hourly()
            else:
                data = response.Daily()

            df = pd.DataFrame({
                "date": pd.date_range(
                    start=pd.to_datetime(data.Time(), unit="s", utc=True),
                    end=pd.to_datetime(data.TimeEnd(), unit="s", utc=True),
                    freq=pd.Timedelta(seconds=data.Interval()),
                    inclusive="left"
                ),
                variables[0]: data.Variables(0).ValuesAsNumpy(),
                variables[1]: data.Variables(1).ValuesAsNumpy()
            })

            lon, lat = batch[j]

            df["region"] = region
            df["location_id"] = i + j
            df["latitude"] = lat
            df["longitude"] = lon

            batch_data.append(df)

        df_batch = pd.concat(batch_data, ignore_index=True)

        df_batch.to_csv(batch_file, index=False)

        weather_data.append(df_batch)

        print(
            f"Saved {min(i + batch_size, len(coordinates))} "
            f"/ {len(coordinates)} locations"
        )

    return pd.concat(weather_data, ignore_index=True)

def weather_cache_settings(region, resolution, n_locations):

    if n_locations is None:
        n_locations = (
            100 if resolution == "daily"
            else len(zone_coordinates[region])
        )

    if resolution == "hourly":
        variables = ["temperature_2m", "precipitation"]

    elif resolution == "daily":
        variables = ["temperature_2m_mean", "precipitation_sum"]

    else:
        raise ValueError("Invalid resolution.")

    # Preserve existing aggregated CSV files
    if resolution == "hourly" and n_locations == len(zone_coordinates[region]):
        folder = WEATHER_DIR
        filename = f"{region}_{{start}}_{{end}}_average.csv"

    elif resolution == "daily" and n_locations == 100:
        folder = FORECAST_WEATHER_DIR / "average"
        filename = f"{region}_{{start}}_{{end}}_daily_average.csv"

    else:
        folder = WEATHER_DIR / "average"
        filename = (
            f"{resolution}_{n_locations}_{region}_"
            "{start}_{end}_average.csv"
        )

    return folder, filename, variables

def load_cached_weather(region, start_date, end_date,
                        resolution="daily", n_locations=None):

    folder, filename, variables = weather_cache_settings(
        region, resolution, n_locations
    )

    start = pd.to_datetime(start_date, utc=True).normalize()
    end = pd.to_datetime(end_date, utc=True).normalize()

    frequency = "D" if resolution == "daily" else "h"

    expected_dates = pd.date_range(
        start,
        end + pd.Timedelta(days=1),
        freq=frequency,
        inclusive="left"
    )

    files = sorted(folder.glob(
        filename.format(start="*", end="*")
    ))

    weather_data = []

    for file in files:
        df = pd.read_csv(file)
        df["date"] = pd.to_datetime(df["date"], utc=True)

        df = df[df["date"].isin(expected_dates)]

        if not df.empty:
            weather_data.append(df)

    if weather_data:
        df_average = (
            pd.concat(weather_data, ignore_index=True)
            .groupby("date", as_index=False)
            .last()
            .sort_values("date")
            .reset_index(drop=True)
        )
    else:
        df_average = pd.DataFrame(columns=["date"] + variables)

    missing_dates = expected_dates.difference(df_average["date"])

    return df_average, missing_dates

def get_incomplete_dates(df_average, missing_dates, variables):

    missing_values = df_average.loc[
        df_average[variables].isna().any(axis=1),
        "date"
    ]

    if not missing_values.empty:
        missing_dates = missing_dates.union(
            pd.DatetimeIndex(missing_values)
        )

    return missing_dates

def aggregate_weather(region, start_date, end_date,
                      allow_download=False,
                      resolution="hourly", n_locations=None):

    folder, filename, variables = weather_cache_settings(
        region, resolution, n_locations
    )

    df_average, missing_dates = load_cached_weather(
        region, start_date, end_date,
        resolution, n_locations
    )
    missing_dates = get_incomplete_dates(
        df_average, missing_dates, variables
    )

    if len(missing_dates) == 0:
        return df_average

    if not allow_download:
        raise FileNotFoundError(
            f"Missing {len(missing_dates)} {resolution} observations."
        )

    folder.mkdir(parents=True, exist_ok=True)

    # Group consecutive missing days
    missing_days = pd.Series(
        missing_dates.normalize().unique().sort_values()
    )

    missing_groups = missing_days.groupby(
        (missing_days.diff().dt.days != 1).cumsum()
    )

    for _, dates in missing_groups:

        missing_start = dates.iloc[0].strftime("%Y-%m-%d")
        missing_end = dates.iloc[-1].strftime("%Y-%m-%d")

        df = download_weather(
            region,
            missing_start,
            missing_end,
            resolution,
            n_locations
        )

        df_new = (
            df.groupby("date")[variables]
            .mean()
            .reset_index()
        )

        filepath = folder / filename.format(
            start=missing_start,
            end=missing_end
        )

        df_new.to_csv(filepath, index=False)

    # Reload the complete dataset
    df_average, missing_dates = load_cached_weather(
        region, start_date, end_date,
        resolution, n_locations
    )
    missing_dates = get_incomplete_dates(
        df_average, missing_dates, variables
    )

    if len(missing_dates) > 0:
        raise FileNotFoundError(
            f"Still missing {len(missing_dates)} observations after download."
        )

    return df_average