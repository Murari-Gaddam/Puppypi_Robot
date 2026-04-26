
# PuppyPi Human Follower

A computer vision based human following system built on the Hiwonder PuppyPi quadruped robot.
Uses YOLOv8 for real-time human detection integrated with ROS Noetic for autonomous robot control.

## Overview
The system detects a person in the camera frame, calculates their horizontal offset from center,
and adjusts the robot's yaw rate to follow them autonomously while maintaining forward movement.

## How It Works
1. Camera captures live feed via `cv2.VideoCapture`
2. YOLOv8n detects persons (COCO class 0) in each frame
3. Calculates horizontal offset of detected person from frame center
4. Publishes yaw rate correction to `/puppy_control/velocity`
5. Robot turns left or right to keep the person centered in frame

## Hardware
- Hiwonder PuppyPi Quadruped Robot
- Raspberry Pi (onboard)
- USB Camera

## Stack
- Python 3.8
- ROS Noetic
- Ultralytics YOLOv8n
- OpenCV
- cv_bridge

## Robot Parameters
```python
# Movement
PuppyMove = {'x': 5, 'y': 0, 'Yaw_rate': 0}

# Pose
PuppyPose = {
    'roll': 0, 'pitch': 0, 'yaw': 0,
    'height': -10, 'x_shift': -0.6,
    'stance_x': 0, 'stance_y': 0
}

# Gait
GaitConfig = {
    'overlap_time': 0.2, 'swing_time': 0.3,
    'clearance_time': 0.0, 'z_clearance': 8
}
```

## ROS Topics
| Topic | Type | Description |
|-------|------|-------------|
| `/puppy_control/velocity` | Velocity | Controls x, y, yaw_rate |
| `/puppy_control/pose` | Pose | Controls robot stance and height |
| `/puppy_control/gait` | Gait | Controls gait timing parameters |

## Setup
### Prerequisites
- Hiwonder PuppyPi with ROS Noetic Docker container
- Ultralytics installed inside container
- OpenCV installed inside container

### Network Access
```bash
# SSH into Pi
ssh pi@<IP>

# Enter Docker container
docker exec -it -u ubuntu -w /home/ubuntu puppypi /bin/zsh

# Source ROS environment
source /opt/ros/noetic/setup.bash
source /home/ubuntu/puppypi/devel/setup.bash
```

### Run
```bash
cd /home/ubuntu/puppypi/src/puppy_control/scripts/
python3 cool.py
```

## Compatibility Issues

### Current Environment (Docker Container — Python 3.8)
| Package | Version | Status |
|---------|---------|--------|
| ultralytics | latest | ❌ Not installable — insufficient storage |
| onnxruntime | 1.19.2 | ✅ Installed as workaround |
| opencv-python-headless | 4.13.0 | ✅ Working |
| numpy | 1.24.4 | ✅ Working |

### Known Issues
- **Ultralytics not installable inside Docker** — container storage at 97% capacity (948MB free),
  full ultralytics install requires ~2GB with torch dependencies
- **Python version mismatch** — Pi host runs Python 3.11, Docker runs Python 3.8.
  Packages installed outside Docker are not visible inside container
- **Camera access** — `/dev/video0` is claimed by ROS `usb_cam` node.
  Direct `cv2.VideoCapture(0)` fails inside Docker. Must subscribe to `/usb_cam/image_raw` topic instead
- **Ultralytics API incompatible with onnxruntime** — `model(frame)` call does not work with
  `onnxruntime.InferenceSession`. Raw numpy preprocessing pipeline required — fix in progress

### Workaround Applied
YOLOv8n exported to ONNX on host machine and copied into container:
```bash
# On host machine with ultralytics installed
python3 -c "from ultralytics import YOLO; YOLO('yolov8n.pt').export(format='onnx')"

# Copy to Pi
scp yolov8n.onnx ubuntu@<PI_IP>:/home/ubuntu/

# Copy into Docker container
sudo docker cp /home/ubuntu/yolov8n.onnx 82df:/home/ubuntu/puppypi/src/puppy_control/scripts/
```

## Known Bug
```python
# Wrong — when offcentre is negative, multiplying by -0.002 makes yaw_rate positive (wrong direction)
elif offcentre < -100:
    PuppyMove["Yaw_rate"] = -0.002 * offcentre

# Fix — same formula for both cases, sign of offcentre handles direction
PuppyMove["Yaw_rate"] = 0.002 * offcentre
```

## Status
- [x] SSH, VNC, VS Code Remote SSH setup
- [x] Docker navigation
- [x] ROS publishers working
- [x] Robot locomotion working
- [x] YOLOv8n ONNX model deployed on Pi
- [ ] Camera ROS topic integration
- [ ] ONNX Runtime inference pipeline
- [ ] Human detection and steering end to end

## Next Steps
- Fix ONNX inference pipeline or find storage solution for full ultralytics install
- Switch camera input from `VideoCapture` to `/usb_cam/image_raw` ROS topic
- Expand filesystem to 128GB microSD for storage headroom
- Integrate OpenVINO for ARM optimization on Raspberry Pi
