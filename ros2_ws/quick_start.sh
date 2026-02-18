#!/bin/bash
# Quick start script untuk testing ROS2 detection packages
# Menjalankan combined detector (YOLO + LaneNet)

set -e

echo "=========================================="
echo "ROS2 YOLO + LaneNet Quick Start"
echo "=========================================="
echo ""

# Check if workspace is built
if [ ! -d "install" ]; then
    echo "Error: Workspace not built!"
    echo "Please run: ./build.sh first"
    exit 1
fi

# Source workspace
source install/setup.bash

# Check for video file argument
if [ -z "$1" ]; then
    echo "Starting video file selector UI..."
    echo ""
    ros2 run video_publisher video_file_selector.py
else
    VIDEO_FILE="$1"
    
    if [ ! -f "$VIDEO_FILE" ]; then
        echo "Error: Video file not found: $VIDEO_FILE"
        exit 1
    fi
    
    echo "Video file: $VIDEO_FILE"
    echo ""
    echo "Starting detection pipeline..."
    echo ""
    echo "Terminal 1: Video Publisher (this terminal)"
    echo "Terminal 2: Open another terminal and run:"
    echo "  cd $(pwd) && source install/setup.bash"
    echo "  ros2 launch yolo_lanenet_detector yolo_lanenet_detector.launch.py"
    echo ""
    echo "Terminal 3: To view results, run:"
    echo "  ros2 run rqt_image_view rqt_image_view"
    echo "  Then select topic: /combined/image_detected"
    echo ""
    echo "Press Ctrl+C to stop"
    echo ""
    
    # Start video publisher
    ros2 run video_publisher video_publisher_node.py \
        --ros-args -p video_file:="$VIDEO_FILE"
fi
