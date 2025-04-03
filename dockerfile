FROM python:3.10-slim

# 安装依赖
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    curl \
    unzip \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libxss1 \
    libxtst6 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# 设置环境变量
ENV CHROME_BIN="/usr/bin/chromium"
ENV CHROMEDRIVER_PATH="/usr/bin/chromedriver"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 安装 Python 依赖
WORKDIR /app
COPY . /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
