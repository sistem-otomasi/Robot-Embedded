/*
 * STM32 Embedded System - ROS Communication
 * Support: STM32F1, STM32F4
 * 
 * Communicates with MiniPC ROS via MQTT over Ethernet/WiFi
 */

#include <Arduino.h>
#include <WiFi.h>
#include <Ethernet.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <stm32_def.h>

// ============ Configuration ============

// For Ethernet (STM32F4)
byte mac[] = {0x00, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE};
IPAddress ip(192, 168, 1, 101);
IPAddress gateway(192, 168, 1, 1);
IPAddress subnet(255, 255, 255, 0);
IPAddress dns(8, 8, 8, 8);

// For WiFi (with WiFi shield)
// const char* WIFI_SSID = "YOUR_SSID";
// const char* WIFI_PASSWORD = "YOUR_PASSWORD";

// MQTT Configuration
const char* MQTT_BROKER = "192.168.1.100";
const int MQTT_PORT = 1883;
const char* MQTT_CLIENT_ID = "stm32_embedded_01";

// MQTT Topics
const char* TOPIC_HEARTBEAT = "robot/embedded/heartbeat";
const char* TOPIC_SENSOR_DATA = "robot/embedded/sensors";
const char* TOPIC_STATUS = "robot/embedded/status";
const char* TOPIC_CONTROL = "robot/control/command";

// Pin Configuration
#ifdef STM32F407xx
    #define LED_PIN PA1
    #define BUTTON_PIN PA0
    #define ADC_PIN PA4
#elif defined(STM32F103xx)
    #define LED_PIN PB12
    #define BUTTON_PIN PB13
    #define ADC_PIN PA0
#endif

// ============ Global Objects ============

EthernetClient ethClient;
PubSubClient client(ethClient);

// State variables
unsigned long lastHeartbeat = 0;
unsigned long lastSensorRead = 0;
const unsigned long HEARTBEAT_INTERVAL = 5000;
const unsigned long SENSOR_READ_INTERVAL = 2000;

volatile bool buttonPressed = false;

// Function declarations
void setupEthernet();
void setupADC();
void reconnectMQTT();
void publishHeartbeat();
void publishSensorData();
void messageCallback(char* topic, byte* payload, unsigned int length);
void handleControl(const JsonDocument& doc);
void buttonISR();
uint16_t readADC();

// ============ Setup ============

void setup() {
    Serial.begin(115200);
    delay(2000);  // Wait for serial monitor
    
    Serial.println("\n=== STM32 Embedded System Startup ===");
    Serial.println("Platform: STM32F4/F1");
    Serial.println("Protocol: MQTT over Ethernet");
    
    // Initialize pins
    pinMode(LED_PIN, OUTPUT);
    pinMode(BUTTON_PIN, INPUT_PULLUP);
    pinMode(ADC_PIN, ANALOG);
    
    digitalWrite(LED_PIN, LOW);
    
    // Setup ADC
    setupADC();
    
    // Setup Ethernet
    setupEthernet();
    
    // Setup MQTT
    client.setServer(MQTT_BROKER, MQTT_PORT);
    client.setCallback(messageCallback);
    
    // Attach button interrupt
    attachInterrupt(digitalPinToInterrupt(BUTTON_PIN), buttonISR, FALLING);
    
    Serial.println("Setup completed successfully");
    delay(1000);
}

// ============ Main Loop ============

void loop() {
    // Maintain Ethernet connection
    Ethernet.maintain();
    
    // Reconnect MQTT if needed
    if (!client.connected()) {
        reconnectMQTT();
    }
    
    client.loop();
    
    // Handle button press
    if (buttonPressed) {
        Serial.println("Button pressed!");
        digitalWrite(LED_PIN, HIGH);
        delay(500);
        digitalWrite(LED_PIN, LOW);
        buttonPressed = false;
    }
    
    // Publish heartbeat periodically
    if (millis() - lastHeartbeat >= HEARTBEAT_INTERVAL) {
        publishHeartbeat();
        lastHeartbeat = millis();
    }
    
    // Publish sensor data periodically
    if (millis() - lastSensorRead >= SENSOR_READ_INTERVAL) {
        publishSensorData();
        lastSensorRead = millis();
    }
    
    delay(50);
}

