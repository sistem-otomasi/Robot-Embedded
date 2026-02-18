# Robot Embedded-to-ROS Communication System

Sistem komunikasi lengkap antara embedded devices (ESP32/STM32) dengan ROS2 yang berjalan di MiniPC, termasuk package deteksi objek (YOLO) dan deteksi garis (LaneNet).

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      EMBEDDED SYSTEMS                            │
│  ┌─────────────────┐  ┌──────────────────┐  ┌─────────────────┐ │
│  │   ESP32-WROOM   │  │  STM32F4         │  │  STM32F1        │ │
│  │   (WiFi)        │  │  (Ethernet)      │  │  (WiFi Shield)  │ │
│  └────────┬────────┘  └────────┬─────────┘  └────────┬────────┘ │
│           │                    │                      │           │
│           │ WiFi              │ Ethernet            │ WiFi       │
└───────────┼────────────────────┼──────────────────────┼───────────┘
            │                    │                      │
            │                    └──────────┬───────────┘
            │                               │
            │         ┌──────────────────────┘
            │         │
            └─────────┴──────────┬─────────────────────┐
                                 │                     │
                          ┌──────▼──────┐      ┌──────▼──────┐
                          │   MQTT      │      │   Network   │
                          │   Broker    │      │   Switch    │
                          └──────┬──────┘      └─────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │      MiniPC ROS2        │
                    │  ┌──────────────────┐   │
                    │  │ MQTT to ROS      │   │
                    │  │ Bridge Node      │   │
                    │  └──────────────────┘   │
                    │  ┌──────────────────┐   │
                    │  │ YOLO Detector    │   │
                    │  │ LaneNet Detector │   │
                    │  └──────────────────┘   │
                    │  Topics:                │
                    │  - Sensor data          │
                    │  - Heartbeat            │
                    │  - Status               │
                    │  - Control commands     │
                    │  - Object detection     │
                    │  - Lane detection       │
                    └─────────────────────────┘
```

## 📦 Repository Structure

```
Robot-Embedded/
├── ESP32/              # ESP32 firmware untuk WiFi communication
├── STM32/              # STM32 firmware untuk Ethernet communication
├── ros2_ws/            # ROS2 workspace untuk vision & detection
│   ├── src/
│   │   ├── yolo_detector/           # YOLO object detection
│   │   ├── lanenet_detector/        # LaneNet lane detection
│   │   ├── yolo_lanenet_detector/   # Combined detector
│   │   └── video_publisher/         # Video file publisher (.mov support)
│   ├── build.sh        # Build script
│   ├── requirements.txt
│   └── README.md       # Detailed ROS2 documentation
└── README.md           # This file
```

## 🚀 Quick Start

### ROS2 Vision Detection Packages (YOLO & LaneNet)

Untuk setup lengkap YOLO, LaneNet, dan Video Publisher (.mov file support), lihat:

**📖 [ROS2 Packages Documentation](ros2_ws/README.md)**

Quick commands:
```bash
# Build packages
cd ros2_ws
./build.sh

# Source workspace
source install/setup.bash

# Run video file selector UI
ros2 run video_publisher video_file_selector.py

# Atau manual dengan command line
ros2 run video_publisher video_publisher_node.py \
  --ros-args -p video_file:=/path/to/video.mov

ros2 launch yolo_lanenet_detector yolo_lanenet_detector.launch.py
```

### 1. Setup Embedded Device (pilih salah satu)

#### Option A: ESP32 dengan WiFi

```bash
cd Embedded/ESP32
# Edit platformio.ini dan src/main.cpp untuk WiFi credentials
nano src/main.cpp

# Upload ke board
pio run -t upload -e esp32-wroom-32
pio device monitor --baud 115200
```

#### Option B: STM32F4 dengan Ethernet

```bash
cd Embedded/STM32
# Update MAC address dan IP configuration
nano src/main.cpp

# Build dan upload dengan STM32CubeIDE atau PlatformIO
pio run -t upload -e stm32f407vg
```

### 2. Setup MQTT Broker di MiniPC

```bash
# Install Mosquitto
sudo apt install mosquitto mosquitto-clients

