import cv2
import mediapipe as mp
import serial
import time

try:
    arduino = serial.Serial('COM5', 9600)  
    time.sleep(2)
    print("Arduino connected.")
except Exception as e:
    print(f"Arduino not connected: {e}")
    arduino = None

mp_face_mesh = mp.solutions.face_mesh
mp_face_detection = mp.solutions.face_detection
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)
face_detect = mp_face_detection.FaceDetection(min_detection_confidence=0.6)

LEFT_EYE = [362, 385, 387, 263, 373, 380]
RIGHT_EYE = [33, 160, 158, 133, 153, 144]

def calculate_ear(landmarks, eye):
    p2 = landmarks[eye[1]]
    p6 = landmarks[eye[5]]
    p3 = landmarks[eye[2]]
    p5 = landmarks[eye[4]]
    p1 = landmarks[eye[0]]
    p4 = landmarks[eye[3]]

    ver1 = ((p2.x - p6.x)**2 + (p2.y - p6.y)**2)**0.5
    ver2 = ((p3.x - p5.x)**2 + (p3.y - p5.y)**2)**0.5
    hor = ((p1.x - p4.x)**2 + (p1.y - p4.y)**2)**0.5

    return (ver1 + ver2) / (2.0 * hor)

EAR_THRESHOLD = 0.23
blink_count = 0
is_blinking = False

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    h, w = frame.shape[:2]
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    face_result = face_detect.process(rgb)
    if face_result.detections:
        for det in face_result.detections:
            bbox = det.location_data.relative_bounding_box
            x = int(bbox.xmin * w)
            y = int(bbox.ymin * h)
            w_box = int(bbox.width * w)
            h_box = int(bbox.height * h)
            cv2.rectangle(frame, (x, y), (x + w_box, y + h_box), (0, 255, 0), 2)

    mesh_result = face_mesh.process(rgb)
    if mesh_result.multi_face_landmarks:
        landmarks = mesh_result.multi_face_landmarks[0].landmark

        def draw_eye_rect(eye_points, color):
            xs = [int(landmarks[p].x * w) for p in eye_points]
            ys = [int(landmarks[p].y * h) for p in eye_points]
            x_min, x_max = min(xs), max(xs)
            y_min, y_max = min(ys), max(ys)
            cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), color, 2)

        draw_eye_rect(LEFT_EYE, (255, 0, 0))  # Left eye 
        draw_eye_rect(RIGHT_EYE, (255, 0, 0))  # Right eye 

        left_ear = calculate_ear(landmarks, LEFT_EYE)
        right_ear = calculate_ear(landmarks, RIGHT_EYE)
        ear = (left_ear + right_ear) / 2

        if ear < EAR_THRESHOLD:
            if not is_blinking:
                blink_count += 1
                is_blinking = True
                print(f"Blink #{blink_count}")
                if arduino:
                    arduino.write(b'1')
        else:
            if is_blinking:
                is_blinking = False
                if arduino:
                    arduino.write(b'0')

    cv2.putText(frame, f"Blinks: {blink_count}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

    cv2.imshow("Face + Eye + Blink Detection", frame)
    if cv2.waitKey(1) & 0xFF == 27:  
        break

cap.release()
cv2.destroyAllWindows()
if arduino:
    arduino.close()
