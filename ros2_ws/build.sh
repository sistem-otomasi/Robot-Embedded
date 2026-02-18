#!/bin/bash
# Build script untuk ROS2 packages
# YOLO, LaneNet, dan YOLO LaneNet Detector

set -e

echo "========================================"
echo "Building ROS2 Detection Packages"
echo "========================================"
echo ""

# Warna untuk output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Cek apakah ROS2 Humble terinstall
if ! command -v ros2 &> /dev/null; then
    echo -e "${RED}ERROR: ROS2 not found!${NC}"
    echo "Please install ROS2 Humble first."
    echo "See: https://docs.ros.org/en/humble/Installation.html"
    exit 1
fi

echo -e "${GREEN}✓ ROS2 found${NC}"

# Cek apakah di dalam workspace
if [ ! -d "src" ]; then
    echo -e "${RED}ERROR: Not in ROS2 workspace!${NC}"
    echo "Please run this script from ros2_ws directory"
    exit 1
fi

# Install Python dependencies
echo ""
echo -e "${YELLOW}Installing Python dependencies...${NC}"
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt
    echo -e "${GREEN}✓ Python dependencies installed${NC}"
else
    echo -e "${YELLOW}⚠ requirements.txt not found, skipping...${NC}"
fi

# Install ROS dependencies using rosdep
echo ""
echo -e "${YELLOW}Installing ROS2 dependencies...${NC}"
rosdep update || true
rosdep install --from-paths src --ignore-src -y
echo -e "${GREEN}✓ ROS2 dependencies installed${NC}"

# Clean previous build (optional)
if [ "$1" == "--clean" ]; then
    echo ""
    echo -e "${YELLOW}Cleaning previous build...${NC}"
    rm -rf build/ install/ log/
    echo -e "${GREEN}✓ Clean complete${NC}"
fi

# Build packages
echo ""
echo -e "${YELLOW}Building packages...${NC}"
echo ""

# Build dengan parallel jobs
colcon build \
    --symlink-install \
    --cmake-args -DCMAKE_BUILD_TYPE=Release \
    --parallel-workers $(nproc)

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}========================================"
    echo "✓ Build successful!"
    echo "========================================${NC}"
    echo ""
    echo "To use the packages, source the workspace:"
    echo "  source install/setup.bash"
    echo ""
    echo "Then you can run:"
    echo "  - Video file selector UI:"
    echo "    ros2 run video_publisher video_file_selector.py"
    echo ""
    echo "  - YOLO detector:"
    echo "    ros2 launch yolo_detector yolo_detector.launch.py"
    echo ""
    echo "  - LaneNet detector:"
    echo "    ros2 launch lanenet_detector lanenet_detector.launch.py"
    echo ""
    echo "  - Combined YOLO + LaneNet:"
    echo "    ros2 launch yolo_lanenet_detector yolo_lanenet_detector.launch.py"
    echo ""
else
    echo ""
    echo -e "${RED}========================================"
    echo "✗ Build failed!"
    echo "========================================${NC}"
    echo "Please check the error messages above."
    exit 1
fi
