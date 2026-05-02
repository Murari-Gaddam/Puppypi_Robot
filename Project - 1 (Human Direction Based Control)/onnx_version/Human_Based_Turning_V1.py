import onnxruntime as ort
import numpy as np
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import rospy
import math
from std_srvs.srv import SetBool
from puppy_control.msg import Velocity, Pose, Gait
import cv2

ROS_NODE_NAME = 'Human_Follower' 
model = ort.InferenceSession("yolov8n.onnx")
bridge = CvBridge()
latest_frame = None

def image_callback(msg):
    global latest_frame
    latest_frame = bridge.imgmsg_to_cv2(msg, "bgr8")

def run_inference(frame):
    img = cv2.resize(frame, (640, 640))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img.astype(np.float32) / 255.0
    img = np.transpose(img, (2, 0, 1))
    img = np.expand_dims(img, axis=0)
    
    outputs = model.run(None, {model.get_inputs()[0].name: img})
    predictions = outputs[0][0]
    predictions = predictions.T
    
    boxes = predictions[:, :4]
    scores = predictions[:, 4:]
    person_scores = scores[:, 0]
    mask = person_scores > 0.5
    person_boxes = boxes[mask]
    
    if len(person_boxes) == 0:
        return None
    
    best_idx = person_scores[mask].argmax()
    cx, cy, w, h = person_boxes[best_idx]
    
    orig_w = frame.shape[1]
    cx = int(cx * orig_w / 640)
    return cx
PuppyMove = {'x': 5, 'y' : 0 , "Yaw_rate" : 0}
PuppyPose = {'roll':math.radians(0), 'pitch':math.radians(0), 'yaw':0.000, 'height':-10, 'x_shift':-0.65, 'stance_x':0, 'stance_y':0}
GaitConfig = {'overlap_time':0.1, 'swing_time':0.2, 'clearance_time':0.3, 'z_clearance':5} 
def Move():
    global latest_frame
    if latest_frame is None:
        return
    frame = latest_frame.copy()
    frame_center = frame.shape[1] // 2
    center_x = run_inference(frame)
    if center_x is None:
        PuppyMove['Yaw_rate'] = 0
        return
    offcentre = frame_center - center_x
    PuppyMove['Yaw_rate'] = 0.001 * offcentre

def cleanup(): 
    PuppyVelocityPub.publish(x=0, y=0, yaw_rate=0) 
    print('is_shutdown')

if __name__ == '__main__': 
    rospy.init_node(ROS_NODE_NAME, log_level=rospy.INFO) 
    rospy.on_shutdown(cleanup) 
    
    PuppyPosePub = rospy.Publisher('/puppy_control/pose', Pose, queue_size=1) 
    PuppyGaitConfigPub = rospy.Publisher('/puppy_control/gait', Gait, queue_size=1) 
    PuppyVelocityPub = rospy.Publisher('/puppy_control/velocity', Velocity, queue_size=1) 

    set_mark_time_srv = rospy.ServiceProxy('/puppy_control/set_mark_time', SetBool) 

    rospy.sleep(0.2) 
    PuppyPosePub.publish(stance_x=PuppyPose['stance_x'], stance_y=PuppyPose['stance_y'], x_shift=PuppyPose['x_shift'] 
            ,height=PuppyPose['height'], roll=PuppyPose['roll'], pitch=PuppyPose['pitch'], yaw=PuppyPose['yaw'], run_time = 500)
    
    rospy.sleep(0.2) 
    PuppyGaitConfigPub.publish(overlap_time = GaitConfig['overlap_time'], swing_time = GaitConfig['swing_time'] 
                    , clearance_time = GaitConfig['clearance_time'], z_clearance = GaitConfig['z_clearance']) 
    rospy.sleep(0.2)
    rospy.Subscriber('/usb_cam/image_raw', Image, image_callback)
    while not rospy.is_shutdown():
        Move()
        PuppyVelocityPub.publish(x=PuppyMove['x'], y=PuppyMove['y'], yaw_rate=PuppyMove['Yaw_rate']) 
        rospy.sleep(0.2) 

