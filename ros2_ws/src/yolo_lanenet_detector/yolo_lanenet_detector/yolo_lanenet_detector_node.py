#!/usr/bin/env python3
"""
Combined YOLO + LaneNet Detector Node for ROS2 Humble
Performs both object detection (YOLO) and lane detection (LaneNet) simultaneously
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from vision_msgs.msg import Detection2D, Detection2DArray, ObjectHypothesisWithPose
from std_msgs.msg import Header, Float32MultiArray
from cv_bridge import CvBridge
import cv2
import numpy as np

try:
    from ultralytics import YOLO
    ULTRALYTICS_AVAILABLE = True
except ImportError:
    ULTRALYTICS_AVAILABLE = False


class YOLOLaneNetDetectorNode(Node):
    """Combined YOLO + LaneNet Detector Node"""
    
    def __init__(self):
        super().__init__('yolo_lanenet_detector_node')
        
        # Declare parameters
        self.declare_parameter('yolo_model_path', 'yolov8n.pt')
        self.declare_parameter('confidence_threshold', 0.5)
        self.declare_parameter('iou_threshold', 0.45)
        self.declare_parameter('image_topic', '/camera/image_raw')
        self.declare_parameter('detection_topic', '/combined/detections')
        self.declare_parameter('lane_topic', '/combined/lanes')
        self.declare_parameter('visualization_topic', '/combined/image_detected')
        self.declare_parameter('device', 'cpu')
        
        # Lane detection parameters
        self.declare_parameter('roi_top', 0.5)
        self.declare_parameter('roi_bottom', 1.0)
        self.declare_parameter('canny_low', 50)
        self.declare_parameter('canny_high', 150)
        self.declare_parameter('hough_threshold', 50)
        self.declare_parameter('hough_min_line_length', 100)
        self.declare_parameter('hough_max_line_gap', 50)
        
        # Get parameters
        model_path = self.get_parameter('yolo_model_path').value
        self.confidence_threshold = self.get_parameter('confidence_threshold').value
        self.iou_threshold = self.get_parameter('iou_threshold').value
        image_topic = self.get_parameter('image_topic').value
        detection_topic = self.get_parameter('detection_topic').value
        lane_topic = self.get_parameter('lane_topic').value
        visualization_topic = self.get_parameter('visualization_topic').value
        device = self.get_parameter('device').value
        
        # Lane parameters
        self.roi_top = self.get_parameter('roi_top').value
        self.roi_bottom = self.get_parameter('roi_bottom').value
        self.canny_low = self.get_parameter('canny_low').value
        self.canny_high = self.get_parameter('canny_high').value
        self.hough_threshold = self.get_parameter('hough_threshold').value
        self.hough_min_line_length = self.get_parameter('hough_min_line_length').value
        self.hough_max_line_gap = self.get_parameter('hough_max_line_gap').value
        
        # Initialize CV Bridge
        self.bridge = CvBridge()
        
        # Load YOLO model
        if not ULTRALYTICS_AVAILABLE:
            self.get_logger().warn('Ultralytics not installed! Object detection disabled.')
            self.model = None
        else:
            try:
                self.get_logger().info(f'Loading YOLO model: {model_path}')
                self.model = YOLO(model_path)
                self.model.to(device)
                self.get_logger().info(f'YOLO model loaded successfully on {device}')
            except Exception as e:
                self.get_logger().error(f'Failed to load YOLO model: {e}')
                self.model = None
        
        # Create subscribers
        self.image_sub = self.create_subscription(
            Image,
            image_topic,
            self.image_callback,
            10
        )
        
        # Create publishers
        self.detection_pub = self.create_publisher(
            Detection2DArray,
            detection_topic,
            10
        )
        
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
        
        self.get_logger().info('YOLO + LaneNet Combined Detector Node initialized')
    
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
        if lines is not None:
            height, width = image.shape[:2]
            mid_x = width // 2
            
            left_lines = []
            right_lines = []
            
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
            
            # Draw left lane (green)
            for line in left_lines:
                x1, y1, x2, y2 = line
                cv2.line(image, (x1, y1), (x2, y2), (0, 255, 0), 3)
            
            # Draw right lane (blue)
            for line in right_lines:
                x1, y1, x2, y2 = line
                cv2.line(image, (x1, y1), (x2, y2), (255, 0, 0), 3)
        
        return image
    
    def image_callback(self, msg):
        """Process incoming image messages"""
        try:
            # Convert ROS Image to OpenCV
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            result_image = cv_image.copy()
            
            # Create header
            header = Header()
            header.stamp = self.get_clock().now().to_msg()
            header.frame_id = msg.header.frame_id
            
            # 1. YOLO Object Detection
            detection_array = Detection2DArray()
            detection_array.header = header
            
            if self.model is not None:
                try:
                    results = self.model(
                        cv_image,
                        conf=self.confidence_threshold,
                        iou=self.iou_threshold,
                        verbose=False
                    )
                    
                    # Process YOLO detections
                    for result in results:
                        for box in result.boxes:
                            detection = Detection2D()
                            
                            # Bounding box
                            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                            detection.bbox.center.position.x = float((x1 + x2) / 2)
                            detection.bbox.center.position.y = float((y1 + y2) / 2)
                            detection.bbox.size_x = float(x2 - x1)
                            detection.bbox.size_y = float(y2 - y1)
                            
                            # Class and confidence
                            hypothesis = ObjectHypothesisWithPose()
                            hypothesis.hypothesis.class_id = str(int(box.cls[0]))
                            hypothesis.hypothesis.score = float(box.conf[0])
                            detection.results.append(hypothesis)
                            
                            detection_array.detections.append(detection)
                    
                    # Draw YOLO detections
                    result_image = results[0].plot()
                except Exception as e:
                    self.get_logger().error(f'YOLO detection error: {e}')
            
            # Publish object detections
            self.detection_pub.publish(detection_array)
            
            # 2. Lane Detection
            lanes = self.detect_lanes(cv_image)
            
            # Create lane message
            lane_msg = Float32MultiArray()
            if lanes is not None:
                for line in lanes:
                    x1, y1, x2, y2 = line[0]
                    lane_msg.data.extend([float(x1), float(y1), float(x2), float(y2)])
            
            # Publish lane data
            self.lane_pub.publish(lane_msg)
            
            # Draw lanes on result image
            result_image = self.draw_lanes(result_image, lanes)
            
            # Add text overlay
            cv2.putText(result_image, f'Objects: {len(detection_array.detections)}', 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            if lanes is not None:
                cv2.putText(result_image, f'Lane Lines: {len(lanes)}', 
                           (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            # Publish visualization
            viz_msg = self.bridge.cv2_to_imgmsg(result_image, encoding='bgr8')
            viz_msg.header = header
            self.visualization_pub.publish(viz_msg)
            
        except Exception as e:
            self.get_logger().error(f'Error processing image: {e}')


def main(args=None):
    rclpy.init(args=args)
    
    node = YOLOLaneNetDetectorNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
