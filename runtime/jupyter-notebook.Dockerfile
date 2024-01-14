FROM jupyter/scipy-notebook:python-3.10

# Use an environment variable to set the Jupyter token for authorization
CMD start-notebook.sh --NotebookApp.token=$TOKEN