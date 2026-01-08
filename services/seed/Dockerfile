FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir httpx

COPY services/seed/seed.py /app/
COPY examples/ /app/examples/

CMD ["python", "seed.py"]
