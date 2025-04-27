# Dockerfile (at repo root)
FROM python:3.12-slim

# 1) Install Chromium dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      chromium \
      dbus \
      ca-certificates \
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

# 2) Set our working folder so that `report/` is the project root
WORKDIR /app/report

# 3) Install Python deps from report/requirements.txt
COPY report/requirements.txt .  
RUN pip install --no-cache-dir -r requirements.txt

# 4) Copy *all* of report/
COPY report/ .

# 5) Tell Pyppeteer where to find Chromium
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium

# 6) Start your FastAPI app
CMD ["uvicorn", "report_ai.server:app", "--host", "0.0.0.0", "--port", "8000"]
