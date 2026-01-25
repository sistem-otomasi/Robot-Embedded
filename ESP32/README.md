# ESP32 Embedded System - ROS Communication

Firmware untuk ESP32 untuk berkomunikasi dengan ROS2 melalui MQTT bridge.

## Fitur
- WiFi connectivity
- MQTT communication dengan MiniPC
- Heartbeat monitoring
- Sensor data publishing
- Control command handling
- Real-time status updates

## Komponen

### Hardware
- ESP32-WROOM-32
- 1x LED (GPIO 2)
- 1x Push Button (GPIO 0)
- 1x Analog Sensor (A0)

### Software Dependencies
- Arduino IDE atau PlatformIO
- ArduinoJson library
- PubSubClient library

## Instalasi

### Menggunakan PlatformIO

```bash
cd Embedded/ESP32
pio run -t upload -e esp32-wroom-32
pio device monitor
```

### Menggunakan Arduino IDE

1. Install board ESP32: https://github.com/espressif/arduino-esp32
2. Install libraries:
   - ArduinoJson
   - PubSubClient
3. Upload sketch ke board

## Konfigurasi

Edit `src/main.cpp` dan ubah:

```cpp
const char* WIFI_SSID = "YOUR_SSID";
const char* WIFI_PASSWORD = "YOUR_PASSWORD";
const char* MQTT_BROKER = "192.168.1.100";  // IP MiniPC
```

## MQTT Topics

**Publishing:**
- `robot/embedded/heartbeat` - Heartbeat signal dengan metadata
- `robot/embedded/sensors` - Sensor readings (ADC, temperature, humidity)
- `robot/embedded/status` - Device status dan aksi response

**Subscribing:**
- `robot/control/command` - Perintah dari ROS untuk kontrol LED, dll

## Contoh Payload

### Heartbeat
```json
{
  "device_id": "esp32_embedded_01",
  "timestamp": 120000,
  "uptime_ms": 120000,
  "rssi": -45,
  "ip": "192.168.1.50"
}
```

### Sensor Data
```json
{
  "device_id": "esp32_embedded_01",
  "timestamp": 120000,
  "adc_raw": 2048,
  "voltage": 1.65,
  "temperature": 25.5,
  "humidity": 60.0,
  "led_state": 0
}
```

### Control Command (dari ROS)
```json
{
  "led": true,
  "delay": 500
}
```

## Testing

### Monitor Serial Output
```bash
pio device monitor --baud 115200
```

### Publish Test Command
```bash
mosquitto_pub -h 192.168.1.100 -t "robot/control/command" -m '{"led": true}'
```

### Subscribe to Topics
```bash
mosquitto_sub -h 192.168.1.100 -t "robot/embedded/#"
```
