FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    gcc \
    make \
    nano \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy the contents
COPY . /app

#RUN pip install --no-cache-dir -r requirements.txt

# Expose port for FastAPI app
EXPOSE 8000

# Run the FastAPI app with uvicorn
CMD ["uvicorn", "challenge.api:app", "--host", "0.0.0.0", "--port", "8000"]