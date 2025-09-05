
FROM python:3.13.7-slim-trixie

ENV PYTHONUNBUFFERED=1 \
	PYTHONDONTWRITEBYTECODE=1 \
	PATH="/root/.local/bin:$PATH" \
	PYTHONPATH=/app

WORKDIR /app

# Install system dependencies required by some Python packages (adjust if you know exact needs)
RUN apt-get update && apt-get install -y --no-install-recommends \
	build-essential \
	gcc \
	libpq-dev \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt


COPY . /app

EXPOSE 80

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
