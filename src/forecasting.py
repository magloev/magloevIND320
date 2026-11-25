import pandas as pd
import numpy as np

from river import linear_model
from river import preprocessing
from river import optim

def train_river(train_data, features, learning_rate=0.01):

    model = (
        preprocessing.StandardScaler()
        | linear_model.LinearRegression(
            optimizer=optim.SGD(
                lr=learning_rate
            )
        )
    )

    for _, row in train_data.iterrows():

        x = row[features].to_dict()
        y = float(row["fill_level"])

        model.learn_one(x, y)

    return model

def recursive_forecast(
    model,
    history,
    lags,
    horizon=12
):

    history = list(history)
    predictions = []

    for step in range(horizon):

        x = {
            f"lag_{lag}": history[-lag]
            for lag in lags
        }

        prediction = model.predict_one(x)

        predictions.append(prediction)
        history.append(prediction)

    return predictions

def recursive_forecast_short_weather(
    model,
    train_data,
    weather_history,
    reservoir_lags,
    weather_features,
    horizon=12
):

    history = train_data["fill_level"].tolist()
    predictions = []

    last_date = train_data["date"].iloc[-1]

    # Calculate historical averages for each week of the year
    climatology = weather_history.groupby(
        weather_history.index.isocalendar().week
    ).mean()

    for step in range(1, horizon + 1):

        forecast_date = last_date + pd.Timedelta(
            weeks=step
        )

        # Reservoir lag features
        x = {
            f"lag_{lag}": history[-lag]
            for lag in reservoir_lags
        }

        # Weather lag features
        for variable, lag in weather_features:

            weather_date = forecast_date - pd.Timedelta(
                weeks=lag
            )

            # Use actual weather if available
            if weather_date <= last_date:

                value = weather_history[variable].get(
                    weather_date, np.nan
                )

            else:
                value = np.nan

            # Estimate unavailable weather
            if pd.isna(value):

                week = weather_date.isocalendar().week

                value = climatology[variable].get(
                    week,
                    weather_history[variable].mean()
                )

                if pd.isna(value):
                    value = weather_history[variable].mean()

                if pd.isna(value):
                    raise ValueError(
                        f"No weather data available for {variable}."
                    )

            x[f"{variable}_lag_{lag}"] = value

        prediction = model.predict_one(x)

        predictions.append(prediction)
        history.append(prediction)

    return predictions

def forecast_reservoir(
    df,
    region="NO3",
    history_years=10,
    horizon=12,
    learning_rate=0.09,
    reservoir_lags=(1, 2, 4, 52),
    weather_features=(),
    end_date=None,
    training_start=None
):

    data = df.copy()

    # Validate selected parameters
    if history_years < 1 or horizon < 1:
        raise ValueError("History and horizon must be positive.")

    if not reservoir_lags or any(lag < 1 for lag in reservoir_lags):
        raise ValueError("Select valid reservoir lags.")

    if any(lag < 0 for _, lag in weather_features):
        raise ValueError("Weather lags cannot be negative.")

    if not np.isfinite(learning_rate) or learning_rate <= 0:
        raise ValueError("Learning rate must be positive.")

    # Select price area if the dataset contains multiple regions
    if "area_id" in data.columns:

        if "area_type" in data.columns:
            data = data[data["area_type"] == "EL"]

        area_ids = pd.to_numeric(
            data["area_id"].astype(str).str.replace(
                "NO", "", regex=False
            ),
            errors="coerce"
        )

        data = data[area_ids == int(region[2:])]

    if data.empty:
        raise ValueError(f"No data available for {region}.")

    # Prepare weekly time series
    data["date"] = pd.to_datetime(data["date"])
    data = data.sort_values("date").set_index("date")

    if data.index.has_duplicates:
        raise ValueError("Multiple observations per date.")

    if not (data.index.dayofweek == 6).all():
        raise ValueError("Weekly observations must be Sunday-dated.")

    data = data.asfreq("W-SUN")

    # Select the last available observation
    if end_date is not None:
        data = data.loc[:pd.Timestamp(end_date)]

    last_date = data["fill_level"].last_valid_index()

    if last_date is None:
        raise ValueError("No reservoir observations available.")

    data = data.loc[:last_date].copy()

    # Construct reservoir lag features
    features = []

    for lag in reservoir_lags:

        column = f"lag_{lag}"

        data[column] = data["fill_level"].shift(lag)
        features.append(column)

    # Construct optional weather lag features
    for variable, lag in weather_features:

        if variable not in data.columns:
            raise ValueError(
                f"Weather variable {variable} is unavailable."
            )

        column = f"{variable}_lag_{lag}"

        data[column] = data[variable].shift(lag)
        features.append(column)

    # Select training period
    forecast_start = last_date + pd.Timedelta(weeks=1)

    if training_start is None:
        train_start = forecast_start - pd.DateOffset(
            years=history_years
        )
    else:
        train_start = pd.Timestamp(training_start)

    train_data = data.loc[
        data.index >= train_start
    ].reset_index()

    train_clean = train_data.dropna(
        subset=features + ["fill_level"]
    )

    # Check that sufficient data is available
    history = data["fill_level"].tolist()

    if len(train_clean) < 2:
        raise ValueError("Insufficient training data.")

    if (
        len(history) < max(reservoir_lags)
        or pd.isna(history[-max(reservoir_lags):]).any()
    ):
        raise ValueError("Insufficient reservoir lag history.")

    # Train River model
    model = train_river(
        train_clean,
        features,
        learning_rate=learning_rate
    )

    # Recursive forecasting with optional weather
    if weather_features:

        weather_columns = list({
            variable for variable, lag in weather_features
        })

        weather_history = data[weather_columns]

        predictions = recursive_forecast_short_weather(
            model,
            data.reset_index(),
            weather_history,
            reservoir_lags,
            weather_features,
            horizon
        )

    # Recursive forecasting without weather
    else:

        predictions = recursive_forecast(
            model,
            history,
            reservoir_lags,
            horizon
        )

    # Check for numerical instability
    if not np.isfinite(predictions).all():
        raise ValueError("Forecast is numerically unstable.")

    # Create future dates
    forecast_dates = pd.date_range(
        start=forecast_start,
        periods=horizon,
        freq="W-SUN"
    )

    # Prepare forecasting results
    df_forecast = pd.DataFrame({
        "date": forecast_dates,
        "prediction": predictions
    })

    return train_data, df_forecast