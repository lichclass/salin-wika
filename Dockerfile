# AI Amended: Package the same two-command CLI in a small Python image with persistent results support.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install --yes --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
ARG TARGETARCH
RUN python -m pip install --no-cache-dir --upgrade pip \
    && if [ "$TARGETARCH" = "arm64" ]; then \
        python -m pip install --no-cache-dir torch==2.11.0 \
            --index-url https://download.pytorch.org/whl/cpu; \
    fi \
    && python -m pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p results

ENTRYPOINT ["python", "main.py"]
CMD ["--help"]
