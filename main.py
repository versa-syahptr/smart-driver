import cv2
import tkinter as tk
from sdp import SDP
from qr import QRCodeGenerator

sdp = SDP(source=0)

@sdp.tracker.set_action_callback
def putText(text: str, image):
    # create red border to image
    cv2.rectangle(image, (0, 0), (image.shape[1], image.shape[0]), (0, 0, 255), 10)
    # put text to image
    cv2.putText(image, text, (10, 270),  
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    
    # save image
    # cv2.imwrite(f"result-{text}.jpg", image)

if __name__ == "__main__":
    fullscreen = False
    root = tk.Tk()
    root.title("Smart Driver Setup")
    root.attributes("-fullscreen", fullscreen)
    qr_generator = QRCodeGenerator(root)
    qr_generator.pack(fill=tk.BOTH, expand=True)
    root.mainloop()
    sdp.run(fullscreen=fullscreen)
