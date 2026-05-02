FROM python:3.12-slim-trixie
COPY --from=ghcr.io/astral-sh/uv:0.10.4 /uv /uvx /bin/
WORKDIR /app
COPY ./uv.lock .
COPY ./pyproject.toml .
COPY ./services/historical-data-service/setup/ ./services/historical-data-service/setup/
RUN uv sync --package setup
CMD ["uv", "run", "services/historical-data-service/setup/setup.py"]