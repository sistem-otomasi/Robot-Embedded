#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// WiFi Configuration
const char* WIFI_SSID = "YOUR_SSID";
const char* WIFI_PASSWORD = "YOUR_PASSWORD";

// MQTT Broker Configuration
const char* MQTT_BROKER = "192.168.1.100";  // IP MiniPC
const int MQTT_PORT = 1883;
const char* MQTT_CLIENT_ID = "esp32_embedded_01";

// MQTT Topics
const char* TOPIC_HEARTBEAT = "robot/embedded/heartbeat";
const char* TOPIC_SENSOR_DATA = "robot/embedded/sensors";
const char* TOPIC_STATUS = "robot/embedded/status";
const char* TOPIC_CONTROL = "robot/control/command";

// Pins
const int LED_PIN = 2;
const int BUTTON_PIN = 0;

// Global objects
WiFiClient espClient;
PubSubClient client(espClient);

// Global variables
unsigned long lastHeartbeat = 0;
const unsigned long HEARTBEAT_INTERVAL = 5000;  // 5 seconds

// Function declarations
void setupWiFi();
void reconnectMQTT();
void publishHeartbeat();
void publishSensorData();
void messageCallback(char* topic, byte* payload, unsigned int length);
void handleControl(const JsonDocument& doc);

void setup() {
    Serial.begin(115200);
    delay(1000);
    
    Serial.println("\n\n=== ESP32 Embedded System Startup ===");
    
    // Initialize pins
    pinMode(LED_PIN, OUTPUT);
    pinMode(BUTTON_PIN, INPUT);
    
    digitalWrite(LED_PIN, LOW);
    
    // Setup WiFi
    setupWiFi();
    
    // Setup MQTT
    client.setServer(MQTT_BROKER, MQTT_PORT);
    client.setCallback(messageCallback);
    
    Serial.println("Setup completed successfully");
}

void loop() {
    // Ensure WiFi is connected
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("WiFi disconnected, reconnecting...");
        setupWiFi();
    }
    
    // Reconnect MQTT if needed
    if (!client.connected()) {
        reconnectMQTT();
    }
    
    client.loop();
    
    // Check button state for manual control
    if (digitalRead(BUTTON_PIN) == LOW) {
        digitalWrite(LED_PIN, HIGH);
        delay(1000);
        digitalWrite(LED_PIN, LOW);
    }
    
    // Publish heartbeat periodically
    if (millis() - lastHeartbeat >= HEARTBEAT_INTERVAL) {
        publishHeartbeat();
        publishSensorData();
        lastHeartbeat = millis();
    }
    
    delay(100);
}

void setupWiFi() {
    Serial.print("Connecting to WiFi: ");
    Serial.println(WIFI_SSID);
    
    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 20) {
        delay(500);
        Serial.print(".");
        attempts++;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\nWiFi connected!");
        Serial.print("IP address: ");
        Serial.println(WiFi.localIP());
        digitalWrite(LED_PIN, HIGH);
    } else {
        Serial.println("\nFailed to connect to WiFi");
    }
}

void reconnectMQTT() {
    int attempts = 0;
    while (!client.connected() && attempts < 5) {
        Serial.print("Attempting MQTT connection...");
        
        if (client.connect(MQTT_CLIENT_ID)) {
            Serial.println("connected");
            
            // Subscribe to control topic
            client.subscribe(TOPIC_CONTROL);
            
            // Publish initial status
            client.publish(TOPIC_STATUS, "{\\"state\\": \\"online\\", \\"device\\": \\"ESP32\\"}");
            
        } else {
            Serial.print("failed, rc=");
            Serial.print(client.state());
            Serial.println(" try again in 5 seconds");
            delay(5000);
        }
        attempts++;
    }
}

void publishHeartbeat() {
    StaticJsonDocument<200> doc;
    doc["device_id"] = MQTT_CLIENT_ID;
    doc["timestamp"] = millis();
    doc["uptime_ms"] = millis();
    doc["rssi"] = WiFi.RSSI();
    doc["ip"] = WiFi.localIP().toString();
    
    char buffer[256];
    serializeJson(doc, buffer);
    
    client.publish(TOPIC_HEARTBEAT, buffer);
    Serial.print("Heartbeat published: ");
    Serial.println(buffer);
}

void publishSensorData() {
    // Read analog sensor (ADC)
    int adc_value = analogRead(A0);
    float voltage = (adc_value / 4095.0) * 3.3;
    
    StaticJsonDocument<300> doc;
    doc["device_id"] = MQTT_CLIENT_ID;
    doc["timestamp"] = millis();
    doc["adc_raw"] = adc_value;
    doc["voltage"] = voltage;
    doc["temperature"] = 25.5;  // Dummy temperature reading
    doc["humidity"] = 60.0;     // Dummy humidity reading
    doc["led_state"] = digitalRead(LED_PIN);
    
    char buffer[512];
    serializeJson(doc, buffer);
    
    client.publish(TOPIC_SENSOR_DATA, buffer);
    Serial.print("Sensor data published: ");
    Serial.println(buffer);
}

void messageCallback(char* topic, byte* payload, unsigned int length) {
    Serial.print("Message received on topic: ");
    Serial.println(topic);
    
    // Convert payload to string
    char message[length + 1];
    memcpy(message, payload, length);
    message[length] = '\0';
    
    Serial.print("Payload: ");
    Serial.println(message);
    
    // Parse JSON
    StaticJsonDocument<256> doc;
    DeserializationError error = deserializeJson(doc, message);
    
    if (error) {
        Serial.print("JSON parse error: ");
        Serial.println(error.c_str());
        return;
    }
    
    handleControl(doc);
}

void handleControl(const JsonDocument& doc) {
    if (doc.containsKey("led")) {
        bool ledState = doc["led"];
        digitalWrite(LED_PIN, ledState ? HIGH : LOW);
        
        StaticJsonDocument<200> response;
        response["action"] = "led_set";
        response["state"] = ledState;
        response["timestamp"] = millis();
        
        char buffer[256];
        serializeJson(response, buffer);
        client.publish(TOPIC_STATUS, buffer);
        
        Serial.print("LED set to: ");
        Serial.println(ledState ? "ON" : "OFF");
    }
    
    if (doc.containsKey("delay")) {
        delay(doc["delay"]);
    }
}
