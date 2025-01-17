# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment variables
ENV PORT=8000
ENV HOST=0.0.0.0

# Expose port
EXPOSE 8000

# Start the application
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8000", "--workers", "4", "--threads", "4", "--timeout", "120"]