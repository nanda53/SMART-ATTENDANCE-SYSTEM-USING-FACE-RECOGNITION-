🔐 Smart Attendance System using Face Recognition + RFID + Firebase
This project is a smart attendance system built using:

🎯 Face Recognition (via webcam)

📡 RFID tag detection

☁️ Firebase Realtime Database

🐍 Python (OpenCV, face_recognition, firebase_admin)

✅ Students are authenticated via RFID and face before attendance is marked.
✅ Real-time logs are synced to Firebase.

📷 Hardware Required
Webcam

RFID module (e.g., RC522 or 125kHz reader)

RFID tags

Rassberry pi 4b

🚀 Features
Register new students with RFID + face encoding

Match RFID + face to verify student identity

Record entry and exit times

Store attendance logs to Firebase Realtime DB

🧠 How It Works
register.py is used to register a new student with:

USN (student ID)

RFID tag

Face encoding (captured via webcam)

attendance.py:

Reads RFID from the scanner

Captures a face and compares it with stored encodings

If both match, logs entry/exit time and updates attendance count

🏗️ Firebase Realtime Database Structure
students
├── 4jn21et001
│ ├── face_encoding: [...]
│ ├── rfid: "291034509490"
│ ├── attendance_count: 4
│ ├── entry_time: "2025-05-31 09:00:00"
│ └── exit_time: "2025-05-31 15:00:00"

