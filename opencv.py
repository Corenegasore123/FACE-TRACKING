import cv2
import serial
import time
# Initialize serial
try:
    ser = serial.Serial('COM7', 9600, timeout=1)  # Replace with your port
    time.sleep(2)
except serial.SerialException:
    print("Error: Could not open serial port.")
    exit()
# Load Haar Cascade
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
# Initialize video capture
cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
# Control parameters
KP = 0.05  # Proportional gain
DEADZONE = 50  # Pixels offset before moving
MIN_ANGLE, MAX_ANGLE = 30, 150  # Match Arduino limits
current_angle = 90  # Start centered
# Get frame dimensions
ret, frame = cap.read()
if not ret:
    print("Error: Could not open webcam.")
    ser.close()
    exit()
h, w = frame.shape[:2]
frame_center_x = w // 2
# Tracking variables
prev_cx, prev_cy = None, None
prev_time = time.time()
while True:
    ret, frame = cap.read()
    if not ret:
        break
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    current_time = time.time()
    time_diff = current_time - prev_time if prev_time is not None else 1.0
    direction = ""
    speed = 0.0
    motor_adjusted = False
    horizontal_direction = "CENTERED"
    for (x, y, w, h) in faces:
        # Draw bounding box
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cx = x + w // 2
        cy = y + h // 2
        cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
        # Movement tracking
        if prev_cx is not None and prev_cy is not None:
            dx = cx - prev_cx
            dy = cy - prev_cy
            if abs(dx) > 10 or abs(dy) > 10:
                if abs(dx) > abs(dy):
                    direction = "Right" if dx > 0 else "Left"
                else:
                    direction = "Down" if dy > 0 else "Up"
            distance = ((dx ** 2) + (dy ** 2)) ** 0.5
            speed = distance / time_diff if time_diff > 0 else 0
        # Stepper control: Keep face centered horizontally
        offset_x = cx - frame_center_x
        if abs(offset_x) > DEADZONE:
            angle_adjust = int(KP * offset_x)
            new_angle = current_angle - angle_adjust  # Negative for correct direction
            new_angle = max(MIN_ANGLE, min(MAX_ANGLE, new_angle))
            ser.write(f"{new_angle}\n".encode())
            current_angle = new_angle
            motor_adjusted = True
            # Update horizontal direction
            horizontal_direction = "LEFT" if offset_x > 0 else "RIGHT"
        else:
            horizontal_direction = "CENTERED"
        prev_cx, prev_cy = cx, cy
        prev_time = current_time
        break  # Track only first face
    # Display info
    text = f"Direction: {horizontal_direction}, Speed: {speed:.2f} px/s"
    if motor_adjusted:
        text += f" | Stepper: {current_angle}°"
    cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.imshow('Face Stepper Tracker', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
# Cleanup
ser.close()
cap.release()
cv2.destroyAllWindows()