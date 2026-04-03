.PHONY: help setup start install dev test lint format build run logs shell health pg/up pg/down generate/proto deploy push pull

# Переменные
IMAGE_NAME ?= domesticator
VERSION ?= latest
PORT ?= 8000
REGISTRY ?= docker.io
NAMESPACE ?= domesticator
CONTAINER_NAME ?= domesticator

setup: ## Установка всех зависимостей (Python, Node, uv, Chromium)
	@bash setup.sh

start: setup ## Полная установка + запуск сервера
	@echo "==> Starting server on http://localhost:$(PORT) ..."
	APP_ENV=development uv run uvicorn http_api.run:server --reload --host 0.0.0.0 --port $(PORT)

help: ## Все доступные команды
	@grep -E '^[a-zA-Z_/]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Установка зависимостей
	uv sync --all-extras

dev: ## Локальный запуск с hot reload
	@test -f .env.local || cp .env.local.example .env.local
	APP_ENV=development uv run uvicorn http_api.run:server --reload --host 0.0.0.0 --port $(PORT)

test: ## Запуск тестов
	uv run pytest -v

lint: ## Проверка кода
	uv run ruff check .

format: ## Форматирование кода
	uv run ruff format .
	uv run ruff check --fix .

build: ## Сборка Docker образа
	docker build -t $(IMAGE_NAME):$(VERSION) .

run: ## Запуск в контейнере
	docker run -d --name $(CONTAINER_NAME) -p $(PORT):8000 --env-file .env.local $(IMAGE_NAME):$(VERSION)

logs: ## Просмотр логов
	docker logs -f $(CONTAINER_NAME)

shell: ## Подключение к контейнеру
	docker exec -it $(CONTAINER_NAME) /bin/bash

health: ## Проверка здоровья
	curl -s http://localhost:$(PORT)/health | python3 -m json.tool

pg/up: ## Запуск PostgreSQL
	docker run -d --name domesticator-pg -p 5432:5432 -e POSTGRES_DB=domesticator -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password postgres:16-alpine

pg/down: ## Остановка PostgreSQL
	docker stop domesticator-pg && docker rm domesticator-pg

generate/proto: ## Генерация protobuf файлов
	uv run python -m grpc_tools.protoc -I. --python_out=. --pyi_out=. shared/proto/event.proto

deploy: build push ## Полное развертывание

push: ## Загрузка в реестр
	docker tag $(IMAGE_NAME):$(VERSION) $(REGISTRY)/$(NAMESPACE)/$(IMAGE_NAME):$(VERSION)
	docker push $(REGISTRY)/$(NAMESPACE)/$(IMAGE_NAME):$(VERSION)

pull: ## Скачивание из реестра
	docker pull $(REGISTRY)/$(NAMESPACE)/$(IMAGE_NAME):$(VERSION)
