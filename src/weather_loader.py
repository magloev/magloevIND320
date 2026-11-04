import json
from pathlib import Path
import pandas as pd

with open("data/weather/zone_coordinates.json", "r") as f:
    zone_coordinates = json.load(f)

def download_weather(region, start_date, end_date):
    """
    Download hourly ERA5 weather data for all sampled coordinates
    in a region, saving each completed batch as a CSV file.
    """

    # Look up sampled coordinates for the selected region
    coordinates = zone_coordinates[region]
    url = "https://archive-api.open-meteo.com/v1/archive"

    batch_size = 100
    weather_data = []

    # Create folder for the selected region and time interval
    folder = Path("data/weather") / f"{region.replace(' ', '')}_{start_date}_{end_date}"
    folder.mkdir(parents=True, exist_ok=True)

    # Loop through coordinates in batches of 10
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
            "hourly": ["temperature_2m", "precipitation"],
            "models": "era5",
            "timezone": "GMT"
        }

        # Download weather data for the batch
        responses = openmeteo.weather_api(url, params=params)

        batch_data = []

        # Process each location in the batch
        for j, response in enumerate(responses):

            hourly = response.Hourly()

            temperature = hourly.Variables(0).ValuesAsNumpy()
            precipitation = hourly.Variables(1).ValuesAsNumpy()

            # Construct DataFrame
            df = pd.DataFrame({
                "date": pd.date_range(
                    start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                    end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                    freq=pd.Timedelta(seconds=hourly.Interval()),
                    inclusive="left"
                ),
                "temperature_2m": temperature,
                "precipitation": precipitation
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

def aggregate_weather(region, start_date, end_date):
    """
    Load existing hourly regional averages if available.
    Otherwise download, aggregate and save weather data.
    """

    output_dir = Path("data/weather")
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{region}_{start_date}_{end_date}_average.csv"
    filepath = output_dir / filename

    # Load previously aggregated data
    if filepath.exists():
        print("Loading existing aggregated weather data")
        return pd.read_csv(filepath, parse_dates=["date"])

    # Download weather data if aggregated CSV is missing
    df = download_weather(region, start_date, end_date)

    # Calculate hourly regional averages
    df_average = (
        df.groupby("date")[["temperature_2m", "precipitation"]]
        .mean()
        .reset_index()
    )

    # Save aggregated data
    df_average.to_csv(filepath, index=False)

    return df_average