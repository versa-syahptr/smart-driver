import cv2
import time
import numpy as np
import mediapipe as mp

from typing import Callable, Optional

from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.framework.formats import landmark_pb2

from utils import Color, ChoosenLandmarks, ChoosenIndices

mp_drawing = mp.solutions.drawing_utils
mp_face_mesh = mp.solutions.face_mesh
denormalize_coordinates = mp_drawing._normalized_to_pixel_coordinates


class FaceLandmarker:
    def __init__(self, model: str = "face_landmarker.task", num_faces: int = 1, 
                 run_mode: vision.RunningMode = vision.RunningMode.LIVE_STREAM,
                 min_face_detection_confidence: float = 0.5,
                 min_face_presence_confidence: float = 0.5,
                 min_tracking_confidence: float = 0.5) -> None:
        base_options = python.BaseOptions(model_asset_path=model)
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            running_mode=run_mode,
            num_faces=num_faces,
            min_face_detection_confidence=min_face_detection_confidence,
            min_face_presence_confidence=min_face_presence_confidence,
            min_tracking_confidence=min_tracking_confidence,
            output_face_blendshapes=True,
            result_callback=self._save_callback)
        self.detector = vision.FaceLandmarker.create_from_options(options)
        self._save_callback_fn: Optional[Callable] = None
        self.last_result: vision.FaceLandmarkerResult = None

    def _save_callback(self, result: vision.FaceLandmarkerResult,
                    unused_output_image: mp.Image, timestamp_ms: int):
        self.last_result = result
        if self._save_callback_fn is not None:
            self._save_callback_fn(result, unused_output_image, timestamp_ms)
    
    # set save callback decorator
    def set_save_callback(self, fn: Optional[Callable]):
        self._save_callback_fn = fn
    
    def detect(self, image: np.ndarray, flip=False):
        if flip:
            image = cv2.flip(image, 1)

        # Convert the image from BGR to RGB as required by the TFLite model.
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)

        # Run face landmarker using the model.
        self.detector.detect_async(mp_image, time.time_ns() // 1_000_000)
    
    def draw_default_landmarks(self, image: np.ndarray) -> np.ndarray:
        if self.last_result is None:
            print("No result")
            return
        # annotated_image = cv2.flip(image, 1)
        annotated_image = image.copy()
        for face_landmarks in self.last_result.face_landmarks:
            face_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
            face_landmarks_proto.landmark.extend([
                landmark_pb2.NormalizedLandmark(x=landmark.x, # type: ignore
                                                y=landmark.y,
                                                z=landmark.z) for
                landmark in face_landmarks
            ])
            mp_drawing.draw_landmarks(
                image=annotated_image,
                landmark_list=face_landmarks_proto,
                connections=mp_face_mesh.FACEMESH_TESSELATION,
                landmark_drawing_spec=None,
                connection_drawing_spec=mp.solutions.drawing_styles
                .get_default_face_mesh_tesselation_style())
            mp_drawing.draw_landmarks(
                image=annotated_image,
                landmark_list=face_landmarks_proto,
                connections=mp_face_mesh.FACEMESH_CONTOURS,
                landmark_drawing_spec=None,
                connection_drawing_spec=mp.solutions.drawing_styles
                .get_default_face_mesh_contours_style())
            mp_drawing.draw_landmarks(
                image=annotated_image,
                landmark_list=face_landmarks_proto,
                connections=mp_face_mesh.FACEMESH_IRISES,
                landmark_drawing_spec=None,
                connection_drawing_spec=mp.solutions.drawing_styles
                .get_default_face_mesh_iris_connections_style())

        return annotated_image
    
    def get_chosen_landmarks(self, w, h) -> ChoosenLandmarks:
        if self.last_result is None:
            return
        
        chosen_landmarks = ChoosenLandmarks()

        for face_landmarks in self.last_result.face_landmarks:
            for idx in ChoosenIndices.ALL:
            # for idx in all_chosen_idxs+mouth_idx:
                # denormalize landmarks
                lm = face_landmarks[idx]
                denom = [int(lm.x * w), int(lm.y * h)]
                if idx in ChoosenIndices.LEFT_EYE:
                # if idx in chosen_left_eye_idxs:
                    chosen_landmarks.left_eye.append(denom)
                elif idx in ChoosenIndices.RIGHT_EYE:
                # if idx in chosen_right_eye_idxs:
                    chosen_landmarks.right_eye.append(denom)
                elif idx in ChoosenIndices.MOUTH:
                # if idx in mouth_idx:
                    chosen_landmarks.mouth.append(denom)
                # chosen_landmarks.append(denom)
            for idx in ChoosenIndices.POSE:
                lm = face_landmarks[idx]
                denom = [int(lm.x * w), int(lm.y * h)]
                chosen_landmarks.pose2d.append(denom)
                chosen_landmarks.pose3d.append([denom[0], denom[1], lm.z])
        return chosen_landmarks
    
    def draw_chosen_landmarks(self, image: np.ndarray, color: Color) -> np.ndarray:
        if self.last_result is None:
            return
        # annotated_image = cv2.flip(image, 1)
        annotated_image = image.copy()
        for face_landmarks in self.last_result.face_landmarks:
            for idx in set(ChoosenIndices.ALL + ChoosenIndices.POSE):
                landmark = face_landmarks[idx]
                cv2.circle(annotated_image, 
                           (int(landmark.x * annotated_image.shape[1]), 
                            int(landmark.y * annotated_image.shape[0])), 
                            2, color.value, -1)

        return annotated_image
