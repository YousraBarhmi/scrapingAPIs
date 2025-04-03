# 1. Base image with Python + dependencies
FROM python:3.11-slim

# 2. Install system dependencies for Chrome & Selenium
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libgdk-pixbuf2.0-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils \
    libu2f-udev \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# 3. Set environment vars for Chrome
ENV CHROME_BIN=/usr/bin/chromium \
    CHROMEDRIVER_PATH=/usr/bin/chromedriver \
    DOCKER=true

# 4. Set working directory
WORKDIR /app

# 5. Copy app files
COPY . .

# 6. Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# 7. Expose port for FastAPI
EXPOSE 8000

# 8. Default command
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
