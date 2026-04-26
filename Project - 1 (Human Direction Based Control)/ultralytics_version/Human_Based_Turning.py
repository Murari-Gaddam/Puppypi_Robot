from ultralytics import YOLO
import cv2 as cv 
import rospy
import math
from std_srvs.srv import SetBool
from puppy_control.msg import Velocity, Pose, Gait

ROS_NODE_NAME = 'Human_Follower' 

model = YOLO("yolov8n.pt") 
vid = cv.VideoCapture(0)

PuppyMove = {'x': 5, 'y' : 0 , "Yaw_rate" : 0}
PuppyPose = {'roll':math.radians(0), 'pitch':math.radians(0), 'yaw':0.000, 'height':-10, 'x_shift':-0.6, 'stance_x':0, 'stance_y':0}
GaitConfig = {'overlap_time':0.2, 'swing_time':0.3, 'clearance_time':0.0, 'z_clearance':8} 
def Move():
    isTrue, frame = vid.read()
    if not isTrue:
        return

    results = model(frame)
    annotated_frame = results[0].plot()

    frame_center = frame.shape[1] // 2

    for box in results[0].boxes:
        cls = int(box.cls[0])

        if cls == 0:
            x1, y1, x2, y2 = box.xyxy[0]

            center_x = int((x1 + x2) / 2)
            offcentre = frame_center - center_x

            if offcentre > 100:
                PuppyMove["Yaw_rate"] = 0.002*offcentre
            elif offcentre < -100:
                PuppyMove["Yaw_rate"]= 0.002*offcentre
            else:
                PuppyMove['Yaw_rate'] = 0

            break 
def cleanup(): 
    PuppyVelocityPub.publish(x=0, y=0, yaw_rate=0) 
    print('is_shutdown')
    vid.release()
    cv.destroyAllWindows()

if __name__ == '__main__': 

    rospy.init_node(ROS_NODE_NAME, log_level=rospy.INFO) 
    rospy.on_shutdown(cleanup) 
    
    PuppyPosePub = rospy.Publisher('/puppy_control/pose', Pose, queue_size=1) 
    PuppyGaitConfigPub = rospy.Publisher('/puppy_control/gait', Gait, queue_size=1) 
    PuppyVelocityPub = rospy.Publisher('/puppy_control/velocity', Velocity, queue_size=1) 

    set_mark_time_srv = rospy.ServiceProxy('/puppy_control/set_mark_time', SetBool) 

    rospy.sleep(0.2) 
    PuppyPosePub.publish(stance_x=PuppyPose['stance_x'], stance_y=PuppyPose['stance_y'], x_shift=PuppyPose['x_shift'] 
            ,height=PuppyPose['height'], roll=PuppyPose['roll'], pitch=PuppyPose['pitch'], yaw=PuppyPose['yaw'], run_time = 500) #66
    
    rospy.sleep(0.2) 
    PuppyGaitConfigPub.publish(overlap_time = GaitConfig['overlap_time'], swing_time = GaitConfig['swing_time'] 
                    , clearance_time = GaitConfig['clearance_time'], z_clearance = GaitConfig['z_clearance']) 
    rospy.sleep(0.2)
    while not rospy.is_shutdown():
        Move()
        PuppyVelocityPub.publish(x=PuppyMove['x'], y=PuppyMove['y'], yaw_rate=PuppyMove['Yaw_rate']) 
        rospy.sleep(0.2) 
