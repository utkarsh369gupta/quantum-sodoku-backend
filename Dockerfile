# Use a lightweight Python image
FROM python:3.11-slim

# Prevent Python from writing .pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Install system dependencies (optional but helps avoid build failures)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency list first (for caching)
COPY requirements.txt .

# Force use of prebuilt wheels (avoids maturin / Rust issues)
RUN pip install --no-cache-dir --only-binary=:all: -r requirements.txt || \
    pip install --no-cache-dir -r requirements.txt

# Copy your FastAPI app
COPY . .

# Expose the port that Render expects
EXPOSE 10000

# Default command to start the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
