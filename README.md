# Automatic Data Analysis

## Description

## Prerequisites

Whole solution (both app and execution runtime) relies on configuration file. It should be named `.env` and placed in the root directory. Its content should be as follows:

```
DATASET_PATH=<path to dataset>
SSH_HOST=<ssh_hostname, for local development 127.0.0.1>
SSH_PORT=<ssh_port>
SSH_USERNAME=<username>
SSH_PASSWORD=<password>
JUPYTER_HOST=<jupyter_hostname, for local development 127.0.0.1>
JUPYTER_PORT=<jupyter_port>
JUPYTER_NOTEBOOKS_PATH=<path to notebooks directory>
```

## How to run

1. Install requirements.txt (pip install -r requirements.txt).
2. Set OPENAI_API_KEY environment variable to your OpenAI API key.
3. Move/copy selected dataset in CSV format to the project directory. It should be named `data.csv`.
4. Run `python main.py` and follow the prompts.

## Execution runtime

### Python container

Execution runtime is a Debian based docker container with Python 3.10 and ssh server (for remote code execution).
On the first execution, to create image run `docker compose -f python-runtime.docker-compose.yml build`.
Then run `docker compose -f python-runtime.docker-compose.yml up` to start the container. It will be available on port <ssh_port> (ssh -p <ssh_port> <username>@<ssh_hostname>).

### Jupyter notebook container

Jupyter notebook container is an official Jupyter docker image [jupyter/datascience-notebook](https://hub.docker.com/r/jupyter/datascience-notebook) with python 3.10 kernel installed.
You simply run `docker compose -f jupyter-notebook.docker-compose.yml up` to start the container. It will be available on port <jupyter_port> (http://<jupyter_hostname>:<jupyter_port>).
Note: Notebooks will be saved in the directory specified in the configuration file.


