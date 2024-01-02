FROM python:3.10-slim

WORKDIR /app

# Update pip and install requirements
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the application
COPY src/ /app

# Expose streamlit port
EXPOSE 8501

# Add healthcheck
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run the application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]