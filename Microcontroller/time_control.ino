#include <WiFi.h>
#include "time.h"
#include <PubSubClient.h>

// WiFi настройки
const char* ssid     = ""; // заменить на свой
const char* password = ""; // заменить на свой

// Время (NTP)
const char* ntpServer = "pool.ntp.org";
const long  gmtOffset_sec = 3 * 3600;  // Москва = GMT+3
const int   daylightOffset_sec = 0;

// Пины кнопок
const int button1Pin = 21;  // Кнопка 1 пловца (Q) 
const int button2Pin = 19;  // Кнопка 2 пловца (W)
const int button3Pin = 18;  // Кнопка Start (S)


bool button1State = HIGH;
bool lastButton1State = HIGH;

bool button2State = HIGH;
bool lastButton2State = HIGH;

bool button3State = HIGH;
bool lastButton3State = HIGH;

// Синхронизация времени
unsigned long syncedMillis = 0;
time_t syncedEpoch = 0;

// MQTT настройки
const char *mqtt_broker = "broker.emqx.io";
const char *topic_q = "sensor/qwedd";
const char *topic_w = "sensor/w_button";
const char *topic_s = "sensor/start_butt";
const char *topic_subscribe = "sensor/response";
const char *mqtt_username = "";
const char *mqtt_password = "";
const int mqtt_port = 1883;

WiFiClient espClient;
PubSubClient client(espClient);

void setup() {
  Serial.begin(115200);
  pinMode(button1Pin, INPUT_PULLUP);
  pinMode(button2Pin, INPUT_PULLUP);
  pinMode(button3Pin, INPUT_PULLUP);

  WiFi.setSleep(false);  // стабильность

  WiFi.begin(ssid, password);
  Serial.print("Подключение к Wi-Fi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWi-Fi подключён");

  // Настройка времени
  configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
  struct tm timeinfo;
  if (getLocalTime(&timeinfo)) {
    time(&syncedEpoch);
    syncedMillis = millis();
    Serial.println("Время синхронизировано");
  } else {
    Serial.println("Ошибка синхронизации времени");
  }

  // MQTT
  client.setServer(mqtt_broker, mqtt_port);
  client.setCallback(callback);
  client.setKeepAlive(60);
  reconnect();
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // Кнопка 1 (Q)
  button1State = digitalRead(button1Pin);
  if (button1State == LOW && lastButton1State == HIGH) {
    logButtonPress(topic_q, "Q");
    delay(1000);
  }
  lastButton1State = button1State;

  // Кнопка 2 (W)
  button2State = digitalRead(button2Pin);
  if (button2State == LOW && lastButton2State == HIGH) {
    logButtonPress(topic_w, "W");
    delay(1000);
  }
  lastButton2State = button2State;

    // Кнопка 3 (S)
  button3State = digitalRead(button3Pin);
  if (button3State == LOW && lastButton3State == HIGH) {
    logButtonPress(topic_s, "S");
    delay(1000);
  }
  lastButton3State = button3State;
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Подключение к MQTT... ");
    String client_id = "esp32-client-" + String(WiFi.macAddress());

    if (client.connect(client_id.c_str(), mqtt_username, mqtt_password)) {
      Serial.println("Успешно");
      client.subscribe(topic_subscribe);
      client.publish(topic_q, "ESP32 запущен и подключен");
    } else {
      Serial.print("Ошибка подключения. Код: ");
      Serial.println(client.state());
      delay(2000);
    }
  }
}

void callback(char *topicName, byte *payload, unsigned int length) {
  Serial.print("Сообщение в теме: ");
  Serial.println(topicName);
  Serial.print("Сообщение: ");
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println("\n-----------------------");
}

void logButtonPress(const char* topic, const char* label) {
  unsigned long currentMillis = millis();
  time_t currentEpoch = syncedEpoch + (currentMillis - syncedMillis) / 1000;
  int ms = (currentMillis - syncedMillis) % 1000;

  struct tm timeinfo;
  localtime_r(&currentEpoch, &timeinfo);

  char timeStr[64];
  strftime(timeStr, sizeof(timeStr), "%Y-%m-%d %H:%M:%S", &timeinfo);

  char fullTimeStr[128];
  snprintf(fullTimeStr, sizeof(fullTimeStr), "%s.%03d", timeStr, ms);

  Serial.printf("Нажата кнопка %s: %s\n", label, fullTimeStr);

  if (client.publish(topic, fullTimeStr)) {
    Serial.printf("MQTT (%s): сообщение отправлено\n", topic);
  } else {
    Serial.printf("MQTT (%s): ошибка отправки\n", topic);
  }
}
