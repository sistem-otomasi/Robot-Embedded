# STM32 Embedded System - ROS Communication

Firmware untuk STM32F1/F4 untuk berkomunikasi dengan ROS2 melalui MQTT bridge.

## Hardware Support

- **STM32F407VG** - Discovery board dengan Ethernet
- **STM32F103RB** - Blue Pill dengan WiFi Shield (opsional)

## Fitur

- Ethernet connectivity (STM32F4) atau WiFi Shield
- MQTT communication dengan MiniPC
- ADC sensor reading
- Interrupt-based button handling
- LED control dari ROS
- Real-time heartbeat monitoring
- JSON serialization/deserialization

## Konektivitas

### STM32F4 (Ethernet)
```
STM32F407 --[Ethernet]--> Network Switch --> MiniPC
```

### STM32F1 (WiFi Shield)
```
STM32F103 --[SPI]--> WiFi Shield --> WiFi Router --> MiniPC
```

## Instalasi & Upload

### Menggunakan PlatformIO

```bash
cd Embedded/STM32

# Untuk STM32F4 Discovery
pio run -t upload -e stm32f407vg
pio device monitor

# Untuk STM32F1 Blue Pill
pio run -t upload -e stm32f103rb
```

### Menggunakan STM32CubeIDE

1. Buka STM32CubeIDE
2. Import project
3. Configure IDE untuk STM32
4. Build dan upload

## Konfigurasi

Edit `src/main.cpp` dan ubah network configuration:

```cpp
// Ethernet (STM32F4)
const char* MQTT_BROKER = "192.168.1.100";

// atau WiFi (dengan WiFi Shield)
const char* WIFI_SSID = "YOUR_SSID";
const char* WIFI_PASSWORD = "YOUR_PASSWORD";
```

## Pin Mapping

### STM32F407VG Discovery
- LED: PA1
- Button: PA0  
- ADC: PA4

### STM32F103RB Blue Pill
- LED: PB12
- Button: PB13
- ADC: PA0

## MQTT Communication

### Topics Published
- `robot/embedded/heartbeat` - Device status & uptime
- `robot/embedded/sensors` - ADC, temperature, humidity
- `robot/embedded/status` - Control response

### Topics Subscribed
- `robot/control/command` - Control commands (LED, blink, dll)

## Contoh Payload

### Control LED
```json
{
  "led": true
}
```

### Blink LED
```json
{
  "blink": 5
}
```

### Response
```json
{
  "action": "led_set",
  "state": true,
  "timestamp": 5000
}
```

## Troubleshooting

### Ethernet tidak terhubung
- Cek MAC address di setup
- Verify network cable
- Check router DHCP settings

### MQTT connection failed
- Verify MQTT broker IP address
- Check firewall rules
- Test dengan `mosquitto_pub/sub`

### Serial Monitor No Output
- Verify baud rate: 115200
- Check USB driver installation
- Try different USB cable

## Debug

Untuk debug lebih detail, ubah log level:

```cpp
#define DEBUG_ENABLED 1
```

## Testing

### Subscribe ke semua sensor data
```bash
mosquitto_sub -h 192.168.1.100 -t "robot/embedded/#" -v
```

### Send LED command
```bash
mosquitto_pub -h 192.168.1.100 -t "robot/control/command" -m '{"led":true}'
```

### Monitor serial output
```bash
pio device monitor --baud 115200 --raw
```
