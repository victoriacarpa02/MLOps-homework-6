import os
from datetime import datetime

import pandas as pd

from batch import get_input_path, get_output_path

import subprocess
import sys

from numpy.testing import assert_allclose


def dt(hour, minute, second=0):
    return datetime(2023, 1, 1, hour, minute, second)


def main():
    data = [
        (None, None, dt(1, 1), dt(1, 10)),
        (1, 1, dt(1, 2), dt(1, 10)),
        (1, None, dt(1, 2, 0), dt(1, 2, 59)),
        (3, 4, dt(1, 2, 0), dt(2, 2, 1)),
    ]

    columns = [
        "PULocationID",
        "DOLocationID",
        "tpep_pickup_datetime",
        "tpep_dropoff_datetime",
    ]

    df_input = pd.DataFrame(data, columns=columns)
    input_file = get_input_path(2023, 1)

    options = {
        "client_kwargs": {
            "endpoint_url": os.environ["S3_ENDPOINT_URL"],
        }
    }

    df_input.to_parquet(
        input_file,
        engine="pyarrow",
        compression=None,
        index=False,
        storage_options=options,
    )

    print("Test period: 2023-01")
    print("Input rows:", len(df_input))
    print("Input file:", input_file)

    output_file = get_output_path(2023, 1)

    subprocess.run(
        [sys.executable, "batch.py", "2023", "1"],
        check=True,
    )

    df_result = pd.read_parquet(
        output_file,
        engine="pyarrow",
        storage_options=options,
    )

    assert df_result.columns.tolist() == [
        "ride_id",
        "predicted_duration",
    ]
    assert len(df_result) == 2
    assert df_result["ride_id"].tolist() == [
        "2023/01_0",
        "2023/01_1",
    ]

    assert_allclose(
        df_result["predicted_duration"].to_numpy(),
        [23.19714924577506, 13.08010120625567],
        rtol=0,
        atol=1e-6,
    )

    print("Output rows:", len(df_result))
    print(
        "Q6 sum of predicted durations:",
        df_result["predicted_duration"].sum(),
    )
    print("Integration test PASSED")


if __name__ == "__main__":
    main()