# 🔐 Smart Attendance System using Face Recognition + RFID + Firebase

This project is a smart attendance system built using:

- 🎯 Face Recognition (via webcam)
- 📡 RFID tag detection
- ☁️ Firebase Realtime Database
- 🐍 Python (OpenCV, face_recognition, firebase_admin)

✅ Students are authenticated via RFID and face before attendance is marked.  
✅ Real-time logs are synced to Firebase.

---

## 🚀 Features

- Register new students with RFID + face encoding
- Match RFID + face to verify student identity
- Record entry and exit times
- Store attendance logs to Firebase Realtime DB

---

## 🧠 How It Works

1. `register.py` is used to register a new student with:
   - USN (student ID)
   - RFID tag
   - Face encoding (captured via webcam)

2. `attendance.py`:
   - Reads RFID from the scanner
   - Captures a face and compares it with stored encodings
   - If both match, logs entry/exit time and updates attendance count

---
## 🚀 Firebase Setup Instructions


1.Create a Firebase project:
   -Go to Firebase Console → Add Project → Complete the setup.


2.Enable the Realtime Database
   -In your project, go to Build > Realtime Database
   -Click Create Database → Start in test mode (for quick testing).
   -Note the database URL (like https://<your-database-name>.firebaseio.com/).

  
3.Generate a Service Account
   -In Project Settings > Service Accounts, click Generate new private key.  
   -Save it as smart-attendenc-firebase-adminsdk-n7bv3-f692ab38b6.json in your project directory.     


4.Add Firebase Admin SDK in Python:

   -Install the package:

    pip install firebase-admin


   -Initialize Firebase in your script:

      import firebase_admin
      from firebase_admin import credentials, db
      
      cred = credentials.Certificate("smart-attendenc-firebase-adminsdk-n7bv3-f692ab38b6.json")
      firebase_admin.initialize_app(cred, {
          'databaseURL': 'https://<your-database-name>.firebaseio.com/'
      })

## 🏗️ Firebase Realtime Database Structure

students

├── 4jn21et001

│ ├── face_encoding: [0.124, 0.542, ..., 0.989]

│ ├── rfid: "291034509490"


│ ├── attendance_count: 4

│ ├── entry_time: "2025-05-31 09:00:00"

│ └── exit_time: "2025-05-31 15:00:00"

