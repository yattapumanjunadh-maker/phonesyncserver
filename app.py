from flask import Flask, request, jsonify
import sqlite3
import os
from flask import send_from_directory

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app = Flask(__name__)

@app.route("/")
def home():
    return "PhoneSync Server Running Successfully!"

@app.route("/register", methods=["POST"])
def register():

    data = request.json

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, email, password)
        )

        conn.commit()
        conn.close()

        return jsonify({
            "status": "success",
            "message": "User Registered Successfully"
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })
@app.route("/login", methods=["POST"])
def login():

    data = request.json

    email = data.get("email")
    password = data.get("password")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE email=? AND password=?",
        (email, password)
    )

    user = cursor.fetchone()
    conn.close()

    if user:
        return jsonify({
            "status": "success",
            "message": "Login Successful"
        })

    return jsonify({
        "status": "error",
        "message": "Invalid Email or Password"
    })
@app.route("/upload", methods=["POST"])
def upload_file():

    if "file" not in request.files:
        return jsonify({
            "status": "error",
            "message": "No file selected"
        })

    file = request.files["file"]

    if file.filename == "":
        return jsonify({
            "status": "error",
            "message": "Empty filename"
        })

    import os
    import time

    filename = f"photo_{int(time.time() * 1000)}.jpg"
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(save_path)


    return jsonify({
    "status": "success",
    "message": "File uploaded successfully",
    "filename": filename
    })
@app.route('/files', methods=['GET'])
def list_files():
    files = os.listdir(UPLOAD_FOLDER)

    return jsonify({
        "status": "success",
        "files": files
    })
@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(
        UPLOAD_FOLDER,
        filename,
        as_attachment=True
    )
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)