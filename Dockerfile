FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends libpq5 && rm -rf /var/lib/apt/lists/*

# Install uv runner to manage project dependencies
RUN pip install --no-cache-dir uv

COPY pyproject.toml README.md LICENSE ./
COPY src ./src

RUN uv pip install --system .

EXPOSE 8000

CMD ["uvicorn", "svc_catalogue.main:app", "--host", "0.0.0.0", "--port", "8000"]
