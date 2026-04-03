FROM python:3.12-slim AS base

RUN pip install uv

WORKDIR /app

COPY pyproject.toml uv.lock* ./
RUN uv sync --no-dev --no-editable

COPY . .

# Генерация protobuf
RUN uv run python -m grpc_tools.protoc -I. --python_out=. --pyi_out=. shared/proto/event.proto 2>/dev/null || true

# Установка Playwright и Chromium
RUN PLAYWRIGHT_BROWSERS_PATH=/app/browsers uv run playwright install chromium --with-deps

ENV PLAYWRIGHT_BROWSERS_PATH=/app/browsers
ENV APP_ENV=production

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "http_api.run:server", "--host", "0.0.0.0", "--port", "8000"]
