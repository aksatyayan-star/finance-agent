# --- Build Stage ---
# Use a full Python image to ensure all build tools are available for dependencies.
FROM python:3.11-slim as builder

WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
# Using --no-cache-dir to keep the layer small
RUN pip install --no-cache-dir -r requirements.txt

# --- Final Stage ---
# Use a slim image for the final container to reduce size.
FROM python:3.11-slim

WORKDIR /app

# Copy installed dependencies from the build stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application source code
COPY . .

# Set environment variables for the container
# PYTHONUNBUFFERED ensures that print statements are sent straight to the terminal.
# PORT is the standard variable used by Cloud Run to specify the port.
ENV PYTHONUNBUFFERED 1
ENV PORT 8080

# Expose the port that Gunicorn will run on
EXPOSE 8080

# The command to run the application using Gunicorn
# --bind 0.0.0.0 makes the server accessible from outside the container.
# --workers is a good practice for production, 3 is a reasonable default.
# server:app points to the 'app' object in the 'server.py' file.
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "3", "server:app"]
