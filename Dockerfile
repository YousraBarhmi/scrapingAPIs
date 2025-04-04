FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    wget unzip gnupg libasound2 libnss3 libxss1 libappindicator3-1 \
    libatk-bridge2.0-0 libatk1.0-0 libcups2 libdrm2 libgbm1 libnspr4 \
    libxcomposite1 libxdamage1 libxrandr2 fonts-liberation xdg-utils \
    --no-install-recommends && rm -rf /var/lib/apt/lists/*

# Install Chrome 135 (the version you provided)
RUN wget -q https://storage.googleapis.com/chrome-for-testing-public/135.0.7049.42/linux64/chrome-linux64.zip -O /tmp/chrome.zip && \
    unzip /tmp/chrome.zip -d /opt && \
    mv /opt/chrome-linux64 /opt/chrome && \
    ln -s /opt/chrome/chrome /usr/bin/google-chrome && \
    rm /tmp/chrome.zip

# Install the corresponding version of ChromeDriver
RUN wget -q https://storage.googleapis.com/chrome-for-testing-public/135.0.7049.42/linux64/chromedriver-linux64.zip -O /tmp/chromedriver.zip && \
    unzip /tmp/chromedriver.zip -d /opt && \
    mv /opt/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver && \
    rm -rf /tmp/chromedriver.zip

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project code
COPY . .

# Set environment variables
ENV CHROME_BIN=/usr/bin/google-chrome
ENV CHROME_DRIVER=/usr/local/bin/chromedriver

# Run the service
EXPOSE 8000
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
