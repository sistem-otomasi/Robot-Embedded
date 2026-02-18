#!/usr/bin/env python3
"""
Video File Selector - Simple UI for selecting video files
Provides both CLI and GUI interface for video file selection
"""

import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess


class VideoFileSelector:
    """Video file selector with GUI"""
    
    def __init__(self):
        self.selected_file = None
        self.root = tk.Tk()
        self.root.title("Video File Selector - ROS2 Detector")
        self.root.geometry("600x400")
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the UI components"""
        # Title
        title = tk.Label(
            self.root,
            text="YOLO & LaneNet Video Detector",
            font=("Arial", 16, "bold"),
            pady=20
        )
        title.pack()
        
        # File selection frame
        file_frame = tk.Frame(self.root, pady=10)
        file_frame.pack(fill=tk.X, padx=20)
        
        tk.Label(file_frame, text="Selected File:", font=("Arial", 10)).pack(anchor=tk.W)
        
        self.file_label = tk.Label(
            file_frame,
            text="No file selected",
            font=("Arial", 10),
            fg="gray",
            wraplength=550,
            justify=tk.LEFT
        )
        self.file_label.pack(anchor=tk.W, pady=5)
        
        # Browse button
        browse_btn = tk.Button(
            file_frame,
            text="Browse Video File (.mov, .mp4, .avi)",
            command=self.browse_file,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=10
        )
        browse_btn.pack(pady=10)
        
        # Detector selection
        detector_frame = tk.LabelFrame(self.root, text="Select Detector", font=("Arial", 11), pady=10, padx=10)
        detector_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.detector_var = tk.StringVar(value="yolo")
        
        tk.Radiobutton(
            detector_frame,
            text="YOLO Object Detection",
            variable=self.detector_var,
            value="yolo",
            font=("Arial", 10)
        ).pack(anchor=tk.W)
        
        tk.Radiobutton(
            detector_frame,
            text="LaneNet Lane Detection",
            variable=self.detector_var,
            value="lanenet",
            font=("Arial", 10)
        ).pack(anchor=tk.W)
        
        tk.Radiobutton(
            detector_frame,
            text="YOLO + LaneNet Combined",
            variable=self.detector_var,
            value="combined",
            font=("Arial", 10)
        ).pack(anchor=tk.W)
        
        # Action buttons
        button_frame = tk.Frame(self.root, pady=20)
        button_frame.pack()
        
        run_btn = tk.Button(
            button_frame,
            text="Run Detection",
            command=self.run_detection,
            bg="#2196F3",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=30,
            pady=10
        )
        run_btn.pack(side=tk.LEFT, padx=10)
        
        quit_btn = tk.Button(
            button_frame,
            text="Quit",
            command=self.root.quit,
            bg="#f44336",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=30,
            pady=10
        )
        quit_btn.pack(side=tk.LEFT, padx=10)
        
        # Status
        self.status_label = tk.Label(
            self.root,
            text="Ready",
            font=("Arial", 9),
            fg="blue"
        )
        self.status_label.pack(pady=10)
    
    def browse_file(self):
        """Open file browser to select video file"""
        filetypes = (
            ('Video files', '*.mov *.mp4 *.avi *.mkv'),
            ('MOV files', '*.mov'),
            ('MP4 files', '*.mp4'),
            ('AVI files', '*.avi'),
            ('All files', '*.*')
        )
        
        filename = filedialog.askopenfilename(
            title='Select a video file',
            initialdir=os.path.expanduser('~'),
            filetypes=filetypes
        )
        
        if filename:
            self.selected_file = filename
            self.file_label.config(text=filename, fg="black")
            self.status_label.config(text="Video file selected", fg="green")
    
    def run_detection(self):
        """Run the selected detector"""
        if not self.selected_file:
            messagebox.showerror("Error", "Please select a video file first!")
            return
        
        if not os.path.exists(self.selected_file):
            messagebox.showerror("Error", f"File not found: {self.selected_file}")
            return
        
        detector = self.detector_var.get()
        
        # Build ROS2 launch command
        if detector == "yolo":
            cmd = [
                "ros2", "launch", "yolo_detector", "yolo_detector.launch.py",
                f"image_topic:=/camera/image_raw"
            ]
            video_cmd = [
                "ros2", "run", "video_publisher", "video_publisher_node.py",
                f"--ros-args", "-p", f"video_file:={self.selected_file}"
            ]
        elif detector == "lanenet":
            cmd = [
                "ros2", "launch", "lanenet_detector", "lanenet_detector.launch.py",
                f"image_topic:=/camera/image_raw"
            ]
            video_cmd = [
                "ros2", "run", "video_publisher", "video_publisher_node.py",
                f"--ros-args", "-p", f"video_file:={self.selected_file}"
            ]
        elif detector == "combined":
            cmd = [
                "ros2", "launch", "yolo_lanenet_detector", "yolo_lanenet_detector.launch.py",
                f"image_topic:=/camera/image_raw"
            ]
            video_cmd = [
                "ros2", "run", "video_publisher", "video_publisher_node.py",
                f"--ros-args", "-p", f"video_file:={self.selected_file}"
            ]
        
        self.status_label.config(text=f"Starting {detector} detection...", fg="orange")
        
        # Show instructions
        instructions = f"""
Detection will start in a new terminal.

Commands to run manually:

Terminal 1 (Video Publisher):
{' '.join(video_cmd)}

Terminal 2 (Detector):
{' '.join(cmd)}

To view results:
ros2 run rqt_image_view rqt_image_view

Close this dialog to continue.
"""
        
        messagebox.showinfo("Launch Instructions", instructions)
        
        self.status_label.config(text="Ready to launch - Check terminal for commands", fg="blue")
    
    def run(self):
        """Run the GUI"""
        self.root.mainloop()


def main():
    """Main function"""
    print("=" * 60)
    print("Video File Selector for ROS2 YOLO & LaneNet Detector")
    print("=" * 60)
    
    # Check if running with GUI support
    try:
        app = VideoFileSelector()
        app.run()
    except Exception as e:
        print(f"\nGUI not available: {e}")
        print("\nFalling back to CLI mode...")
        
        # CLI mode
        print("\nEnter the path to your video file (.mov, .mp4, .avi):")
        video_file = input("Video file path: ").strip()
        
        if not os.path.exists(video_file):
            print(f"Error: File not found: {video_file}")
            sys.exit(1)
        
        print("\nSelect detector:")
        print("1. YOLO Object Detection")
        print("2. LaneNet Lane Detection")
        print("3. YOLO + LaneNet Combined")
        
        choice = input("Enter choice (1-3): ").strip()
        
        detector_map = {
            "1": "yolo_detector",
            "2": "lanenet_detector",
            "3": "yolo_lanenet_detector"
        }
        
        if choice not in detector_map:
            print("Invalid choice!")
            sys.exit(1)
        
        detector = detector_map[choice]
        
        print(f"\nStarting {detector} with video: {video_file}")
        print("\nRun these commands in separate terminals:")
        print(f"\nTerminal 1:")
        print(f"ros2 run video_publisher video_publisher_node.py --ros-args -p video_file:={video_file}")
        print(f"\nTerminal 2:")
        print(f"ros2 launch {detector} {detector}.launch.py")
        print(f"\nTerminal 3 (optional - to view results):")
        print(f"ros2 run rqt_image_view rqt_image_view")


if __name__ == '__main__':
    main()
