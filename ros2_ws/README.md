# ROS2 YOLO, LaneNet, dan YOLO LaneNet Detector

Package ROS2 Humble untuk deteksi objek dan deteksi garis menggunakan YOLO dan LaneNet.

## 📦 Packages

Workspace ini berisi 4 package ROS2:

1. **yolo_detector** - Deteksi objek menggunakan YOLOv8
2. **lanenet_detector** - Deteksi garis menggunakan LaneNet (classical CV)
3. **yolo_lanenet_detector** - Gabungan YOLO + LaneNet untuk deteksi objek dan garis secara bersamaan
4. **video_publisher** - Publisher untuk file video (.mov, .mp4, .avi) dengan UI selector

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install ROS2 Humble (jika belum)
# Lihat: https://docs.ros.org/en/humble/Installation.html

# Install Python dependencies
cd ros2_ws
pip3 install -r requirements.txt

# Install ROS2 dependencies
sudo apt update
sudo apt install -y \
    ros-humble-cv-bridge \
    ros-humble-vision-msgs \
    ros-humble-image-transport \
    ros-humble-rqt-image-view

# Install rosdep dependencies
cd ros2_ws
rosdep install --from-paths src --ignore-src -y
```

### 2. Build Packages

```bash
cd ros2_ws

# Build semua packages
colcon build

# Atau build package tertentu
colcon build --packages-select yolo_detector
colcon build --packages-select lanenet_detector
colcon build --packages-select yolo_lanenet_detector
colcon build --packages-select video_publisher

# Source workspace
source install/setup.bash
```

### 3. Download YOLO Model

```bash
# YOLOv8 nano model (otomatis didownload saat pertama kali dijalankan)
# Atau download manual:
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt

# Model lain yang tersedia:
# yolov8s.pt (small)
# yolov8m.pt (medium)
# yolov8l.pt (large)
# yolov8x.pt (xlarge)
```

## 📹 Cara Menggunakan dengan File Video (.mov)

### Opsi 1: Menggunakan UI (Graphical User Interface)

```bash
# Source workspace terlebih dahulu
source install/setup.bash

# Jalankan video file selector dengan UI
ros2 run video_publisher video_file_selector.py
```

UI akan menampilkan:
- Tombol untuk browse file video (.mov, .mp4, .avi)
- Pilihan detector (YOLO, LaneNet, atau Combined)
- Tombol untuk run detection

### Opsi 2: Menggunakan Command Line

#### A. YOLO Object Detection

Terminal 1 - Video Publisher:
```bash
source install/setup.bash
ros2 run video_publisher video_publisher_node.py \
  --ros-args -p video_file:=/path/to/your/video.mov
```

Terminal 2 - YOLO Detector:
```bash
source install/setup.bash
ros2 launch yolo_detector yolo_detector.launch.py
```

Terminal 3 - View Results:
```bash
ros2 run rqt_image_view rqt_image_view
# Pilih topic: /yolo/image_detected
```

#### B. LaneNet Lane Detection

Terminal 1 - Video Publisher:
```bash
source install/setup.bash
ros2 run video_publisher video_publisher_node.py \
  --ros-args -p video_file:=/path/to/your/video.mov
```

Terminal 2 - LaneNet Detector:
```bash
source install/setup.bash
ros2 launch lanenet_detector lanenet_detector.launch.py
```

Terminal 3 - View Results:
```bash
ros2 run rqt_image_view rqt_image_view
# Pilih topic: /lanenet/image_detected
```

#### C. Combined YOLO + LaneNet Detection

Terminal 1 - Video Publisher:
```bash
source install/setup.bash
ros2 run video_publisher video_publisher_node.py \
  --ros-args -p video_file:=/path/to/your/video.mov
