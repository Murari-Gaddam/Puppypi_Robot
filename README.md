# PuppyPi AI Project Suite

A collection of AI and computer vision projects built on the Hiwonder PuppyPi quadruped robot,
running on Raspberry Pi with ROS Noetic. The goal is to progressively build an intelligent,
autonomous quadruped capable of perception, decision making, and interaction.

---

## Hardware
- Hiwonder PuppyPi Quadruped Robot
- Raspberry Pi (onboard)
- USB Camera
- 128GB Samsung EVO Plus microSD (planned upgrade from 32GB)

## Core Stack
- Python 3.8
- ROS Noetic
- Docker (Hiwonder container)
- OpenCV
- ONNX Runtime
- YOLOv8 (Ultralytics)
- cv_bridge

---

## Projects

### ✅ 1. Setup & Infrastructure
**Status: Complete**

Full development environment setup for remote development on the PuppyPi.

**What was done:**
- SSH, VNC, and VS Code Remote SSH access configured
- Docker container navigation and ROS environment setup
- College ethernet for downloads, hotspot for development sessions
- Filesystem expansion to 128GB planned

**Tech used:** SSH, Docker, ROS Noetic, VS Code Remote SSH

---

### 🔄 2. Human Follower
**Status: In Progress**

Real time human detection and autonomous following using YOLOv8 and ROS.

**How it works:**
- Subscribes to `/usb_cam/image_raw` ROS topic for camera feed
- YOLOv8n detects persons (COCO class 0) in each frame
- Calculates horizontal offset of person from frame center
- Publishes yaw rate correction to `/puppy_control/velocity`
- Robot turns to keep person centered while moving forward

**What's working:**
- ROS publishers and subscribers
- Robot locomotion
- YOLOv8n ONNX model deployed on Pi

**Pending:**
- ONNX Runtime inference pipeline
- Camera ROS topic integration
- End to end steering test

**Tech used:** Python, ROS Noetic, YOLOv8n ONNX, ONNX Runtime, OpenCV, cv_bridge

---

### 📅 3. OpenVINO Optimization
**Status: Planned — Q3 2026**

Optimize all inference pipelines using Intel OpenVINO for ARM deployment on Raspberry Pi.

**Goal:**
- Convert YOLOv8 ONNX models to OpenVINO IR format
- Achieve faster inference with lower CPU usage on Pi
- Benchmark latency improvements over raw ONNX Runtime

**Why:**
- Direct connection to GSoC OpenVINO application
- ARM optimization is a real bottleneck on Pi hardware
- Builds deep understanding of model optimization pipeline

**Tech needed:** OpenVINO, Model Optimizer, Python, ONNX, ARM benchmarking tools

---

### 📅 4. Voice Commanded Robot
**Status: Planned — Q3 2026**

Control the PuppyPi using natural language voice commands via a lightweight speech pipeline.

**Goal:**
- Wake word detection on Pi
- Speech to text using faster-whisper
- Command parsing and ROS action execution
- Commands like "follow me", "stop", "sit", "turn left"

**Why:**
- Connects PuppyPi project to personal AI assistant project
- Demonstrates multimodal AI on edge hardware
- Strong demo for research applications and GSoC proposals

**Tech needed:** faster-whisper, PyAudio, ROS, Python, lightweight LLM or rule based parser

---

### 📅 5. Obstacle Avoidance
**Status: Planned — Q4 2026**

Autonomous navigation with real time obstacle detection and avoidance.

**Goal:**
- Detect obstacles using camera based depth estimation or ultrasonic sensors
- Integrate avoidance logic with existing locomotion stack
- Combine with human follower for safe autonomous following

**Tech needed:** OpenCV, depth estimation models, ROS navigation stack, sensor integration

---

### 📅 6. Full Autonomous Agent
**Status: Long Term**

Combine all modules into a single autonomous agent that can perceive, decide, and act.

**Goal:**
- Human following with obstacle avoidance
- Voice command override
- OpenVINO optimized inference for all vision tasks
- Logging and telemetry via ROS

**Tech needed:** Full stack — ROS, OpenVINO, faster-whisper, YOLOv8, Python, possibly ROS2 migration

---

## Setup Guide
```bash
# SSH into Pi
ssh pi@<IP>

# Enter Docker container
docker exec -it -u ubuntu -w /home/ubuntu puppypi /bin/zsh

# Source ROS
source /opt/ros/noetic/setup.bash
source /home/ubuntu/puppypi/devel/setup.bash
```

## Known Infrastructure Issues
- Docker container storage at 97% capacity — 128GB SD card upgrade planned
- Python version mismatch between Pi host (3.11) and Docker container (3.8)
- Camera `/dev/video0` claimed by ROS `usb_cam` node — must use ROS topic instead of direct capture
- Ultralytics not installable inside Docker due to storage constraints — using ONNX Runtime as workaround

## Roadmap
| Project | Target | Status |
|---------|--------|--------|
| Setup & Infrastructure | April 2026 | ✅ Done |
| Human Follower | May 2026 | 🔄 In Progress |
| OpenVINO Optimization | Q3 2026 | 📅 Planned |
| Voice Commanded Robot | Q3 2026 | 📅 Planned |
| Obstacle Avoidance | Q4 2026 | 📅 Planned |
| Full Autonomous Agent | 2027 | 📅 Long Term |

## Why This Project
Building real AI systems on constrained hardware teaches what production ML actually looks like —
storage limits, Python version conflicts, Docker networking, ROS integration, and ARM optimization.
These are the exact problems that matter in robotics and edge AI, and exactly what OpenVINO GSoC
is about.
