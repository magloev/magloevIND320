from src.weather_loader import download_weather, aggregate_weather


def download_forecast_weather(region, start_date, end_date):
    return download_weather(
        region, start_date, end_date,
        resolution="daily",
        n_locations=100
    )


def aggregate_forecast_weather(region, start_date, end_date,
                               allow_download=False):

    return aggregate_weather(
        region, start_date, end_date,
        allow_download=allow_download,
        resolution="daily",
        n_locations=100
    )