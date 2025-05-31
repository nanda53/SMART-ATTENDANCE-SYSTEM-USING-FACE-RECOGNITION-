import cv2
import face_recognition
import numpy as np
import firebase_admin
from firebase_admin import credentials, db
import time

# Initialize Firebase
cred = credentials.Certificate("smart-attendenc-firebase-adminsdk-n7bv3-f692ab38b6.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://<your-database-name>.firebaseio.com/'
})

# Get student details
student_id = input("Enter Student ID: ")
student_rfid = input("Enter RFID: ")

# Initialize webcam
cap = cv2.VideoCapture(0)
print("Please look at the camera for face registration...")

face_encoding = None

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)

    if face_locations:
        face_encoding = face_recognition.face_encodings(rgb_frame, face_locations)[0]
        # Draw rectangle around the face
        for (top, right, bottom, left) in face_locations:
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

        cv2.imshow("Registration - Press 's' to Save", frame)

        # Press 's' to save the face encoding
        if cv2.waitKey(1) & 0xFF == ord('s'):
            print("Saving face encoding and RFID...")
            break
    else:
        cv2.imshow("Registration - No face detected", frame)
        cv2.waitKey(1)

cap.release()
cv2.destroyAllWindows()

if face_encoding is not None:
    # Convert the numpy array to a list
    encoding_list = face_encoding.tolist()

    # Save to Firebase
    ref = db.reference(f'students/{student_id}')
    ref.set({
        'rfid': student_rfid,
        'face_encoding': encoding_list,
        'attendance_count': 0,
        'entry_time': '',
        'exit_time': '',
        'last_seen': ''
    })

    print(f"Student {student_id} registered successfully in Firebase!")
else:
    print("No face encoding found. Please try again.")
