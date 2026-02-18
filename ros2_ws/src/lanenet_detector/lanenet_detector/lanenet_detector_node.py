#!/usr/bin/env python3
"""
LaneNet Lane Detection Node for ROS2 Humble
Detects lane lines in camera images using computer vision
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Point
from std_msgs.msg import Header, Float32MultiArray
from cv_bridge import CvBridge
import cv2
import numpy as np


class LaneNetDetectorNode(Node):
    """LaneNet Lane Detection Node"""
    
    def __init__(self):
        super().__init__('lanenet_detector_node')
        
        # Declare parameters
        self.declare_parameter('image_topic', '/camera/image_raw')
        self.declare_parameter('lane_topic', '/lanenet/lanes')
        self.declare_parameter('visualization_topic', '/lanenet/image_detected')
        self.declare_parameter('roi_top', 0.5)
        self.declare_parameter('roi_bottom', 1.0)
        self.declare_parameter('canny_low', 50)
        self.declare_parameter('canny_high', 150)
        self.declare_parameter('hough_threshold', 50)
        self.declare_parameter('hough_min_line_length', 100)
        self.declare_parameter('hough_max_line_gap', 50)
        
        # Get parameters
        image_topic = self.get_parameter('image_topic').value
        lane_topic = self.get_parameter('lane_topic').value
        visualization_topic = self.get_parameter('visualization_topic').value
        self.roi_top = self.get_parameter('roi_top').value
        self.roi_bottom = self.get_parameter('roi_bottom').value
        self.canny_low = self.get_parameter('canny_low').value
        self.canny_high = self.get_parameter('canny_high').value
        self.hough_threshold = self.get_parameter('hough_threshold').value
        self.hough_min_line_length = self.get_parameter('hough_min_line_length').value
        self.hough_max_line_gap = self.get_parameter('hough_max_line_gap').value
        
        # Initialize CV Bridge
        self.bridge = CvBridge()
        
        # Create subscribers
        self.image_sub = self.create_subscription(
            Image,
            image_topic,
            self.image_callback,
            10
        )
        
        # Create publishers
        self.lane_pub = self.create_publisher(
            Float32MultiArray,
            lane_topic,
            10
        )
        
        self.visualization_pub = self.create_publisher(
            Image,
            visualization_topic,
            10
        )
        
        self.get_logger().info('LaneNet Detector Node initialized')
    
    def region_of_interest(self, img, vertices):
        """Apply region of interest mask"""
        mask = np.zeros_like(img)
        cv2.fillPoly(mask, vertices, 255)
        masked_image = cv2.bitwise_and(img, mask)
        return masked_image
    
    def detect_lanes(self, image):
        """Detect lane lines using classical computer vision"""
        height, width = image.shape[:2]
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply Canny edge detection
        edges = cv2.Canny(blur, self.canny_low, self.canny_high)
        
        # Define region of interest
        roi_vertices = np.array([[
            (0, height),
            (0, int(height * self.roi_top)),
            (width, int(height * self.roi_top)),
            (width, height)
        ]], dtype=np.int32)
        
        # Apply region of interest mask
        masked_edges = self.region_of_interest(edges, roi_vertices)
        
        # Detect lines using Hough transform
        lines = cv2.HoughLinesP(
            masked_edges,
            rho=1,
            theta=np.pi/180,
            threshold=self.hough_threshold,
            minLineLength=self.hough_min_line_length,
            maxLineGap=self.hough_max_line_gap
        )
        
        return lines
    
    def draw_lanes(self, image, lines):
        """Draw detected lane lines on image"""
        lane_image = np.copy(image)
        
        if lines is not None:
            left_lines = []
            right_lines = []
            
            height, width = image.shape[:2]
            mid_x = width // 2
            
            for line in lines:
                x1, y1, x2, y2 = line[0]
                
                # Calculate slope
                if x2 - x1 == 0:
                    continue
                slope = (y2 - y1) / (x2 - x1)
                
                # Filter by slope and position
                if slope < -0.5 and x1 < mid_x and x2 < mid_x:
                    left_lines.append(line[0])
                elif slope > 0.5 and x1 > mid_x and x2 > mid_x:
                    right_lines.append(line[0])
            
            # Draw left lane
            if left_lines:
                for line in left_lines:
                    x1, y1, x2, y2 = line
                    cv2.line(lane_image, (x1, y1), (x2, y2), (0, 255, 0), 5)
            
            # Draw right lane
            if right_lines:
                for line in right_lines:
                    x1, y1, x2, y2 = line
                    cv2.line(lane_image, (x1, y1), (x2, y2), (0, 0, 255), 5)
        
        return lane_image
    
    def image_callback(self, msg):
        """Process incoming image messages"""
        try:
            # Convert ROS Image to OpenCV
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            
            # Detect lanes
            lines = self.detect_lanes(cv_image)
            
            # Create lane message
            lane_msg = Float32MultiArray()
            if lines is not None:
                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    lane_msg.data.extend([float(x1), float(y1), float(x2), float(y2)])
            
            # Publish lane data
            self.lane_pub.publish(lane_msg)
            
            # Create visualization
            lane_image = self.draw_lanes(cv_image, lines)
            
            # Publish visualization
            viz_msg = self.bridge.cv2_to_imgmsg(lane_image, encoding='bgr8')
            viz_msg.header = Header()
            viz_msg.header.stamp = self.get_clock().now().to_msg()
            viz_msg.header.frame_id = msg.header.frame_id
            self.visualization_pub.publish(viz_msg)
            
        except Exception as e:
            self.get_logger().error(f'Error processing image: {e}')


def main(args=None):
    rclpy.init(args=args)
    
    node = LaneNetDetectorNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
