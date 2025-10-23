# Use an official Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy the script into the container
COPY switcher-rest-api.py .

# Install dependencies
RUN pip install --no-cache-dir bottle aioswitcher

# Expose port 8080
EXPOSE 8080

# Run the service
CMD ["python", "switcher-rest-api.py"]
