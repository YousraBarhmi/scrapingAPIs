# Base image with Python 3.11.4
FROM python:3.11.4-slim

# Set environment variables to make installs non-interactive
ENV DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /app

# Install required system dependencies for Chromium and headless execution
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    curl \
    unzip \
    gnupg \
    gconf-service \
    libasound2 \
    libatk1.0-0 \
    libcairo2 \
    libcups2 \
    libfontconfig1 \
    libgdk-pixbuf2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libxss1 \
    libxshmfence1 \
    libgbm1 \
    lsb-release \
    xdg-utils \
    fonts-liberation \
    chromium \
    chromium-driver \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Set environment variables for Selenium
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver
ENV DOCKER=true

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy app source code
COPY . .

# Expose FastAPI port (default 8080)
EXPOSE 8080

# Run the FastAPI app
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]
