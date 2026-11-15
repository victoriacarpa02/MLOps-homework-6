import pickle
import sys
from pathlib import Path

import pandas as pd
import os


def get_input_path(year, month):
    default_pattern = (
        "https://d37ci6vzurychx.cloudfront.net/trip-data/"
        "yellow_tripdata_{year:04d}-{month:02d}.parquet"
    )
    pattern = os.getenv("INPUT_FILE_PATTERN", default_pattern)
    return pattern.format(year=year, month=month)


def prepare_data(df, categorical):
    df = df.copy()

    df["duration"] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    df["duration"] = df.duration.dt.total_seconds() / 60

    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()

    df[categorical] = (
        df[categorical].fillna(-1).astype("int").astype("str")
    )

    return df


def read_data(filename, categorical):
    endpoint_url = os.getenv("S3_ENDPOINT_URL")

    if endpoint_url and str(filename).startswith("s3://"):
        options = {
            "client_kwargs": {
                "endpoint_url": endpoint_url,
            }
        }
        df = pd.read_parquet(filename, storage_options=options)
    else:
        df = pd.read_parquet(filename)

    return prepare_data(df, categorical)


def get_output_path(year, month):
    default_pattern = "output/yellow_tripdata_{year:04d}-{month:02d}.parquet"
    pattern = os.getenv("OUTPUT_FILE_PATTERN", default_pattern)
    return pattern.format(year=year, month=month)


def save_data(df, filename):
    options = None
    endpoint_url = os.getenv("S3_ENDPOINT_URL")

    if str(filename).startswith("s3://"):
        if endpoint_url:
            options = {
                "client_kwargs": {
                    "endpoint_url": endpoint_url,
                }
            }
    else:
        Path(filename).parent.mkdir(parents=True, exist_ok=True)

    df.to_parquet(
        filename,
        engine="pyarrow",
        index=False,
        storage_options=options,
    )


def main(year, month):
    categorical = ["PULocationID", "DOLocationID"]

    input_file = get_input_path(year, month)

    output_file = get_output_path(year, month)

    with open("model.bin", "rb") as f_in:
        dv, lr = pickle.load(f_in)

    df = read_data(input_file, categorical)
    df["ride_id"] = f"{year:04d}/{month:02d}_" + df.index.astype("str")

    dicts = df[categorical].to_dict(orient="records")
    X_val = dv.transform(dicts)
    y_pred = lr.predict(X_val)

    df_result = pd.DataFrame({
        "ride_id": df["ride_id"],
        "predicted_duration": y_pred,
    })

    save_data(df_result, output_file)

    print(f"Period: {year:04d}-{month:02d}")
    print("Predictions:", len(y_pred))
    print("Mean predicted duration:", y_pred.mean())
    print("Output file:", output_file)


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]))