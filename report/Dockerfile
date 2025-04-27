FROM python:3.12-slim

# 1) Install Chrome + its libs
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      chromium \
      libnss3 \
      libxss1 \
      libasound2 \
      fonts-liberation \
      libatk1.0-0 \
      libgbm1 \
      libgtk-3-0 \
      libxcomposite1 \
      libxdamage1 \
      libxrandr2 \
      libxcursor1 \
      libxfixes3 \
      libxi6 \
      libxtst6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium
CMD ["uvicorn", "report_ai.server:app", "--host", "0.0.0.0", "--port", "8000"]
