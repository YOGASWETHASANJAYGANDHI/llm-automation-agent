# Use a minimal Python image
FROM python:3.12-slim-bookworm

# Set environment variable for runtime access (no need for ARG)
ENV AIPROXY_TOKEN=""

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates

# Install FastAPI and Uvicorn
RUN pip install --no-cache-dir fastapi uvicorn

# Set up the application directory
WORKDIR /app

# Copy application files
COPY app.py /app
COPY tasksA.py /app/tasksA.py
COPY tasksB.py /app/tasksB.py
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY .env /app/.env



# Expose the port for FastAPI
EXPOSE 8000

# Run FastAPI with Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

