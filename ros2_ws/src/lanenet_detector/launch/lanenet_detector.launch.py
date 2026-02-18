from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    """Generate launch description for LaneNet detector"""
    
    # Declare launch arguments
    image_topic_arg = DeclareLaunchArgument(
        'image_topic',
        default_value='/camera/image_raw',
        description='Input image topic'
    )
    
    roi_top_arg = DeclareLaunchArgument(
        'roi_top',
        default_value='0.5',
        description='ROI top percentage (0.0-1.0)'
    )
    
    # Create LaneNet detector node
    lanenet_node = Node(
        package='lanenet_detector',
        executable='lanenet_detector_node.py',
        name='lanenet_detector_node',
        output='screen',
        parameters=[{
            'image_topic': LaunchConfiguration('image_topic'),
            'roi_top': LaunchConfiguration('roi_top'),
        }]
    )
    
    return LaunchDescription([
        image_topic_arg,
        roi_top_arg,
        lanenet_node
    ])
