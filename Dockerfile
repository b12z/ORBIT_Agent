FROM python:3.11-slim

# Basic OS deps
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    curl ca-certificates git \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install Python deps first (better layer caching)
COPY requirements.txt ./ 
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright Chromium and its OS deps (needed for scraper)
RUN pip install --no-cache-dir playwright && \
    python -m playwright install --with-deps chromium

# Bring in the rest of the app
COPY . .

# Default: run the app (Telegram loop / autopilot if present)
CMD ["python", "-m", "src.main"]
