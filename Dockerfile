FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN \
    apt-get update && apt-get install -y --no-install-recommends \
    wget \
    unzip \
    ca-certificates \
    libglib2.0-0 \
    libnss3 \
    libfontconfig1 \
    libx11-6 \
    libx11-xcb1 \
    libxcb-dri3-0 \
    libxcb-shm0 \
    libdrm2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libgtk-3-0 \
    libasound2 \
    libxshmfence1 \
    libgbm1 \
    --fix-missing

RUN wget -q -O /tmp/chrome.zip "https://storage.googleapis.com/chrome-for-testing-public/113.0.5672.0/linux64/chrome-linux64.zip" && \
    unzip /tmp/chrome.zip -d /opt/ && \
    ln -s /opt/chrome-linux64/chrome /usr/local/bin/google-chrome

RUN wget -q -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/113.0.5672.24/chromedriver_linux64.zip" && \
    unzip /tmp/chromedriver.zip -d /tmp/ && \
    mv /tmp/chromedriver /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver

RUN google-chrome --version && \
    chromedriver --version
    
RUN rm -rf /tmp/*.zip /tmp/chromedriver-linux64 && \
    apt-get purge -y --auto-remove wget unzip && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ARG FLAG="flag{THIS_IS_A_FAKE_FLAG}"
ENV FLAG=${FLAG}

ENV WORTHIT_USERNAME=Luminoria
ENV WORTHIT_PASSWORD=\$argon2id\$v=19\$m=65540,t=3,p=4\$MW4yUzNkdGo5STlGdkFDZ3pMQnhCQUk3emNUZkQ1eENkNHNzVlA3MTZwST0\$6a7lmy2uI3fQ+Kz+Fkz1OseI7cdQCqVPcCu17OBjiDk

EXPOSE 5000

CMD ["python", "app.py"]
