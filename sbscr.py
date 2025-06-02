import paho.mqtt.client as mqtt
from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# --- Настройки MQTT ---
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC2 = "sensor/w_button"  # Топик для первой кнопки, можно заменить на свой
MQTT_TOPIC1 = "sensor/qwedd"      # Топик для второй кнопки, можно заменить на свой
MQTT_TOPIC3 = "sensor/start_butt"

# --- Настройки InfluxDB для первой кнопки ---
INFLUXDB_URL1 = "http://influxdb:8086"
INFLUXDB_TOKEN1 = "" # Заменить на свой
INFLUXDB_ORG1 = "myorg"
INFLUXDB_BUCKET1 = "try5"  # Бакет для первой кнопки

# --- Настройки InfluxDB для второй кнопки ---
INFLUXDB_URL2 = "http://influxdb:8086"
INFLUXDB_TOKEN2 = "" # Заменить на свой
INFLUXDB_ORG2 = "myorg"
INFLUXDB_BUCKET2 = "try6"  # Бакет для второй кнопки

INFLUXDB_BUCKET3 = "try7"  # Бакет для второй кнопки

# Инициализация клиентов InfluxDB
influx_client1 = InfluxDBClient(url=INFLUXDB_URL1, token=INFLUXDB_TOKEN1, org=INFLUXDB_ORG1)
write_api1 = influx_client1.write_api(write_options=SYNCHRONOUS)

influx_client2 = InfluxDBClient(url=INFLUXDB_URL2, token=INFLUXDB_TOKEN2, org=INFLUXDB_ORG2)
write_api2 = influx_client2.write_api(write_options=SYNCHRONOUS)

influx_client3 = InfluxDBClient(url=INFLUXDB_URL2, token=INFLUXDB_TOKEN2, org=INFLUXDB_ORG2)
write_api3 = influx_client2.write_api(write_options=SYNCHRONOUS)



# Получаем объект для работы с API удаления
delete_api = influx_client1.delete_api()

# Указываем временные рамки для удаления
start_time = datetime(1970, 1, 1)  # Начало (самая ранняя дата)
stop_time = datetime.utcnow()      # Конец (текущая дата и время)
predicate = ""

# Выполняем команду удаления
delete_api.delete(
    start=start_time,
    stop=stop_time,
    bucket=INFLUXDB_BUCKET1,
    org=INFLUXDB_ORG1,
    predicate=predicate
)

delete_api.delete(
    start=start_time,
    stop=stop_time,
    bucket=INFLUXDB_BUCKET2,
    org=INFLUXDB_ORG1,
    predicate=predicate
)

delete_api.delete(
    start=start_time,
    stop=stop_time,
    bucket=INFLUXDB_BUCKET3,
    org=INFLUXDB_ORG1,
    predicate=predicate
)

# Колбэк при получении MQTT-сообщения
def on_message(client, userdata, msg):
    time_str = msg.payload.decode()
    print(f"Получено: {time_str}")

    try:
        ts = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S.%f")

        # Определяем, откуда пришло сообщение и записываем в соответствующий бакет.
        if msg.topic == MQTT_TOPIC1:
            # Обработка кнопки 1
            point1 = (
                Point("button_press")
                .field("pressed", 1)
                .time(datetime.utcnow(), WritePrecision.NS)
            )
            write_api1.write(bucket=INFLUXDB_BUCKET1, org=INFLUXDB_ORG1, record=point1)
            print("Записано в InfluxDB (кнопка 1)")

        elif msg.topic == MQTT_TOPIC2:
            # Обработка кнопки 2
            point2 = (
                Point("button_press")
                .field("pressed", 1)
                .time(datetime.utcnow(), WritePrecision.NS)
            )
            write_api2.write(bucket=INFLUXDB_BUCKET2, org=INFLUXDB_ORG2, record=point2)
            print("Записано в InfluxDB (кнопка 2)")

        elif msg.topic == MQTT_TOPIC3:
            # Обработка кнопки 2
            point3 = (
                Point("button_press")
                .field("pressed", 1)
                .time(datetime.utcnow(), WritePrecision.NS)
            )
            write_api3.write(bucket=INFLUXDB_BUCKET3, org=INFLUXDB_ORG2, record=point3)
            print("Записано в InfluxDB (кнопка 3)")

    except ValueError as e:
        print(f"Ошибка парсинга времени: {e}")

# Колбэк при подключении
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Подключено к MQTT брокеру")
        client.subscribe([(MQTT_TOPIC1, 0), (MQTT_TOPIC2, 0), (MQTT_TOPIC3, 0)])  # Подписываемся на оба топика
    else:
        print("Ошибка подключения:", rc)

# Настройка MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Запуск основного цикла MQTT
client.loop_forever()
