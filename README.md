# Automatic Data Analysis

## Description


## How to run

1. Install requirements.txt (pip install -r requirements.txt).
2. Set OPENAI_API_KEY environment variable to your OpenAI API key.
3. Move/copy selected dataset in CSV format to the project directory. It should be named `data.csv`.
4. Run `python main.py` and follow the prompts.

## Execution runtime

Execution runtime is a Debian based docker container with Python 3.10 and ssh server (for remote code execution).
Since build is parametrized, before running it one has to create an *.env* file in root directory. It should have the following content:
```
SSH_USERNAME=<username>
SSH_PASSWORD=<password>
```

On the first execution, to create image run `docker compose build`.
Then run `docker compose up` to start the container. It will be available on port 8022 (ssh -p 8022 <username>@localhost).
