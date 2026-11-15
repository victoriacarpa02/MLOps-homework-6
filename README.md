# MLOps Zoomcamp Homework 6

I added unit and integration tests to the batch prediction script. I used LocalStack to test reading and writing Parquet files in S3.

## Answers

| Question | Answer |
| :--- | :--- |
| Q1. Main block | `if __name__ == "__main__":` |
| Q2. Test package file | `__init__.py` |
| Q3. Rows after preparation | 2 |
| Q4. LocalStack CLI option | `--endpoint-url` |
| Q5. Input file size | 3620 bytes |
| Q6. Sum of predicted durations | 36.28 |

The exact sum was `36.27725045203073`.

## What I tested

The unit test checks duration filtering, missing location IDs and conversion of IDs to strings.

The integration test uploads four sample rows to S3, runs `batch.py` and reads the output from S3. It checks the columns, two remaining rows, ride IDs and predicted durations.

Both tests passed.

## Setup

I used Windows PowerShell, Python 3.10, uv and Docker Desktop.

Run these commands from the project folder:

```powershell
uv venv --python 3.10 .venv

$env:PIPENV_VENV_IN_PROJECT = "1"
$env:PIPENV_IGNORE_VIRTUALENVS = "1"

uvx --python 3.10 pipenv==2024.4.1 sync --dev
```

Dependencies are recorded in `Pipfile.lock`. I pinned Pipenv because the newer version failed with Python 3.10.

## Run all tests

Start Docker Desktop, then run:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\run_tests.ps1
$LASTEXITCODE
```

The runner sets the environment variables, runs the unit test, starts LocalStack, waits for S3 and creates the bucket if needed. It then runs the integration test.

Expected results:

```text
1 passed
Integration test PASSED
All tests PASSED
0
```

LocalStack stays running after the tests.

## Run only the unit test

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_batch.py -v
```

This test does not need Docker or S3.

## Test files in S3

The bucket is `nyc-duration`.

Input: `s3://nyc-duration/in/2023-01.parquet`

Output: `s3://nyc-duration/out/2023-01.parquet`

Check both files after running the tests:

```powershell
docker compose exec localstack aws --endpoint-url=http://localhost:4566 s3 ls s3://nyc-duration/ --recursive
```

## Stop LocalStack

```powershell
docker compose down
```

The next test run recreates the bucket and test data.