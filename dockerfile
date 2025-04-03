# Base image with Python 3.11.4
FROM python:3.11.4-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Install required dependencies
RUN apt-get update && apt-get install -y \
    gconf-service libasound2 libatk1.0-0 libcairo2 libcups2 libfontconfig1 \
    libgdk-pixbuf2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libxss1 fonts-liberation \
    libnss3 lsb-release xdg-utils libgbm1 libxshmfence1 \
    wget unzip curl

# Install Chromium Browser instead of Google Chrome
RUN apt-get install -y chromium chromium-driver

# Set environment variables for Chrome and Chromedriver
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROME_DRIVER=/usr/bin/chromedriver

# Verify installations
RUN echo "Chromium version: $(chromium --version)" && \
    echo "Chromedriver version: $(chromedriver --version)"

# Copy the entire project into the container
COPY . .

# Expose the port that FastAPI will use (default 8080)
EXPOSE 8080

# Clean up any unnecessary packages after installation
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Ensure all packages are updated to their latest versions
RUN apt-get update && apt-get dist-upgrade -y 

# Command to run the FastAPI app with Uvicorn
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]
