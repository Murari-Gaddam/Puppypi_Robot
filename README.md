# PuppyPi Human Follower

A computer vision based human following system built on the Hiwonder PuppyPi quadruped robot.

## Overview
Uses YOLOv8 (ONNX) for real-time human detection integrated with ROS Noetic for autonomous robot control. The system detects a person in the camera frame, calculates their offset from center, and adjusts the robot's yaw rate to follow them.

## Hardware
- Hiwonder PuppyPi Quadruped Robot
- Raspberry Pi (onboard)
- USB Camera

## Stack
- Python 3.8
- ROS Noetic
- YOLOv8n (ONNX format)
- ONNX Runtime
- OpenCV
- cv_bridge

## How It Works
1. ROS `usb_cam` node captures camera feed and publishes to `/usb_cam/image_raw`
2. YOLOv8n detects persons (class 0) in each frame
3. Calculates horizontal offset of detected person from frame center
4. Publishes yaw rate correction to `/puppy_control/velocity`
5. Robot turns to keep the person centered in frame

## Setup
### Prerequisites
- Hiwonder PuppyPi with ROS Noetic Docker container
- ONNX Runtime installed inside container
- OpenCV installed inside container

### Network Access
```bash
