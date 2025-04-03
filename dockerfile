# 1. Base image with Python + dependencies
FROM python:3.11-slim

# 2. Install system dependencies for Chrome & Selenium
RUN apt-get update && apt-get install -y \
    wget curl gnupg unzip \
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
    
RUN apt-get update && apt-get install -y python3-distutils


RUN apt-get update && apt-get install -y \
    chromium=114.0.5735.90-1~deb11u1 \
    chromium-driver=114.0.5735.90-1~deb11u1


# 3. Set environment vars for Chrome
ENV CHROME_BIN="/usr/bin/chromium"
ENV CHROMEDRIVER_PATH="/usr/bin/chromedriver"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DOCKER=true

# 4. Définir le dossier de travail
WORKDIR /app
COPY . /app

# 5. Installer les dépendances Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# 6. Exposer le port utilisé par uvicorn
EXPOSE 8000

# 7. Démarrer l'application FastAPI
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
