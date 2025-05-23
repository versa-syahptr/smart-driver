import cv2
from arduino import AccidentDetector
from landmarker import FaceLandmarker
from tracker import Tracker
from utils import calculate_EAR, calculate_MAR, head_pose_rotation, Color, ChoosenIndices


class SDP:
    def __init__(self, source) -> None:
        self.cap = cv2.VideoCapture(source)
        self.fld = FaceLandmarker()
        self.tracker = Tracker()
        self.notifier = AccidentDetector("COM4")
    
    def run(self, fullscreen=True):
        while self.cap.isOpened():
            success, image = self.cap.read()
            if not success:
                print("Failed to read frame")
                break
            image = cv2.flip(image, 1)
            self.fld.detect(image)
            if self.fld.last_result:
                h, w, c = image.shape
                choosen_landmarks = self.fld.get_chosen_landmarks(w, h)
                if choosen_landmarks.isFull:
                    ear = calculate_EAR(choosen_landmarks)
                    image = self.fld.draw_chosen_landmarks(image, Color.GREEN)
                    cv2.putText(image, f"EAR: {ear:.3f}", (10, 30), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    mar = calculate_MAR(choosen_landmarks)
                    cv2.putText(image, f"MAR: {mar:.3f}", (10, 60), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    
                    # calculate face angle
                    x, y, z = head_pose_rotation(choosen_landmarks, w, h)
                    cv2.putText(image, f"X: {x:.3f}", (10, 150), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    cv2.putText(image, f"Y: {y:.3f}", (10, 180),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    cv2.putText(image, f"Z: {z:.3f}", (10, 210),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    if y < -10:
                        text = "Looking Left"
                    elif y > 10:
                        text = "Looking Right"
                    elif x < -5:
                        text = "Looking Down"
                    elif x > 10:
                        text = "Looking Up"
                    else:
                        text = "Forward"
                    
                    p1 = tuple(choosen_landmarks.pose2d[0])
                    p2 = (int(p1[0] + y * 10) , int(p1[1] - x * 10))  
                    cv2.line(image, p2, p1, (255, 0, 0), 3)
                    cv2.circle(image, p1, 2, (0, 255, 0), -1)

                    
                    cv2.putText(image, text, (10, 240),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                    self.tracker.update(ear, mar, x, cb_args=(image, ))
                    self.notifier.get_update()

            if fullscreen:
            # set fullscreen window
                cv2.namedWindow("Face Landmarker", cv2.WINDOW_NORMAL)
                cv2.setWindowProperty("Face Landmarker", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            cv2.imshow("Face Landmarker", image)
            # wait for esc or ctrl+q to exit
            if cv2.waitKey(1) & 0xFF == 27 or cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()