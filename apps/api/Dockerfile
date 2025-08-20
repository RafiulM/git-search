# Use Python 3.12 as base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for Playwright and git
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    curl \
    git \
    libmagic1 \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon-x11-0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpangocairo-1.0-0 \
    libpango-1.0-0 \
    libcairo2 \
    libgtk-3-0 \
    libatspi2.0-0 \
    xvfb \
    fonts-noto-color-emoji \
    fonts-font-awesome \
    fonts-noto-mono \
    fonts-noto-core \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium

# Copy application code
COPY . .

# Set environment variables for emoji support
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV API_PORT=8000

# Expose port
EXPOSE $API_PORT

# Run the application
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $API_PORT"]