import time
import cv2
import tkinter as tk
from PIL import Image, ImageTk

from landmarker import FaceLandmarker
from utils import calculate_EAR, calculate_MAR, head_pose_rotation, ChoosenIndices, ChoosenLandmarks, Color

import simpleaudio as sa

filename = 'metal-pipe-clang.wav'
wave_obj = sa.WaveObject.from_wave_file(filename)
play_obj = None

fld = FaceLandmarker()


class VideoPlayer:
    def __init__(self, root, video_source=0, width=480, height=320):
        self.root = root
        self.root.title("OpenCV and Tkinter Video Player")

        # Open the video source (a filename or camera index)
        self.vid = cv2.VideoCapture(video_source)

        # Get the video source width and height
        self.width = width
        self.height = height

        # Create a Tkinter label to display the video
        self.canvas = tk.Canvas(root, width=self.width, height=self.height)
        self.canvas.pack()

        # Create a button to start and stop the video
        self.btn_start_stop = tk.Button(root, text="Start/Stop", command=self.toggle_playback)
        self.btn_start_stop.pack()

        # Initialize other variables
        self.is_playing = False
        self.update()
        self.start_time = time.perf_counter()
        self.merem_time = 0

        # Run the Tkinter event loop
        self.root.mainloop()

    def toggle_playback(self):
        self.is_playing = not self.is_playing

    def update(self):
        if self.is_playing:
            # Get a frame from the video source
            success, image = self.vid.read()
            # if not success:
            #     print("Failed to read frame")
            #     break
            image = cv2.flip(image, 1)
            fld.detect(image)
            # image = fld.draw_default_landmarks(image)
            if fld.last_result:
                # image = fld.draw_default_landmarks(image)
                h, w, c = image.shape
                choosen_landmarks = fld.get_chosen_landmarks(w, h)
                # print(len(choosen_landmarks.left_eye), len(choosen_landmarks.right_eye), len(choosen_landmarks.mouth))
                if choosen_landmarks.isFull:
                    ear = calculate_EAR(choosen_landmarks)
                    # print("EAR: ", ear, end="\r")
                    if ear < 0.15:
                        end_time = time.perf_counter()
                        image = fld.draw_chosen_landmarks(image, Color.RED)
                        self.merem_time += end_time - self.start_time

                        if self.merem_time > 1.5:
                            cv2.putText(image, "MEREM", (10, 120), 
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                            # playsound("danger.mp3", block=False)
                            print("MEREM")
                            play_obj = wave_obj.play()
                        # print("play")

                            self.merem_time = 0
                    else:
                        image = fld.draw_chosen_landmarks(image, Color.GREEN)
                        self.merem_time = 0
                        self.start_time = time.perf_counter()

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
                    # print(choosen_landmarks.pose2d[0], p1, p2)
                    cv2.line(image, p2, p1, (255, 0, 0), 3)
                    cv2.circle(image, p1, 2, (0, 255, 0), -1)

                    
                    cv2.putText(image, text, (10, 240),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    
            # Convert the image to Tkinter format
            self.update_canvas(image)

            

        # Repeat the update method after 10 milliseconds
        self.root.after(5, self.update)
    
    def update_canvas(self, image) -> None:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        # resize image to fit canvas
        image = image.resize((self.width, self.height), Image.LANCZOS)
        image_tk = ImageTk.PhotoImage(image)
        
        self.canvas.create_image(0, 0, image=image_tk, anchor=tk.NW)
        self.canvas.img_tk = image_tk # type: ignore

    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()

# Create the main Tkinter window and VideoPlayer instance
root = tk.Tk()
# root.geometry("480x320")
print(root.winfo_screenwidth(), root.winfo_screenheight())
# bind ctrl+q key to quit
root.bind("<Control-q>", lambda e: root.destroy())
# set fullscreen
root.attributes("-fullscreen", True)
player = VideoPlayer(root, 1)

# Destroy the main window when closed
# root.protocol("WM_DELETE_WINDOW", root.destroy)
