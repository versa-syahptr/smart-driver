import cv2

# Create a VideoCapture object
cap = cv2.VideoCapture(0)

# Create a QRCodeDetector object
qr_code_detector = cv2.QRCodeDetector()

while True:
    # Read a frame from the webcam
    ret, frame = cap.read()

    # Detect and decode QR code
    data, points, qr_code = qr_code_detector.detectAndDecode(frame)

    # If a QR code is detected, print the data
    

    # Display the frame
    cv2.imshow('QR Code Reader', frame)

    if data:
        print("QR Code Data:", data)
        break   

    # Break the loop if 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the VideoCapture and close all windows
cap.release()
cv2.destroyAllWindows()