// ============ Ethernet Setup ============

void setupEthernet() {
    Serial.println("Initializing Ethernet...");
    
    // Start Ethernet with DHCP
    if (Ethernet.begin(mac) == 0) {
        Serial.println("Failed to configure Ethernet using DHCP");
        
        // Configure manually
        Ethernet.begin(mac, ip, dns, gateway, subnet);
        Serial.println("Configured with static IP");
    }
    
    // Wait for link and IP assignment
    int attempts = 0;
    while (Ethernet.linkStatus() == LinkOFF && attempts < 10) {
        Serial.print(".");
        delay(500);
        attempts++;
    }
    
    if (Ethernet.linkStatus() == LinkON) {
        Serial.println("\nEthernet connected!");
        Serial.print("IP address: ");
        Serial.println(Ethernet.localIP());
        digitalWrite(LED_PIN, HIGH);
    } else {
        Serial.println("\nEthernet connection failed!");
    }
}

// ============ ADC Setup ============

void setupADC() {
    #ifdef STM32F407xx
        // Configure ADC for STM32F4
        adc_init(ADC1);
        adc_set_prescaler(ADC_PRESCALER_PCLK2_8);
    #elif defined(STM32F103xx)
        // Configure ADC for STM32F1
        adc_init(ADC1);
    #endif
}

uint16_t readADC() {
    return analogRead(ADC_PIN);
}

// ============ MQTT Functions ============

void reconnectMQTT() {
    int attempts = 0;
    while (!client.connected() && attempts < 5) {
        Serial.print("Attempting MQTT connection...");
        
        if (client.connect(MQTT_CLIENT_ID)) {
            Serial.println("connected");
            
            // Subscribe to control topic
            client.subscribe(TOPIC_CONTROL);
            
            // Publish initial status
            client.publish(TOPIC_STATUS, "{\\"state\\": \\"online\\", \\"device\\": \\"STM32\\"}");
            
        } else {
            Serial.print("failed, rc=");
            Serial.print(client.state());
            Serial.println(" retry in 5 seconds");
            delay(5000);
        }
        attempts++;
    }
}

void publishHeartbeat() {
    StaticJsonDocument<250> doc;
    doc["device_id"] = MQTT_CLIENT_ID;
    doc["device_type"] = "STM32F4";
    doc["timestamp"] = millis();
    doc["uptime_ms"] = millis();
    doc["ip"] = Ethernet.localIP().toString();
    doc["link_status"] = (Ethernet.linkStatus() == LinkON) ? "up" : "down";
    
    char buffer[512];
    size_t n = serializeJson(doc, buffer);
    
    client.publish(TOPIC_HEARTBEAT, buffer, n);
    Serial.print("Heartbeat: ");
    Serial.println(buffer);
}

void publishSensorData() {
    uint16_t adc_raw = readADC();
    float voltage = (adc_raw / 4095.0) * 3.3;
    
    // Simulate temperature reading from internal sensor
    float temperature = 25.5 + (adc_raw / 4095.0) * 10;
    
    StaticJsonDocument<300> doc;
    doc["device_id"] = MQTT_CLIENT_ID;
    doc["timestamp"] = millis();
    doc["adc_raw"] = adc_raw;
    doc["voltage"] = voltage;
    doc["temperature"] = temperature;
    doc["led_state"] = digitalRead(LED_PIN);
    
    char buffer[512];
    size_t n = serializeJson(doc, buffer);
    
    client.publish(TOPIC_SENSOR_DATA, buffer, n);
    Serial.print("Sensor: ");
    Serial.println(buffer);
}

void messageCallback(char* topic, byte* payload, unsigned int length) {
    Serial.print("Message on topic: ");
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
        
        Serial.print("LED: ");
        Serial.println(ledState ? "ON" : "OFF");
    }
    
    if (doc.containsKey("blink")) {
        int count = doc["blink"];
        for (int i = 0; i < count; i++) {
            digitalWrite(LED_PIN, HIGH);
            delay(200);
            digitalWrite(LED_PIN, LOW);
            delay(200);
        }
    }
}

// ============ Interrupt Handler ============

void buttonISR() {
    buttonPressed = true;
}
