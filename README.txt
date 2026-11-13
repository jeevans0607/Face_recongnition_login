FACE RECOGNITION LOGIN - SETUP GUIDE (WINDOWS)

REQUIREMENTS
- Windows laptop
- Python 3.10 or 3.11 (recommended)
- Chrome or Edge
- Working webcam

STEP 1: EXTRACT
Extract face_recognition_login.zip to a folder, for example:
Desktop\face_recognition_login

STEP 2: OPEN THE FOLDER IN VS CODE
Open VS Code -> File -> Open Folder -> select face_recognition_login.

STEP 3: OPEN TERMINAL
In VS Code select Terminal -> New Terminal.
Make sure the terminal is inside the project folder.

STEP 4: CREATE A VIRTUAL ENVIRONMENT
Run:
py -3.11 -m venv venv

If that command does not work, try:
python -m venv venv

STEP 5: ACTIVATE IT
PowerShell:
.\venv\Scripts\Activate.ps1

If PowerShell blocks activation, use Command Prompt terminal and run:
venv\Scripts\activate.bat

STEP 6: INSTALL PACKAGES
Run:
python -m pip install --upgrade pip
pip install -r requirements.txt

IMPORTANT: The project needs opencv-contrib-python because it contains
the cv2.face LBPH recognizer. Do not install opencv-python alongside it.

STEP 7: START THE APP
Run:
python app.py

You should see a message showing:
http://127.0.0.1:5000

STEP 8: OPEN THE WEB PAGE
Open Chrome or Edge and visit:
http://127.0.0.1:5000

STEP 9: REGISTER
1. Click Start Camera.
2. Allow camera permission.
3. Enter a username, for example student1.
4. Look straight at the camera in good lighting.
5. Click Capture & Register Face.
6. Keep still until the 5 samples are captured.

STEP 10: LOGIN
1. Enter the same username in the Login section.
2. Look at the camera.
3. Click Login with Face.
4. If the face matches, the Dashboard opens.
5. Click Logout to return.

TROUBLESHOOTING
- Camera not opening: close other apps using the webcam and allow camera permission.
- cv2.face missing: uninstall both OpenCV packages and reinstall the contrib package:
  pip uninstall opencv-python opencv-contrib-python -y
  pip install opencv-contrib-python==4.10.0.84
- No face detected: improve lighting, face the camera, and move closer.
- PowerShell activation blocked: use Command Prompt and run venv\Scripts\activate.bat.
- Port 5000 busy: close the other Flask app using that port, then restart.

HOW TO STOP
In the terminal press Ctrl+C.

PRIVACY / SECURITY NOTE
This is a beginner educational demo using OpenCV Haar detection and LBPH
recognition. It is not liveness detection and can be fooled by a photo.
It stores face samples locally in data/faces. Do not use real sensitive
accounts or deploy this as production authentication. Delete the data/faces
folder and data/face_model.yml to remove registered demo samples.
