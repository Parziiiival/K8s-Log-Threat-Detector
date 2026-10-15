FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files into container
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Run API server accessible outside the container
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]