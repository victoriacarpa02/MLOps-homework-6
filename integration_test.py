import os
from datetime import datetime

import pandas as pd

from batch import get_input_path


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


if __name__ == "__main__":
    main()