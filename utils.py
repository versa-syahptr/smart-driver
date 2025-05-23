from typing import List, Tuple
from enum import Enum
import numpy as np
from dataclasses import dataclass, field
import cv2

chosen_left_eye_idxs  = [362, 385, 387, 263, 373, 380]
chosen_right_eye_idxs = [33,  160, 158, 133, 153, 144]

class ChoosenIndices:
    LEFT_EYE = [362, 385, 387, 263, 373, 380]
    RIGHT_EYE = [33,  160, 158, 133, 153, 144]
    MOUTH = [61, 37, 267, 291, 314, 84]
    POSE = [1, 33, 61, 199, 263, 291]
    ALL = LEFT_EYE + RIGHT_EYE + MOUTH


@dataclass
class ChoosenLandmarks:
    right_eye: List = field(default_factory=list)
    left_eye: List = field(default_factory=list)
    mouth: List = field(default_factory=list)
    pose2d: List = field(default_factory=list)
    pose3d: List = field(default_factory=list)

    @property
    def isFull(self):
        return len(self.right_eye) == 6 and len(self.left_eye) == 6 and len(self.mouth) == 6


class Color(Enum):
    RED = (0, 0, 255)
    GREEN = (0, 255, 0)

def distance(point_1, point_2):
    """Calculate l2-norm between two points"""
    dist = sum([(i - j) ** 2 for i, j in zip(point_1, point_2)]) ** 0.5
    return dist

def calculate_EAR(landmarks: ChoosenLandmarks):
    ear = 0.0
    for coords_points in (landmarks.left_eye, landmarks.right_eye):
        try:
            P2_P6 = distance(coords_points[1], coords_points[5])
            P3_P5 = distance(coords_points[2], coords_points[4])
            P1_P4 = distance(coords_points[0], coords_points[3])

            # Compute the eye aspect ratio
            ear += (P2_P6 + P3_P5) / (2.0 * P1_P4)
        except Exception:
            ear = 0.0
    return ear/2.0

def calculate_MAR(landmarks: ChoosenLandmarks):
    mar = 0.0
    try:
        P2_P6 = distance(landmarks.mouth[1], landmarks.mouth[5])
        P3_P5 = distance(landmarks.mouth[2], landmarks.mouth[4])
        P1_P4 = distance(landmarks.mouth[0], landmarks.mouth[3])

        # Compute the mouth aspect ratio
        mar += (P2_P6 + P3_P5) / (2.0 * P1_P4)
    except Exception as e:
        mar = 0.0
    return mar


def face_gradient(landmarks):
    a = landmarks[10]
    b = landmarks[152]
    # calculate gradient of the line in y and z axis
    y_grad = (b.y - a.y) / (b.z - a.z)
    return y_grad


def head_pose_rotation(landmarks: ChoosenLandmarks, w, h): 
        # Convert it to the NumPy array
        face_2d = np.array(landmarks.pose2d, dtype=np.float64)

        # Convert it to the NumPy array
        face_3d = np.array(landmarks.pose3d, dtype=np.float64)

        # The camera matrix
        focal_length = 1 * w

        cam_matrix = np.array([ [focal_length, 0, h / 2],
                                [0, focal_length, w / 2],
                                [0, 0, 1]])

        # The distortion parameters
        dist_matrix = np.zeros((4, 1), dtype=np.float64)

        # Solve PnP
        success, rot_vec, trans_vec = cv2.solvePnP(face_3d, face_2d, cam_matrix, dist_matrix)

        # Get rotational matrix
        rmat, jac = cv2.Rodrigues(rot_vec)

        # Get angles
        angles, mtxR, mtxQ, Qx, Qy, Qz = cv2.RQDecomp3x3(rmat)

        # Get the y rotation degree
        x = angles[0] * 360
        y = angles[1] * 360
        z = angles[2] * 360

        return x,y,z