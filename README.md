# Automatic Data Analysis

## Description

## Prerequisites

Whole solution (both app and execution runtime) relies on configuration file. It should be named `.env` and placed in the root directory. Its content should be as follows:

```
DATASET_PATH=<path to dataset>
SSH_HOST=<hostname, for local development 127.0.0.1>
SSH_PORT=<port>
SSH_USERNAME=<username>
SSH_PASSWORD=<password>
```

## How to run

1. Install requirements.txt (pip install -r requirements.txt).
2. Set OPENAI_API_KEY environment variable to your OpenAI API key.
3. Move/copy selected dataset in CSV format to the project directory. It should be named `data.csv`.
4. Run `python main.py` and follow the prompts.

## Execution runtime

Execution runtime is a Debian based docker container with Python 3.10 and ssh server (for remote code execution).
On the first execution, to create image run `docker compose build`.
Then run `docker compose up` to start the container. It will be available on port 8022 (ssh -p 8022 <username>@localhost).
