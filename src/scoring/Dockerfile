# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

#dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY app/ ./app

#ports
EXPOSE 8000

#run
CMD ["fastapi","run", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]