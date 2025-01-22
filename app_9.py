from flask import Flask, render_template, request
import os

app = Flask(__name__)

FRAME_FOLDER = os.path.join('static', 'frames')

@app.route('/')
def index():
    frames = [f for f in os.listdir(FRAME_FOLDER) if f.lower().endswith(('png', 'svg'))]
    return render_template('index.html', frames=frames)

@app.route('/upload', methods=['POST'])
def upload():
    if 'profile_pic' in request.files:
        profile_pic = request.files['profile_pic']
        if profile_pic.filename != '':
            upload_path = os.path.join('static', 'uploads', profile_pic.filename)
            profile_pic.save(upload_path)
            return f"Uploaded {profile_pic.filename} successfully"
    return "No file uploaded"

if __name__ == '__main__':
    app.run(debug=True)
