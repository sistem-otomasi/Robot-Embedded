#!/usr/bin/env python3
"""
YOLO Object Detection Node for ROS2 Humble
Detects objects in camera images using YOLOv8
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from vision_msgs.msg import Detection2D, Detection2DArray, ObjectHypothesisWithPose
from std_msgs.msg import Header
from cv_bridge import CvBridge
import cv2
import numpy as np

try:
    from ultralytics import YOLO
    ULTRALYTICS_AVAILABLE = True
except ImportError:
    ULTRALYTICS_AVAILABLE = False


class YOLODetectorNode(Node):
    """YOLO Object Detection Node"""
    
    def __init__(self):
        super().__init__('yolo_detector_node')
        
        # Declare parameters
        self.declare_parameter('model_path', 'yolov8n.pt')
        self.declare_parameter('confidence_threshold', 0.5)
        self.declare_parameter('iou_threshold', 0.45)
        self.declare_parameter('image_topic', '/camera/image_raw')
        self.declare_parameter('detection_topic', '/yolo/detections')
        self.declare_parameter('visualization_topic', '/yolo/image_detected')
        self.declare_parameter('device', 'cpu')
        
        # Get parameters
        model_path = self.get_parameter('model_path').value
        self.confidence_threshold = self.get_parameter('confidence_threshold').value
        self.iou_threshold = self.get_parameter('iou_threshold').value
        image_topic = self.get_parameter('image_topic').value
        detection_topic = self.get_parameter('detection_topic').value
        visualization_topic = self.get_parameter('visualization_topic').value
        device = self.get_parameter('device').value
        
        # Initialize CV Bridge
        self.bridge = CvBridge()
        
        # Load YOLO model
        if not ULTRALYTICS_AVAILABLE:
            self.get_logger().error('Ultralytics not installed! Install with: pip install ultralytics')
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
        
        self.visualization_pub = self.create_publisher(
            Image,
            visualization_topic,
            10
        )
        
        self.get_logger().info('YOLO Detector Node initialized')
    
    def image_callback(self, msg):
        """Process incoming image messages"""
        if self.model is None:
            return
        
        try:
            # Convert ROS Image to OpenCV
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            
            # Run YOLO detection
            results = self.model(
                cv_image,
                conf=self.confidence_threshold,
                iou=self.iou_threshold,
                verbose=False
            )
            
            # Create Detection2DArray message
            detection_array = Detection2DArray()
            detection_array.header = Header()
            detection_array.header.stamp = self.get_clock().now().to_msg()
            detection_array.header.frame_id = msg.header.frame_id
            
            # Process detections
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
            
            # Publish detections
            self.detection_pub.publish(detection_array)
            
            # Create visualization
            annotated_image = results[0].plot()
            
            # Publish visualization
            viz_msg = self.bridge.cv2_to_imgmsg(annotated_image, encoding='bgr8')
            viz_msg.header = detection_array.header
            self.visualization_pub.publish(viz_msg)
            
        except Exception as e:
            self.get_logger().error(f'Error processing image: {e}')


def main(args=None):
    rclpy.init(args=args)
    
    node = YOLODetectorNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
