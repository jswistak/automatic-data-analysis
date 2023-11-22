# Automatic Data Analysis

### [Code documentation (pdoc3)](https://jswistak.github.io/automatic-data-analysis)

## Description

## Prerequisites

Whole solution (both app and execution runtime) relies on configuration file (for local use). It should be named `.env` and placed in the root directory. Its content should be as follows:

```
DATASET_PATH=<path to dataset>

# python-ssh-runtime
SSH_HOST=<ssh_hostname, for local development 127.0.0.1>
SSH_PORT=<ssh_port>
SSH_USERNAME=<username>
SSH_PASSWORD=<password>

# jupyter-notebook-runtime
JUPYTER_HOST=<jupyter_hostname, for local development 127.0.0.1>
JUPYTER_PORT=<jupyter_port>
JUPYTER_TOKEN=<token_used_later_for_authentication>

# apache-zeppelin-runtime
ZEPPELIN_HOST=<zeppelin_hostname, for local development 127.0.0.1>
ZEPPELIN_PORT=8080
```

## How to run

0. Run execution runtime if using local one (see Execution runtime section).
1. Install requirements.txt (pip install -r requirements.txt).
2. Set OPENAI_API_KEY environment variable to your OpenAI API key.
3. Move/copy selected dataset in CSV format to the project directory. It should be named `data.csv`.
4. Run `python main.py` and follow the prompts.

## Execution runtime

### Python container

Execution runtime is a Debian based docker container with Python 3.10 and ssh server (for remote code execution).
On the first execution, to create image run `docker compose --profile python-ssh  build`.
Then run `docker compose --profile python-ssh up` to start the container. It will be available on port <ssh_port> (ssh -p <ssh_port> <username>@<ssh_hostname>). You may add flag `-d` to run it in the background.

### Jupyter notebook container

Jupyter notebook container is an official Jupyter docker image [jupyter/datascience-notebook](https://hub.docker.com/r/jupyter/datascience-notebook) with python 3.10 kernel installed.
You simply run `docker compose --profile jupyter-notebook up` to start the container. It will be available on port <jupyter_port> (http://<jupyter_hostname>:<jupyter_port>). You may add flag `-d` to run it in the background.

### Apache Zeppelin container
**Note: It does not support ARM architecture (e.g. Apple M1).**
Official Apache Zeppelin docker image [apache/zeppelin](https://hub.docker.com/r/apache/zeppelin) with replaced default python interpreter with python 3.10 (for consistency with other runtimes).
On the first execution, to create image run `docker compose --profile apache-zeppelin build`.
Then run `docker compose --profile apache-zeppelin up` to start the container. It will be available on port <zeppelin_port> (http://<zeppelin_hostname>:<zeppelin_port>). You may add flag `-d` to run it in the background.


