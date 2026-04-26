# Human Follower

Autonomous human following system for the PuppyPi quadruped robot.
Detects a person in the camera frame and adjusts the robot's yaw rate to keep them centered.

## Versions

### v1 — Ultralytics + OpenCV (`/ultralytics_version`)
Uses Ultralytics YOLOv8n API with direct camera capture via OpenCV.
Simple and clean but requires full ultralytics install — not compatible with current Docker storage constraints.

### v2 — ONNX Runtime + ROS Camera (`/onnx_version`)
Uses ONNX Runtime for inference and subscribes to `/usb_cam/image_raw` ROS topic instead of direct camera access.
Built to work within Docker container limitations on the Pi.
**Status: In progress — ONNX inference pipeline pending**

## How It Works
1. Camera feed captured (OpenCV or ROS topic)
2. YOLOv8n detects persons (COCO class 0)
3. Horizontal offset calculated from frame center
4. Yaw rate published to `/puppy_control/velocity`
5. Robot turns to follow

## See Individual READMEs
- [`/ultralytics_version/README.md`](./ultralytics_version/README.md)
- [`/onnx_version/README.md`](./onnx_version/README.md)
