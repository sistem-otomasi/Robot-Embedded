from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    """Generate launch description for combined YOLO + LaneNet detector"""
    
    # Declare launch arguments
    yolo_model_arg = DeclareLaunchArgument(
        'yolo_model_path',
        default_value='yolov8n.pt',
        description='Path to YOLO model file'
    )
    
    confidence_arg = DeclareLaunchArgument(
        'confidence_threshold',
        default_value='0.5',
        description='Confidence threshold for YOLO detections'
    )
    
    image_topic_arg = DeclareLaunchArgument(
        'image_topic',
        default_value='/camera/image_raw',
        description='Input image topic'
    )
    
    device_arg = DeclareLaunchArgument(
        'device',
        default_value='cpu',
        description='Device to run YOLO inference on (cpu or cuda)'
    )
    
    # Create combined detector node
    combined_node = Node(
        package='yolo_lanenet_detector',
        executable='yolo_lanenet_detector_node.py',
        name='yolo_lanenet_detector_node',
        output='screen',
        parameters=[{
            'yolo_model_path': LaunchConfiguration('yolo_model_path'),
            'confidence_threshold': LaunchConfiguration('confidence_threshold'),
            'image_topic': LaunchConfiguration('image_topic'),
            'device': LaunchConfiguration('device'),
        }]
    )
    
    return LaunchDescription([
        yolo_model_arg,
        confidence_arg,
        image_topic_arg,
        device_arg,
        combined_node
    ])
