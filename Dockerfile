# ECR Public mirror of the Docker official image (3.13.18-slim), pinned by digest.
FROM public.ecr.aws/docker/library/python:3.13.18-slim@sha256:e48f59cdba69a3cbd9ed2cf0f348d90d45a8d350d98134cf1070bc106ee9ed90

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY db/ db/
COPY simulate_operations.py run.py ./

RUN useradd --system --uid 10001 --no-create-home app
USER 10001

CMD ["python", "run.py"]