# Start broker
sudo systemctl start mosquitto
sudo systemctl status mosquitto

# Enable di startup
sudo systemctl enable mosquitto

# Test connection
mosquitto_pub -h localhost -t test/topic -m "hello"
```

### 3. Build ROS2 Package

```bash
cd ~/robot_ws  # Workspace ROS2 Anda
cp -r /root/Otomasi/Sistem-Otomasi-Robot/MiniPC/ros2_packages/embedded_bridge src/

# Install dependencies
rosdep install --from-paths src --ignore-src -y

# Build
colcon build --packages-select embedded_bridge

# Source
source install/setup.bash
```

### 4. Launch Embedded Bridge

```bash
# Dengan default config (localhost:1883)
ros2 launch embedded_bridge embedded_bridge.launch.py

# Dengan custom MQTT broker IP
ros2 launch embedded_bridge embedded_bridge.launch.py mqtt_broker:=192.168.1.100
```

## 📡 Communication Protocol

### MQTT Topic Hierarchy

```
robot/
├── embedded/
│   ├── heartbeat     ← Device heartbeat + metadata
│   ├── sensors       ← Sensor readings (ADC, temp, humidity)
│   └── status        ← Device status & action responses
└── control/
    └── command       ← Control commands untuk device
```

### Message Flow Diagram

```
ESP32/STM32                    MQTT Broker              ROS2 MiniPC
    │                               │                        │
    ├──── Publish Heartbeat ───────→│                        │
    │                               ├─── Forward to ROS ───→│
    │                               │                        │
    ├──── Publish Sensors ─────────→│                        │
    │                               ├─── Convert to Topic ──→│
    │                               │                        │
    │                               │←─ Subscribe Topics ────│
    │                               │                        │
    │←── Subscribe Command ─────────┤←─ Publish Command ────│
    │                               │                        │
    ├──── Publish Status ──────────→│                        │
    │ (acknowledgment)              ├─── Forward to ROS ───→│
```

## 🔌 Wiring Diagram

### ESP32 Setup

```
┌─────────────────┐
│    ESP32-32     │
│                 │
│ GPIO2 ──→ LED   │
│ GPIO0 ──→ BTN   │
│ A0 ───→ ADC     │
│ GND ──→ GND     │
│ 3.3V ──→ VCC    │
└─────────────────┘
         │
      WiFi
         │
    Router/AP
```

### STM32F4 Setup

```
┌──────────────────┐
│  STM32F407VG     │
│                  │
│ PA1 ──→ LED      │
│ PA0 ──→ BTN      │
│ PA4 ──→ ADC      │
│ ETH ──→ RJ45     │
│ 3.3V ──→ VCC     │
└──────────────────┘
         │
      Ethernet
         │
    Network Switch
```

## 📊 Data Examples

### Heartbeat Message
```json
{
  "device_id": "esp32_embedded_01",
  "timestamp": 120000,
  "uptime_ms": 120000,
  "rssi": -45,
  "ip": "192.168.1.50"
}
```

### Sensor Data Message
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

### Control Command
```json
{
  "led": true,
  "blink": 5,
  "delay": 500
}
```

## 🧪 Testing & Verification

### Test 1: Verify MQTT Broker

```bash
# Terminal 1: Listen to all topics
mosquitto_sub -h localhost -t "robot/#" -v

# Terminal 2: Publish test message
mosquitto_pub -h localhost -t "robot/test/message" -m "Hello MQTT"
```

### Test 2: Check Embedded Device Connection

```bash
# Monitor broker for device heartbeat
mosquitto_sub -h 192.168.1.100 -t "robot/embedded/heartbeat" -v

# Check ESP32 serial output
pio device monitor --baud 115200
```

### Test 3: ROS2 Topic Verification

```bash
# List all topics
ros2 topic list

# Echo sensor data
ros2 topic echo /robot/embedded/sensors

