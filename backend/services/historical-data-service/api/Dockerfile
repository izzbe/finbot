FROM python:3.12-slim-trixie
COPY --from=ghcr.io/astral-sh/uv:0.10.4 /uv /uvx /bin/
WORKDIR /app
COPY ./uv.lock .
COPY ./pyproject.toml .
COPY ./services/historical-data-service/api/ ./services/historical-data-service/api/
COPY ./services/historical-data-service/fetchers/ ./services/historical-data-service/fetchers/
COPY ./packages/common/ ./packages/common/
RUN uv sync --package api
CMD ["uv", "run", "fastapi", "run", "./services/historical-data-service/api/main.py", "--port", "80"]