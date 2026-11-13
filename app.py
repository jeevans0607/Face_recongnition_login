import os, json, base64
from io import BytesIO

import cv2
import numpy as np
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "change-this-demo-secret-key"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
FACES_DIR = os.path.join(DATA_DIR, "faces")
MODEL_PATH = os.path.join(DATA_DIR, "face_model.yml")
LABELS_PATH = os.path.join(DATA_DIR, "labels.json")

os.makedirs(FACES_DIR, exist_ok=True)

# OpenCV's bundled Haar cascade is used to locate faces.
import cv2
import os

cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"

import cv2
import os

cascade_path = os.path.join(
    os.path.dirname(__file__),
    "haarcascade_frontalface_default.xml"
)

face_cascade = cv2.CascadeClassifier(cascade_path)

if face_cascade.empty():
    raise RuntimeError("Haar Cascade XML file not found!")

print("Face detection loaded successfully!")

if face_cascade.empty():
    raise RuntimeError("Face Cascade XML file not loaded!")

print("Face Cascade Loaded Successfully!")

def make_recognizer():
    if not hasattr(cv2, "face"):
        raise RuntimeError(
            "OpenCV face module is missing. Install opencv-contrib-python, "
            "not opencv-python."
        )
    return cv2.face.LBPHFaceRecognizer_create()

def decode_image(data_url):
    if not data_url or "," not in data_url:
        raise ValueError("No webcam image received.")
    raw = base64.b64decode(data_url.split(",", 1)[1])
    image = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Could not read the webcam image.")
    return image

def extract_face(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80)
    )
    if len(faces) == 0:
        raise ValueError("No face detected. Move closer and face the camera.")
    if len(faces) > 1:
        raise ValueError("More than one face detected. Make sure you are alone.")
    x, y, w, h = faces[0]
    face = gray[y:y+h, x:x+w]
    return cv2.resize(face, (200, 200))

def load_labels():
    if os.path.exists(LABELS_PATH):
        with open(LABELS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def train_model():
    labels = {}
    samples, ids = [], []
    names = sorted(
        name for name in os.listdir(FACES_DIR)
        if os.path.isdir(os.path.join(FACES_DIR, name))
    )
    for label_id, username in enumerate(names):
        user_dir = os.path.join(FACES_DIR, username)
        for filename in os.listdir(user_dir):
            if not filename.lower().endswith((".png", ".jpg", ".jpeg")):
                continue
            path = os.path.join(user_dir, filename)
            image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            if image is not None:
                samples.append(cv2.resize(image, (200, 200)))
                ids.append(label_id)
        if any(i == label_id for i in ids):
            labels[str(label_id)] = username

    if not samples:
        raise ValueError("No registered face samples found.")
    recognizer = make_recognizer()
    recognizer.train(samples, np.array(ids, dtype=np.int32))
    recognizer.save(MODEL_PATH)
    with open(LABELS_PATH, "w", encoding="utf-8") as f:
        json.dump(labels, f)
    return len(samples)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["POST"])
def register():
    try:
        username = request.form.get("username", "").strip()
        if not username or len(username) > 24:
            return jsonify(success=False, message="Enter a username (maximum 24 characters)."), 400
        if not username.replace("_", "").isalnum():
            return jsonify(success=False, message="Use only letters, numbers and underscores in the username."), 400

        images = request.form.getlist("images")
        if len(images) < 5:
            return jsonify(success=False, message="Capture at least 5 face samples."), 400

        user_dir = os.path.join(FACES_DIR, username)
        os.makedirs(user_dir, exist_ok=True)

        # Prevent a second registration from silently replacing an existing user.
        if any(f.lower().endswith((".png", ".jpg", ".jpeg")) for f in os.listdir(user_dir)):
            return jsonify(success=False, message="This username is already registered. Try another username."), 409

        saved = 0
        for index, data_url in enumerate(images):
            image = decode_image(data_url)
            face = extract_face(image)
            cv2.imwrite(os.path.join(user_dir, f"sample_{index+1}.png"), face)
            saved += 1

        count = train_model()
        return jsonify(success=True, message=f"Registration successful! Saved {saved} samples. You can now log in.")
    except Exception as e:
        return jsonify(success=False, message=str(e)), 400

@app.route("/login", methods=["POST"])
def login():
    try:
        username = request.form.get("username", "").strip()
        image = decode_image(request.form.get("image"))
        face = extract_face(image)

        if not os.path.exists(MODEL_PATH) or not os.path.exists(LABELS_PATH):
            return jsonify(success=False, message="No users registered yet. Register first."), 400

        recognizer = make_recognizer()
        recognizer.read(MODEL_PATH)
        label_id, confidence = recognizer.predict(face)
        labels = load_labels()
        matched_user = labels.get(str(label_id))

        # LBPH confidence is a distance: lower is a closer match.
        if matched_user == username and confidence < 75:
            session["username"] = matched_user
            return jsonify(success=True, message=f"Welcome, {matched_user}!", confidence=round(confidence, 1))
        return jsonify(success=False, message="Face not recognized for this username. Try again in good lighting."), 401
    except Exception as e:
        return jsonify(success=False, message=str(e)), 400

@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for("home"))
    return render_template("dashboard.html", username=session["username"])

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
