# Use the official Python base image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create and set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        gettext \
        libpq-dev \
        default-libmysqlclient-dev \
        libffi-dev \
        libjpeg-dev \
        libopenjp2-7 \
        libxrender1 \
        libxtst6 \
        zlib1g-dev \
        libcairo2 \
        libpango-1.0-0 \
        libpangocairo-1.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*



# Copy Nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf


# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the application code into the container
COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput

# Apply database migrations
RUN python manage.py migrate

# Start Gunicorn server
CMD ["./entrypoint.sh"]
