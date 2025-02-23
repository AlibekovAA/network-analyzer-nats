# Анализ Сетевых Пакетов

## Обзор

Проект представляет собой приложение для анализа сетевых пакетов, реализованное с использованием Python и Go. Основная цель приложения — анализировать файлы формата PCAP/PCAPNG, предоставлять результаты анализа через API и обеспечивать детальную диагностику работы через логи.

## Пример пользовательского интерфейса

![](example_ui/animation.gif)

## Архитектура

Проект состоит из двух основных компонентов:

1. Python приложение:
   - Использует FastAPI для предоставления API интерфейса.
   - Обрабатывает загрузку файлов, включая проверку типа и размера.
   - Расширенная обработка ошибок с глобальными и валидационными обработчиками.
   - Логирование с учетом временной зоны Europe/Moscow.

2. Go приложение:
   - Выполняет анализ сетевых пакетов с использованием библиотеки Gopacket.
   - Обрабатывает задачи анализа, полученные через NATS.
   - Возвращает результаты анализа обратно в Python приложение.
   - Логирование с настройкой временной зоны Europe/Moscow.

## Используемые технологии

- Docker и Docker Compose для контейнеризации и оркестрации.
- FastAPI для создания REST API.
- NATS для обмена сообщениями между компонентами.
- Go и библиотека Gopacket для анализа сетевых пакетов.
- Mypy для статического анализа Python кода.

## Конфигурация и переменные окружения

- NATS_SERVER_URL — URL сервера NATS (по умолчанию: `nats://localhost:4222`).
- NATS_ADDR — адрес для подключения Go приложения к NATS (по умолчанию: `nats://nats:4222`).
- TZ — временная зона (Europe/Moscow).
- MAX_FILE_SIZE — максимальный размер загружаемого PCAP файла (в байтах).

## Запуск проекта

1. Убедитесь, что у вас установлены Docker и Docker Compose.
2. Склонируйте репозиторий проекта.
3. Создайте кэшированные образы для ускорения сборки:
   ```bash
   docker build -t python_app:cache --target production ./python_app
   docker build -t go_app:cache --target production ./go_app
   ```
4. Выполните сборку с использованием кэша:
   ```bash
   docker-compose build
   ```
5. Запустите контейнеры:
   - Для разработки:
     ```bash
     docker-compose up
     ```
   - Только основные сервисы:
     ```bash
     docker-compose up nats python_app go_app
     ```
   - Для продакшена:
     ```bash
     docker-compose -f docker-compose.yml -f docker/compose/production.yml up
     ```

## Структура Docker конфигурации

Конфигурация Docker разделена на несколько файлов в директории `docker/compose/`:
- `base.yml` - базовая конфигурация NATS сервера
- `python.yml` - конфигурация Python приложения
- `golang.yml` - конфигурация Go приложения
- `production.yml` - дополнительные настройки для продакшена

Основной файл `docker-compose.yml` в корневой директории объединяет все конфигурации.

## Доступные endpoints

- Основной API: [http://localhost:8000](http://localhost:8000)
- Документация API (Swagger UI): [http://localhost:8000/docs](http://localhost:8000/docs)
- Health check: [http://localhost:8000/health](http://localhost:8000/health)

## Оптимизация сборки

Для ускорения сборки используются кэшированные слои Docker. Сначала создаются образы с кэшем, затем применяется команда `docker-compose build` для сборки остальных сервисов.

## Логи

- Логи Go приложения сохраняются в каталоге `logs` и содержат подробные данные с учетом временной зоны Europe/Moscow.

## Очистка Docker окружения

- Остановка всех контейнеров: `docker stop $(docker ps -a -q)`
- Удаление всех контейнеров: `docker rm $(docker ps -a -q)`
- Удаление всех образов: `docker rmi $(docker images -q)`
- Полная очистка системы: `docker system prune -a --volumes -f`