```

Terminal 2 - Combined Detector:
```bash
source install/setup.bash
ros2 launch yolo_lanenet_detector yolo_lanenet_detector.launch.py
```

Terminal 3 - View Results:
```bash
ros2 run rqt_image_view rqt_image_view
# Pilih topic: /combined/image_detected
```

## 🎥 Menggunakan dengan Kamera Live

Jika Anda ingin menggunakan kamera real-time instead of video file:

```bash
# Install usb_cam package
sudo apt install ros-humble-usb-cam

# Terminal 1 - Launch camera
ros2 run usb_cam usb_cam_node_exe

# Terminal 2 - Launch detector (pilih salah satu)
ros2 launch yolo_detector yolo_detector.launch.py
# atau
ros2 launch lanenet_detector lanenet_detector.launch.py
# atau
ros2 launch yolo_lanenet_detector yolo_lanenet_detector.launch.py
```

## 📊 Topics yang Dipublish

### YOLO Detector
- `/yolo/detections` - Detection2DArray (bounding boxes)
- `/yolo/image_detected` - Image (visualisasi)

### LaneNet Detector
- `/lanenet/lanes` - Float32MultiArray (koordinat garis)
- `/lanenet/image_detected` - Image (visualisasi)

### Combined Detector
- `/combined/detections` - Detection2DArray (bounding boxes)
- `/combined/lanes` - Float32MultiArray (koordinat garis)
- `/combined/image_detected` - Image (visualisasi)

### Video Publisher
- `/camera/image_raw` - Image (frame video)

## ⚙️ Configuration

Setiap package memiliki file konfigurasi di folder `config/`:

- `yolo_detector/config/yolo_params.yaml`
- `lanenet_detector/config/lanenet_params.yaml`
- `yolo_lanenet_detector/config/combined_params.yaml`

Edit file-file ini untuk mengubah parameter seperti:
- Threshold deteksi
- Model YOLO yang digunakan
- ROI untuk deteksi lane
- Parameter Canny dan Hough transform

## 🔧 Advanced Usage

### Custom YOLO Model

```bash
ros2 launch yolo_detector yolo_detector.launch.py \
  model_path:=/path/to/custom_model.pt \
  confidence_threshold:=0.7
```

### Video dengan Custom Frame Rate

```bash
ros2 run video_publisher video_publisher_node.py \
  --ros-args \
  -p video_file:=/path/to/video.mov \
  -p frame_rate:=15.0 \
  -p loop:=false
```

### Resize Video untuk Performance

```bash
ros2 run video_publisher video_publisher_node.py \
  --ros-args \
  -p video_file:=/path/to/video.mov \
  -p resize_width:=640 \
  -p resize_height:=480
```

## 🐛 Troubleshooting

### Error: "Ultralytics not installed"
```bash
pip3 install ultralytics
```

### Error: "No module named 'cv2'"
```bash
pip3 install opencv-python
```

### Error: "Failed to open video file"
- Pastikan path file video benar
- Pastikan format video didukung (.mov, .mp4, .avi)
- Coba convert video ke format lain: `ffmpeg -i input.mov output.mp4`

### Performance lambat
- Gunakan model YOLO yang lebih kecil (yolov8n.pt)
- Resize video ke resolusi lebih rendah
- Kurangi frame rate
- Gunakan GPU jika tersedia: `device:=cuda`

### GUI tidak muncul
```bash
# Install tkinter
sudo apt install python3-tk
```

## 📝 Development

### Struktur Package

```
ros2_ws/
├── src/
│   ├── yolo_detector/
│   │   ├── yolo_detector/
│   │   │   ├── __init__.py
│   │   │   └── yolo_detector_node.py
│   │   ├── launch/
│   │   │   └── yolo_detector.launch.py
│   │   ├── config/
│   │   │   └── yolo_params.yaml
│   │   ├── package.xml
│   │   ├── setup.py
│   │   └── CMakeLists.txt
│   │
│   ├── lanenet_detector/
│   ├── yolo_lanenet_detector/
│   └── video_publisher/
│
├── requirements.txt
└── README.md
```

## 📄 License

MIT License

## 👥 Contributors

Robot Embedded Team - Sistem Otomasi
