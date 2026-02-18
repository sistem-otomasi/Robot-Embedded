from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    """Generate launch description for video publisher"""
    
    # Declare launch arguments
    video_file_arg = DeclareLaunchArgument(
        'video_file',
        default_value='',
        description='Path to video file (.mov, .mp4, .avi)'
    )
    
    output_topic_arg = DeclareLaunchArgument(
        'output_topic',
        default_value='/camera/image_raw',
        description='Output image topic'
    )
    
    frame_rate_arg = DeclareLaunchArgument(
        'frame_rate',
        default_value='30.0',
        description='Frame rate for publishing'
    )
    
    loop_arg = DeclareLaunchArgument(
        'loop',
        default_value='true',
        description='Loop video playback'
    )
    
    # Create video publisher node
    video_node = Node(
        package='video_publisher',
        executable='video_publisher_node.py',
        name='video_publisher_node',
        output='screen',
        parameters=[{
            'video_file': LaunchConfiguration('video_file'),
            'output_topic': LaunchConfiguration('output_topic'),
            'frame_rate': LaunchConfiguration('frame_rate'),
            'loop': LaunchConfiguration('loop'),
        }]
    )
    
    return LaunchDescription([
        video_file_arg,
        output_topic_arg,
        frame_rate_arg,
        loop_arg,
        video_node
    ])
