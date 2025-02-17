# Use the official Python slim image as base
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Add non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set proper permissions
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Set environment variables         
ENV FLASK_APP=application.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 5000
EXPOSE 443

# Run the application
#CMD ["flask", "run"]
CMD ["flask", "run", "--cert=app/ssl/certificate.crt", "--key=app/ssl/private.key", "--port=443"]
