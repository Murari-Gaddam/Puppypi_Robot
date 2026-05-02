# PuppyPi Human Follower — ONNX Version

Autonomous human following system for the Hiwonder PuppyPi quadruped robot (Raspberry Pi 5, 8GB RAM).
Detects a person in the camera frame using YOLOv8n ONNX and adjusts the robot's yaw rate to follow them autonomously using ROS Noetic.

## Demo
> Robot walking and turning to follow a detected person in real time.
> *(Video coming soon)*

## How It Works
ROS usb_cam node → /usb_cam/image_raw topic
↓
cv_bridge converts ROS Image → OpenCV numpy array
↓
Preprocess: resize 640x640, BGR→RGB, normalize, NCHW transpose
↓
YOLOv8n ONNX Runtime inference
↓
Parse output [8400, 84] → filter person class (confidence > 0.5)
↓
Calculate horizontal offset from frame center
↓
Publish yaw rate correction to /puppy_control/velocity
↓
Robot turns to keep person centered in frame

## Hardware
- Hiwonder PuppyPi Quadruped Robot
- Raspberry Pi 5 (8GB RAM)
- USB Camera
- 32GB microSD (128GB upgrade planned)

## Stack
- Python 3.8
- ROS Noetic
- ONNX Runtime 1.19.2
- OpenCV 4.13 (headless)
- cv_bridge
- YOLOv8n (ONNX format)
- NumPy

## Robot Parameters
```python
PuppyMove = {'x': 5, 'y': 0, 'Yaw_rate': 0}

PuppyPose = {
    'roll': 0, 'pitch': 0, 'yaw': 0,
    'height': -10, 'x_shift': -0.65,
    'stance_x': 0, 'stance_y': 0
}

GaitConfig = {
    'overlap_time': 0.1,
    'swing_time': 0.2,
    'clearance_time': 0.3,
    'z_clearance': 5
}
```

## ROS Topics
| Topic | Type | Description |
|-------|------|-------------|
| `/usb_cam/image_raw` | sensor_msgs/Image | Camera input |
| `/puppy_control/velocity` | Velocity | Controls x, y, yaw_rate |
| `/puppy_control/pose` | Pose | Controls robot stance and height |
| `/puppy_control/gait` | Gait | Controls gait timing |

## Setup

### Enter Docker Container
```bash
docker exec -it -u ubuntu -w /home/ubuntu puppypi /bin/zsh
```

### Source ROS
```bash
source /opt/ros/noetic/setup.bash
source /home/ubuntu/puppypi/devel/setup.bash
```

### Verify Camera
```bash
rostopic hz /usb_cam/image_raw
```
Should show ~12.5hz

### Run
```bash
cd /home/ubuntu/puppypi/src/puppy_control/scripts/
python3 human.py
```

## Inference Pipeline — run_inference()

YOLOv8n ONNX output shape is `[1, 84, 8400]`:
- 8400 candidate anchor boxes
- 84 values = 4 box coordinates (cx, cy, w, h) + 80 COCO class scores
- Class 0 = person

Preprocessing steps:
1. Resize frame to 640x640 (model input size)
2. BGR → RGB conversion
3. Normalize to 0-1 float32
4. Transpose HWC → NCHW
5. Add batch dimension → shape (1, 3, 640, 640)

Post-processing:
1. Transpose output [84, 8400] → [8400, 84]
2. Extract person scores (column 0)
3. Filter by confidence threshold (0.5)
4. Pick highest confidence detection
5. Scale center_x back to original frame width

## Known Issues & Limitations
- Occasional false positives causing random direction changes — confidence threshold tuning in progress
- Slight body tilt during movement — gait parameter refinement needed
- Storage constraint: Docker container at 97% capacity — ultralytics not installable, using ONNX Runtime as workaround
- opencv-python-headless installed — cv2.imshow not available, display via VNC only

## Current Status
- [x] SSH, VNC, VS Code Remote SSH setup
- [x] Docker navigation and ROS environment
- [x] Camera ROS topic integration (12.5hz)
- [x] ONNX Runtime inference pipeline
- [x] Human detection working
- [x] Robot turning to follow person
- [ ] Movement smoothing and stability refinement
- [ ] Confidence threshold optimization
- [ ] False positive filtering

## Pending Improvements
### Movement Refinement
- Smooth yaw rate transitions to eliminate jerky movement
- Detection cooldown — require consecutive frames before acting
- Dynamic yaw rate scaling based on offset magnitude
- Stop forward movement when person lost from frame

### Stability
- Gait parameter tuning for smoother walking
- Body stabilization during turns
- Battery level monitoring

## Future Expansions

### OpenVINO Optimization
Convert YOLOv8n from ONNX to OpenVINO IR format for faster ARM inference on Raspberry Pi 5:
```python
from openvino.tools import mo
mo.convert_model("yolov8n.onnx", output_model="yolov8n_openvino")
```
Expected improvement: 2-3x faster inference, lower CPU usage, enabling higher camera frame rates.
This directly connects to GSoC OpenVINO contribution goals.

### Voice Control Integration
Connect to personal AI assistant project for voice commanded robot control:
- "Follow me" → activate human follower mode
- "Stop" → halt all movement
- "Sit" → pose command via /puppy_control/pose
- "Turn left/right" → manual yaw control

### Obstacle Avoidance
Add depth estimation or ultrasonic sensor integration to avoid obstacles while following.

### Multi-Person Tracking
Track specific person by appearance rather than just nearest/highest confidence detection.

### Storage Upgrade
128GB Samsung EVO Plus microSD card swap planned — will enable full ultralytics install and remove ONNX workaround.

## Why ONNX Instead of Ultralytics
Ultralytics requires ~2GB storage for torch dependencies. Docker container had only 948MB free on 32GB microSD. Solution: export YOLOv8n to ONNX on host machine, deploy lightweight ONNX Runtime inside container.

```bash
# On host machine with ultralytics
python3 -c "from ultralytics import YOLO; YOLO('yolov8n.pt').export(format='onnx')"

# Copy to Pi then into Docker
scp yolov8n.onnx ubuntu@<PI_IP>:/home/ubuntu/
sudo docker cp /home/ubuntu/yolov8n.onnx 82df:/home/ubuntu/puppypi/src/puppy_control/scripts/
```

## Part of PuppyPi AI Project Suite
This is Project 2 in a larger series of AI projects on the PuppyPi platform.
See the [main repository README](../README.md) for the full roadmap.
