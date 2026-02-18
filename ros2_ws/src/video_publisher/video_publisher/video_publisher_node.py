#!/usr/bin/env python3
"""
Video File Publisher Node for ROS2 Humble
Publishes video frames from .mov, .mp4, .avi files to ROS2 topics
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import Header
from cv_bridge import CvBridge
import cv2
import os
import sys


class VideoPublisherNode(Node):
    """Video File Publisher Node"""
    
    def __init__(self):
        super().__init__('video_publisher_node')
        
        # Declare parameters
        self.declare_parameter('video_file', '')
        self.declare_parameter('output_topic', '/camera/image_raw')
        self.declare_parameter('frame_rate', 30.0)
        self.declare_parameter('loop', True)
        self.declare_parameter('start_frame', 0)
        self.declare_parameter('resize_width', 0)
        self.declare_parameter('resize_height', 0)
        
        # Get parameters
        self.video_file = self.get_parameter('video_file').value
        output_topic = self.get_parameter('output_topic').value
        frame_rate = self.get_parameter('frame_rate').value
        self.loop = self.get_parameter('loop').value
        start_frame = self.get_parameter('start_frame').value
        self.resize_width = self.get_parameter('resize_width').value
        self.resize_height = self.get_parameter('resize_height').value
        
        # Validate video file
        if not self.video_file:
            self.get_logger().error('No video file specified! Use parameter video_file')
            sys.exit(1)
        
        if not os.path.exists(self.video_file):
            self.get_logger().error(f'Video file not found: {self.video_file}')
            sys.exit(1)
        
        # Initialize CV Bridge
        self.bridge = CvBridge()
        
        # Open video file
        self.cap = cv2.VideoCapture(self.video_file)
        
        if not self.cap.isOpened():
            self.get_logger().error(f'Failed to open video file: {self.video_file}')
            sys.exit(1)
        
        # Get video properties
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.original_fps = self.cap.get(cv2.CAP_PROP_FPS)
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Set start frame
        if start_frame > 0:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        
        self.get_logger().info(f'Video file: {self.video_file}')
        self.get_logger().info(f'Resolution: {width}x{height}')
        self.get_logger().info(f'FPS: {self.original_fps}')
        self.get_logger().info(f'Total frames: {self.total_frames}')
        self.get_logger().info(f'Publishing to: {output_topic}')
        
        # Create publisher
        self.image_pub = self.create_publisher(
            Image,
            output_topic,
            10
        )
        
        # Create timer for publishing frames
        timer_period = 1.0 / frame_rate
        self.timer = self.create_timer(timer_period, self.timer_callback)
        
        self.frame_count = 0
        self.get_logger().info('Video Publisher Node initialized')
    
    def timer_callback(self):
        """Publish video frame"""
        ret, frame = self.cap.read()
        
        if not ret:
            if self.loop:
                # Restart video from beginning
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.cap.read()
                self.get_logger().info('Restarting video...')
                if not ret:
                    self.get_logger().error('Failed to restart video')
                    return
            else:
                self.get_logger().info('Video ended')
                self.timer.cancel()
                return
        
        # Resize if needed
        if self.resize_width > 0 and self.resize_height > 0:
            frame = cv2.resize(frame, (self.resize_width, self.resize_height))
        
        # Convert to ROS Image message
        try:
            msg = self.bridge.cv2_to_imgmsg(frame, encoding='bgr8')
            msg.header = Header()
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.header.frame_id = 'camera'
            
            # Publish
            self.image_pub.publish(msg)
            
            self.frame_count += 1
            if self.frame_count % 100 == 0:
                self.get_logger().info(f'Published frame {self.frame_count}/{self.total_frames}')
                
        except Exception as e:
            self.get_logger().error(f'Error publishing frame: {e}')
    
    def destroy_node(self):
        """Cleanup on shutdown"""
        if self.cap:
            self.cap.release()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    
    node = VideoPublisherNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
