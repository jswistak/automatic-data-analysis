FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y \
    curl \
    poppler-utils \
    texlive-xetex \
    pandoc

# Update pip and install requirements
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the application
COPY src/ /app

# Prepare direcotries for files
RUN mkdir /app/reports && mkdir /app/conversations

# Expose streamlit port
EXPOSE 8501

# Add healthcheck
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run the application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]