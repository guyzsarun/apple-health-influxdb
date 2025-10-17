# Use the official Python image
FROM python:3.13-alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

RUN opentelemetry-bootstrap -a install

# Copy application files
COPY ./app .

# Expose the Flask port
EXPOSE 7788

# Define the default command
CMD ["opentelemetry-instrument", "python", "app.py"]