# Publish control command
ros2 topic pub -1 /robot/control/command std_msgs/String "data: '{\"led\": true}'"
```

### Test 4: End-to-End Test

```bash
# Terminal 1: Monitor sensors in ROS
ros2 topic echo /robot/embedded/sensors

# Terminal 2: Send LED control via MQTT
mosquitto_pub -h localhost -t "robot/control/command" -m '{"led": true}'

# Observe: LED harus menyala di board
```

## 🔧 Troubleshooting

### Problem: "MQTT Connection Refused"

**Check:**
```bash
# Is mosquitto running?
sudo systemctl status mosquitto

# Is port 1883 listening?
sudo netstat -tlnp | grep mosquitto

# Firewall?
sudo ufw allow 1883
```

**Solution:**
```bash
sudo systemctl restart mosquitto
```

### Problem: "Embedded device not connecting"

**ESP32:**
```bash
# Check WiFi credentials
nano Embedded/ESP32/src/main.cpp

# Serial monitor
pio device monitor --baud 115200

# Check WiFi network availability
# Verify MQTT broker IP address is correct
```

**STM32F4:**
```bash
# Check Ethernet cable
# Verify MAC address in code
# Check network settings

# Test with ping
ping 192.168.1.101
```

### Problem: "ROS not receiving data"

```bash
# Check bridge node running
ros2 node list

# Check if node has errors
ros2 node info /embedded_bridge

# Monitor MQTT directly
mosquitto_sub -h localhost -t "robot/embedded/#" -v

# Enable debug logging
ros2 launch embedded_bridge embedded_bridge.launch.py | grep -i "ERROR\|WARN"
```

## 📈 Performance Monitoring

### Check latency

```bash
# Monitor message timestamps
ros2 topic echo /robot/embedded/sensors --field header.stamp
```

### Check message frequency

```bash
# Use rostopic tool
ros2 topic hz /robot/embedded/sensors
```

### Monitor MQTT broker

```bash
# Connect with client and monitor
mosquitto_sub -h localhost -t '$SYS/broker/clients/connected'
```

## 🔒 Security Considerations

### Current Setup (Development)
- No authentication
- No encryption
- Open MQTT broker

### Production Setup
```bash
# Enable Mosquitto authentication
sudo nano /etc/mosquitto/mosquitto.conf

# Add:
# allow_anonymous false
# password_file /etc/mosquitto/passwd

# Create password file
mosquitto_passwd -c /etc/mosquitto/passwd username

# Enable TLS
# certfile /path/to/cert.crt
# keyfile /path/to/key.key
```

## 📚 Additional Resources

### Embedded Code
- [ESP32 Program](Embedded/ESP32/README.md)
- [STM32 Program](Embedded/STM32/README.md)

### ROS2 Bridge
- [Bridge Node](MiniPC/ros2_packages/embedded_bridge/README.md)
- [Config File](MiniPC/ros2_packages/embedded_bridge/config/embedded_bridge.yaml)

### External References
- [ROS2 Documentation](https://docs.ros.org/en/humble/)
- [MQTT Protocol](http://mqtt.org/)
- [ESP32 Arduino Framework](https://github.com/espressif/arduino-esp32)
- [STM32 CubeIDE](https://www.st.com/en/development-tools/stm32cubeide.html)

## 📝 Development Workflow

### Adding New Sensor

1. **Embedded Side (ESP32/STM32):**
   ```cpp
   // Read sensor
   float new_sensor = readNewSensor();
   
   // Add to JSON
   doc["new_sensor"] = new_sensor;
   ```

2. **ROS Bridge Side:**
   ```cpp
   // Extract from JSON
   if (data.contains("new_sensor")) {
       msg.name.push_back("new_sensor");
       msg.position.push_back(data["new_sensor"].get<double>());
   }
   ```

3. **Test:**
   ```bash
   ros2 topic echo /robot/embedded/sensors
   ```

### Adding New Control Command

1. **ROS Side:** Publish new command via topic
2. **Bridge Side:** Will automatically forward to MQTT
3. **Embedded Side:** Handle in `handleControl()` function

## 📄 License

MIT License - See ROOT directory LICENSE file
