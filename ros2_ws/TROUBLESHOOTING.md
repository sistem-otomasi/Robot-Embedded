# Troubleshooting Guide

Panduan troubleshooting untuk masalah umum saat menggunakan ROS2 YOLO & LaneNet packages.

## 🔧 Installation Issues

### 1. ROS2 Humble tidak ditemukan

**Error:**
```
ros2: command not found
```

**Solution:**
```bash
# Install ROS2 Humble
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository universe
sudo apt update && sudo apt install curl -y
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
sudo apt update
sudo apt install ros-humble-desktop

# Source ROS2
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

### 2. Python dependencies gagal install

**Error:**
```
ModuleNotFoundError: No module named 'ultralytics'
```

**Solution:**
```bash
# Install dependencies
cd ros2_ws
pip3 install -r requirements.txt

# Atau install satu per satu
pip3 install ultralytics
pip3 install opencv-python
pip3 install torch torchvision
```

### 3. cv_bridge error

**Error:**
```
ModuleNotFoundError: No module named 'cv_bridge'
```

**Solution:**
```bash
sudo apt install ros-humble-cv-bridge
sudo apt install python3-opencv
```

## 🔨 Build Issues

### 1. colcon build gagal

**Error:**
```
CMake Error: Could not find a package configuration file
```

**Solution:**
```bash
# Install dependencies
sudo apt install python3-colcon-common-extensions
sudo apt install ros-humble-vision-msgs
sudo apt install ros-humble-geometry-msgs

# Clean dan rebuild
cd ros2_ws
rm -rf build/ install/ log/
colcon build
```

### 2. Package not found setelah build

**Error:**
```
Package 'yolo_detector' not found
```

**Solution:**
```bash
# Source workspace
cd ros2_ws
source install/setup.bash

