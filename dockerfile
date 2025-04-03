FROM python:3.11-slim

# Install Chrome & dependencies
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    python3-distutils \
    wget curl unzip gnupg \
    libglib2.0-0 \
    libnss3 \
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
    libgconf-2-4 \
    libfontconfig1 \
    fonts-liberation \
    xdg-utils \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV CHROME_BIN="/usr/bin/chromium"
ENV DOCKER=true

WORKDIR /app
COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]