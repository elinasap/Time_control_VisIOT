# Time_control_VisIOT

# Time Control System

Проект для автоматического контроля времени отрыва от бортика и соблюдения регламентированных правил в соревнованиях по плаванию с использованием MQTT, InfluxDB и Web-server.

## Краткое содержание проекта

- **Визулизация старта, касаний бортика и финиша** (Python + Flask) - веб-интерфейс и API
- **Сборщик данных** (MQTT подписчик) - запись в InfluxDB
- **Хранилище** (InfluxDB 2.7) - временные ряды

## Быстрый старт

### Предварительные требования
- Docker 20.10+
- Docker Compose 2.0+

### Запуск
```bash
git clone https://github.com/ваш-репозиторий/time_control.git
cd time_control
docker-compose up --build