# Verify package
ros2 pkg list | grep yolo
```

### 3. Permission denied on executables

**Error:**
```
Permission denied: './build.sh'
```

**Solution:**
```bash
chmod +x build.sh
chmod +x quick_start.sh
chmod +x ros2_ws/src/*/launch/*.py
```

## 📹 Video Issues

### 1. Failed to open video file

**Error:**
```
Failed to open video file: /path/to/video.mov
```

**Checks:**
1. File exists: `ls -la /path/to/video.mov`
2. File format supported: .mov, .mp4, .avi
3. OpenCV dapat membaca file

**Solution:**
```bash
# Cek dengan OpenCV Python
python3 << EOF
import cv2
cap = cv2.VideoCapture('/path/to/video.mov')
if cap.isOpened():
    print("Video OK")
else:
    print("Cannot open video")
cap.release()
EOF

# Convert ke format lain jika perlu
sudo apt install ffmpeg
ffmpeg -i input.mov -c:v libx264 output.mp4
```

### 2. Video playback too fast/slow

**Problem:**
Frame rate tidak sesuai

**Solution:**
```bash
# Adjust frame rate
ros2 run video_publisher video_publisher_node.py \
  --ros-args \
  -p video_file:=/path/to/video.mov \
  -p frame_rate:=15.0  # Sesuaikan nilai
```

### 3. GUI file selector tidak muncul

**Error:**
```
_tkinter.TclError: no display name and no $DISPLAY environment variable
```

**Solution:**
```bash
# Install tkinter
sudo apt install python3-tk

# Jika remote/SSH, enable X11 forwarding
ssh -X user@host

# Atau gunakan CLI mode (tanpa GUI)
ros2 run video_publisher video_publisher_node.py \
  --ros-args -p video_file:=/path/to/video.mov
```

## 🎯 Detection Issues

### 1. YOLO model tidak ter-download

**Error:**
```
ultralytics.utils.downloads.DownloadError
```

**Solution:**
```bash
# Download manual
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt

# Specify path
ros2 launch yolo_detector yolo_detector.launch.py \
  model_path:=/home/user/yolov8n.pt
```

### 2. No objects detected

**Problem:**
YOLO tidak mendeteksi objek apapun

**Checks:**
1. Confidence threshold terlalu tinggi
2. Model tidak cocok untuk kasus tertentu
3. Input image quality buruk

**Solution:**
```bash
# Lower confidence threshold
ros2 launch yolo_detector yolo_detector.launch.py \
  confidence_threshold:=0.3

# Gunakan model lebih besar
ros2 launch yolo_detector yolo_detector.launch.py \
  model_path:=yolov8m.pt
```

### 3. No lanes detected

**Problem:**
LaneNet tidak mendeteksi garis

**Checks:**
1. ROI tidak sesuai
2. Video tidak memiliki lane markings
3. Lighting conditions buruk

**Solution:**
```bash
# Adjust ROI
ros2 launch lanenet_detector lanenet_detector.launch.py \
  roi_top:=0.6

# Edit config file
nano src/lanenet_detector/config/lanenet_params.yaml
# Adjust canny_low, canny_high, hough_threshold
```

## 🚀 Performance Issues

### 1. Low FPS / Lag

**Problem:**
Detection running slow

**Solutions:**

```bash
# 1. Use smaller YOLO model
model_path:=yolov8n.pt  # Instead of yolov8x.pt

# 2. Resize video
ros2 run video_publisher video_publisher_node.py \
  --ros-args \
  -p video_file:=/path/to/video.mov \
  -p resize_width:=640 \
  -p resize_height:=480

# 3. Lower frame rate
-p frame_rate:=10.0

# 4. Use GPU if available
device:=cuda

# 5. Disable visualization
# Comment out visualization_pub.publish() in node code
```

### 2. High CPU usage

**Solution:**
```bash
# Limit CPU cores
colcon build --parallel-workers 2

# Use taskset to limit cores
taskset -c 0-3 ros2 launch yolo_detector yolo_detector.launch.py
```

### 3. Out of memory

**Error:**
```
RuntimeError: CUDA out of memory
```

**Solution:**
```bash
# Use CPU instead
device:=cpu

# Or reduce batch size in YOLO code
# Or use smaller model
model_path:=yolov8n.pt
```

## 📡 Topic/Communication Issues

### 1. No image on topic

**Problem:**
`ros2 topic echo /camera/image_raw` tidak menampilkan data

**Checks:**
```bash
# List topics
ros2 topic list

# Check topic type
ros2 topic info /camera/image_raw

# Check publisher
ros2 topic info /camera/image_raw -v

# Monitor frequency
ros2 topic hz /camera/image_raw
```

**Solution:**
```bash
# Restart nodes
# Ctrl+C and restart

# Check if video publisher running
ros2 node list | grep video
```

### 2. rqt_image_view shows black screen

**Problem:**
Viewer terbuka tapi tidak menampilkan image

**Solution:**
```bash
# Install rqt_image_view
sudo apt install ros-humble-rqt-image-view

# Restart dengan topic specific
ros2 run rqt_image_view rqt_image_view /camera/image_raw

# Check image encoding
ros2 topic echo /camera/image_raw --field encoding
```

### 3. Detection results tidak ter-publish

**Problem:**
Topic detection kosong

**Checks:**
```bash
# Check if detector node running
ros2 node list

# Check node logs
ros2 node info /yolo_detector_node

# View detailed logs
ros2 run rqt_console rqt_console
```

## 🐛 Common Errors

### Error: "Package not found after build"

```bash
cd ros2_ws
source install/setup.bash
ros2 pkg list | grep yolo
```

### Error: "symbol lookup error"

```bash
# Rebuild workspace
cd ros2_ws
rm -rf build/ install/ log/
./build.sh
source install/setup.bash
```

### Error: "Failed to load shared library"

```bash
# Update LD_LIBRARY_PATH
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/ros/humble/lib
```

### Error: "ImportError: cannot import name"

```bash
# Reinstall Python packages
pip3 uninstall ultralytics opencv-python
pip3 install ultralytics opencv-python
```

## 📚 Additional Help

### Enable debug logging

```bash
# Set ROS log level
export RCUTILS_CONSOLE_OUTPUT_FORMAT="[{severity}] [{name}]: {message}"
export RCUTILS_COLORIZED_OUTPUT=1

# Run with debug
ros2 run --prefix 'gdb -ex run --args' video_publisher video_publisher_node.py
```

### Check system requirements

```bash
# Check Python version (need 3.8+)
python3 --version

# Check ROS2 version
ros2 --version

# Check OpenCV
python3 -c "import cv2; print(cv2.__version__)"

# Check PyTorch (for YOLO)
python3 -c "import torch; print(torch.__version__)"
```

### Get help

```bash
# Package help
ros2 launch yolo_detector yolo_detector.launch.py --show-args

# Node help
ros2 run yolo_detector yolo_detector_node.py --help

# Topic info
ros2 topic info /yolo/image_detected
ros2 interface show vision_msgs/msg/Detection2DArray
```

## 🆘 Still Having Issues?

1. Check logs: `ros2 run rqt_console rqt_console`
2. Verify installation: Run `./build.sh` again
3. Test with simple video: Try with a small, simple .mp4 file
4. Check GitHub issues: https://github.com/sistem-otomasi/Robot-Embedded/issues
5. Create new issue with:
   - Error message
   - ROS2 version
   - Python version
   - Video file info
   - Steps to reproduce
