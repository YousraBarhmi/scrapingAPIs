# 1. Base image with Python + dependencies
FROM python:3.11-slim

# 2. Install system dependencies for Chrome & Selenium
RUN apt-get update && apt-get install -y \
    wget curl gnupg unzip \
    chromium \
    chromium-driver \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    libxss1 \
    libappindicator3-1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libx11-xcb1 \
    fonts-liberation \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# 3. Set environment vars for Chrome
ENV CHROME_BIN=/usr/bin/chromium \
    CHROMEDRIVER_PATH=/usr/bin/chromedriver \
    DOCKER=true \
    PYTHONUNBUFFERED=1

# 4. Set working directory
WORKDIR /app

# 5. Copy app files
COPY . .

# Install Python dependencies directly (no venv!)
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8000

# Command to run FastAPI server
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
