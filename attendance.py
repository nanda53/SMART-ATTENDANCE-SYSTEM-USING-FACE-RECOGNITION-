import tkinter as tk
import cv2
import dlib
import numpy as np
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
from PIL import Image, ImageTk
import threading
import time
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

# Initialize Firebase
cred = credentials.Certificate("smart-attendenc-firebase-adminsdk-n7bv3-f692ab38b6.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://smart-attendenc-default-rtdb.firebaseio.com/',
    'storageBucket': 'smart-attendenc.appspot.com'
})

# Load pre-trained face detector and face recognition model
detector = dlib.get_frontal_face_detector()
sp = dlib.shape_predictor("/home/pi/shape_predictor_68_face_landmarks.dat")
facerec = dlib.face_recognition_model_v1("/home/pi/dlib_face_recognition_resnet_model_v1.dat")

# Initialize webcam
cap = cv2.VideoCapture(0)

# Initialize RFID reader
reader = SimpleMFRC522()

# Dictionary to store known faces and attendance records
known_faces = {}
rfid_verified = False  # Global variable to track RFID verification

# Load known faces from Firebase
def load_known_faces():
    global known_faces
    students_ref = db.reference('students')
    students = students_ref.get()
    if students:
        for student_id, student in students.items():
            known_faces[student_id] = {
                'face_encoding': np.array(student['face_encoding']),
                'rfid': student.get('rfid'),
                'attendance_count': student.get('attendance_count', 0),
                'last_seen': student.get('last_seen', None)
            }
    print("Known faces loaded from Firebase.")

load_known_faces()

# Function to mark attendance and update student details
def mark_attendance(student_id, action):
    timestamp = datetime.now()
    students_ref = db.reference('students')
    student_ref = students_ref.child(student_id)

    if action == 'entry':
        student_ref.update({
            'entry_time': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'last_seen': timestamp.strftime('%Y-%m-%d %H:%M:%S')
        })
        print(f"{student_id} entered at {timestamp}")
    elif action == 'exit':
        student_ref.update({
            'exit_time': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'last_seen': timestamp.strftime('%Y-%m-%d %H:%M:%S')
        })
        print(f"{student_id} exited at {timestamp}")

# Function to capture frame from webcam
def capture_frame():
    ret, frame = cap.read()
    if not ret:
        return None
    return frame

# Function to process frame for face recognition
def process_frame():
    frame = capture_frame()
    if frame is None:
        return

    faces = detector(frame, 1)
    detected_students = set()
    for face in faces:
        shape = sp(frame, face)
        face_encoding = facerec.compute_face_descriptor(frame, shape)
        face_encoding = np.array(face_encoding)

        matches = {}
        for student_id, data in known_faces.items():
            encoding = data['face_encoding']
            matches[student_id] = np.linalg.norm(face_encoding - encoding)

        best_match = min(matches, key=matches.get)
        if matches[best_match] < 0.6:
            detected_students.add(best_match)
            student_data = known_faces[best_match]
            last_seen = student_data['last_seen']
            if last_seen is None or (datetime.now() - datetime.strptime(last_seen, '%Y-%m-%d %H:%M:%S')).seconds > 30:
                mark_attendance(best_match, 'entry')
                student_data['attendance_count'] += 1
                student_ref = db.reference('students').child(best_match)
                student_ref.update({'attendance_count': student_data['attendance_count']})
                student_data['last_seen'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    for student_id in known_faces:
        if student_id not in detected_students:
            student_data = known_faces[student_id]
            last_seen = student_data['last_seen']
            if last_seen is not None:
                mark_attendance(student_id, 'exit')
                student_ref = db.reference('students').child(student_id)
                student_ref.update({'attendance_count': student_data['attendance_count']})
                student_data['last_seen'] = None

    return frame

# Function to update video feed on GUI
def update_frame():
    if rfid_verified:
        frame = process_frame()
        if frame is not None:
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            imgtk = ImageTk.PhotoImage(image=img)
            lbl_video.imgtk = imgtk
            lbl_video.configure(image=imgtk)
        lbl_video.after(1000, update_frame)  # Update every second

# Function to handle RFID card reading continuously
def rfid_reader():
    global rfid_verified
    print("RFID reader started.")
    while True:
        try:
            rfid_id, _ = reader.read()
            rfid_id = str(rfid_id).strip()  # Ensure no extra spaces
            print(f"Detected RFID ID: {rfid_id}")

            # Check if RFID ID is in the known faces
            for student_id, data in known_faces.items():
                stored_rfid = data['rfid']
                if stored_rfid and rfid_id == stored_rfid.strip():  # Compare cleaned RFID IDs
                    print(f"RFID card detected for student ID: {student_id}")
                    rfid_verified = True  # Set RFID as verified
                    start_webcam()  # Start the webcam feed
                    time.sleep(10)  # Pause RFID reading for 10 seconds after successful read
                    break
            else:
                print("Unknown RFID card. Access denied.")
                rfid_verified = False  # Reset RFID verification status
                time.sleep(1)  # Pause RFID reading for 1 second

        except Exception as e:
            print(f"RFID read error: {e}")
            rfid_verified = False  # Reset RFID verification status
            time.sleep(1)  # Pause RFID reading for 1 second

# Function to start the webcam feed
def start_webcam():
    lbl_video.configure(image='')  # Clear previous image
    update_frame()

# GUI Setup
root = tk.Tk()
root.title("Smart Attendance System")

lbl_video = tk.Label(root)
lbl_video.pack()

btn_start_webcam = tk.Button(root, text="Start Webcam", command=start_webcam)
btn_start_webcam.pack()

# Start the RFID reader thread
rfid_thread = threading.Thread(target=rfid_reader, daemon=True)
rfid_thread.start()

root.mainloop()

# Release the webcam when the GUI window is closed
cap.release()
GPIO.cleanup()
