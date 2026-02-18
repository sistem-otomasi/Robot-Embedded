# Contoh Penggunaan ROS2 Detection Packages

## 📋 Daftar Isi

1. [Deteksi dari File Video (.mov)](#1-deteksi-dari-file-video-mov)
2. [Deteksi dari Kamera Live](#2-deteksi-dari-kamera-live)
3. [Custom Configuration](#3-custom-configuration)
4. [Viewing Results](#4-viewing-results)
5. [Recording Output](#5-recording-output)

## 1. Deteksi dari File Video (.mov)

### Menggunakan UI (Graphical Interface)

```bash
cd ros2_ws
source install/setup.bash

# Jalankan file selector GUI
ros2 run video_publisher video_file_selector.py
```

Langkah-langkah:
1. Klik "Browse Video File"
2. Pilih file video (.mov, .mp4, .avi)
3. Pilih detector yang diinginkan
4. Klik "Run Detection"

### Menggunakan Command Line

#### A. YOLO Only (Object Detection)

**Terminal 1** - Video Publisher:
```bash
cd ros2_ws
source install/setup.bash
ros2 run video_publisher video_publisher_node.py \
  --ros-args -p video_file:=/home/user/videos/car_driving.mov
```

**Terminal 2** - YOLO Detector:
```bash
cd ros2_ws
source install/setup.bash
ros2 launch yolo_detector yolo_detector.launch.py
```

**Terminal 3** - View Results:
```bash
ros2 run rqt_image_view rqt_image_view
# Pilih topic: /yolo/image_detected
```

#### B. LaneNet Only (Lane Detection)

**Terminal 1** - Video Publisher:
```bash
cd ros2_ws
source install/setup.bash
ros2 run video_publisher video_publisher_node.py \
  --ros-args -p video_file:=/home/user/videos/highway.mov
```

**Terminal 2** - LaneNet Detector:
```bash
cd ros2_ws
source install/setup.bash
ros2 launch lanenet_detector lanenet_detector.launch.py
```

**Terminal 3** - View Results:
```bash
ros2 run rqt_image_view rqt_image_view
# Pilih topic: /lanenet/image_detected
```

#### C. Combined (YOLO + LaneNet)

**Terminal 1** - Video Publisher:
```bash
cd ros2_ws
source install/setup.bash
ros2 run video_publisher video_publisher_node.py \
  --ros-args -p video_file:=/home/user/videos/city_drive.mov
```

**Terminal 2** - Combined Detector:
```bash
cd ros2_ws
source install/setup.bash
ros2 launch yolo_lanenet_detector yolo_lanenet_detector.launch.py
```

**Terminal 3** - View Results:
```bash
ros2 run rqt_image_view rqt_image_view
# Pilih topic: /combined/image_detected
```

### Quick Start Script

```bash
cd ros2_ws

# Dengan GUI
./quick_start.sh

# Atau langsung dengan file video
./quick_start.sh /path/to/video.mov
```

## 2. Deteksi dari Kamera Live

### Install USB Camera Package

```bash
sudo apt install ros-humble-usb-cam
```

### Setup dan Run

**Terminal 1** - USB Camera:
```bash
ros2 run usb_cam usb_cam_node_exe \
  --ros-args -p video_device:=/dev/video0
```

**Terminal 2** - Run Detector:
```bash
cd ros2_ws
source install/setup.bash

# Pilih salah satu:
ros2 launch yolo_detector yolo_detector.launch.py
# atau
ros2 launch lanenet_detector lanenet_detector.launch.py
# atau
ros2 launch yolo_lanenet_detector yolo_lanenet_detector.launch.py
```

**Terminal 3** - View Results:
```bash
ros2 run rqt_image_view rqt_image_view
```

## 3. Custom Configuration

### YOLO dengan Model Custom

```bash
# Download model YOLOv8 medium
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8m.pt

# Run dengan model custom
ros2 launch yolo_detector yolo_detector.launch.py \
  model_path:=/home/user/models/yolov8m.pt \
  confidence_threshold:=0.7
```

### LaneNet dengan ROI Custom

```bash
ros2 launch lanenet_detector lanenet_detector.launch.py \
  roi_top:=0.4
```

### Combined dengan Custom Settings

```bash
ros2 launch yolo_lanenet_detector yolo_lanenet_detector.launch.py \
  yolo_model_path:=yolov8s.pt \
  confidence_threshold:=0.6 \
  device:=cuda
```

### Video Publisher dengan Options

```bash
# Loop disabled (play once)
ros2 run video_publisher video_publisher_node.py \
  --ros-args \
  -p video_file:=/path/to/video.mov \
  -p loop:=false

# Custom frame rate
ros2 run video_publisher video_publisher_node.py \
  --ros-args \
  -p video_file:=/path/to/video.mov \
  -p frame_rate:=15.0

# Resize untuk performance
ros2 run video_publisher video_publisher_node.py \
  --ros-args \
  -p video_file:=/path/to/video.mov \
  -p resize_width:=640 \
  -p resize_height:=480

# Start dari frame tertentu
ros2 run video_publisher video_publisher_node.py \
  --ros-args \
  -p video_file:=/path/to/video.mov \
  -p start_frame:=100
```

## 4. Viewing Results

### Menggunakan rqt_image_view

```bash
ros2 run rqt_image_view rqt_image_view
```

Pilih topic dari dropdown:
- `/yolo/image_detected` - YOLO detection
- `/lanenet/image_detected` - Lane detection
- `/combined/image_detected` - Combined detection
- `/camera/image_raw` - Original video

### Menggunakan ros2 topic echo

**View detection data:**
```bash
# YOLO detections
ros2 topic echo /yolo/detections

# Lane coordinates
ros2 topic echo /lanenet/lanes

# Combined detections
ros2 topic echo /combined/detections
ros2 topic echo /combined/lanes
```

**Check topic info:**
```bash
ros2 topic list
ros2 topic info /yolo/image_detected
ros2 topic hz /camera/image_raw
```

## 5. Recording Output

### Record ke ROS Bag

```bash
# Record semua topics
ros2 bag record -a

# Record specific topics
ros2 bag record /combined/image_detected /combined/detections /combined/lanes

# Record dengan nama custom
ros2 bag record -o my_detection_output /combined/image_detected
```

### Save Video dari Topic

Menggunakan `image_tools`:

```bash
sudo apt install ros-humble-image-tools

# Convert topic ke video
ros2 run image_tools cam2image \
  --ros-args -p topic:=/combined/image_detected
```

Atau gunakan script Python untuk save:

```python
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

class ImageSaver(Node):
    def __init__(self):
        super().__init__('image_saver')
        self.bridge = CvBridge()
        self.writer = cv2.VideoWriter(
            'output.mp4',
            cv2.VideoWriter_fourcc(*'mp4v'),
            30.0,
            (640, 480)
        )
        self.sub = self.create_subscription(
            Image,
            '/combined/image_detected',
            self.callback,
            10
        )
    
    def callback(self, msg):
        cv_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        self.writer.write(cv_image)

def main():
    rclpy.init()
    node = ImageSaver()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.writer.release()
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## 🎯 Tips & Tricks

### Performance Optimization

1. **Gunakan model YOLO lebih kecil:**
   - `yolov8n.pt` - Fastest (nano)
   - `yolov8s.pt` - Fast (small)
   - `yolov8m.pt` - Medium
   - `yolov8l.pt` - Large
   - `yolov8x.pt` - Best accuracy (xlarge)

2. **Resize video untuk FPS lebih tinggi:**
   ```bash
   -p resize_width:=640 -p resize_height:=480
   ```

3. **Kurangi frame rate:**
   ```bash
   -p frame_rate:=15.0
   ```

4. **Gunakan GPU jika tersedia:**
   ```bash
   device:=cuda
   ```

### Debugging

```bash
# Check jika nodes running
ros2 node list

# Check node info
ros2 node info /yolo_detector_node

# Check topics
ros2 topic list

# Monitor topic frequency
ros2 topic hz /camera/image_raw

# View logs
ros2 run rqt_console rqt_console
```

### Multiple Video Streams

```bash
# Video 1
ros2 run video_publisher video_publisher_node.py \
  --ros-args \
  -p video_file:=/path/to/video1.mov \
  -p output_topic:=/camera1/image_raw

# Video 2
ros2 run video_publisher video_publisher_node.py \
  --ros-args \
  -p video_file:=/path/to/video2.mov \
  -p output_topic:=/camera2/image_raw

# Detector for camera 1
ros2 launch yolo_detector yolo_detector.launch.py \
  image_topic:=/camera1/image_raw

# Detector for camera 2
ros2 launch lanenet_detector lanenet_detector.launch.py \
  image_topic:=/camera2/image_raw
```

## 📞 Support

Jika mengalami masalah, cek:
1. Log ROS2: `ros2 run rqt_console rqt_console`
2. Topic status: `ros2 topic list` dan `ros2 topic hz <topic>`
3. Node status: `ros2 node list` dan `ros2 node info <node>`

Untuk pertanyaan lebih lanjut, buka issue di repository.
