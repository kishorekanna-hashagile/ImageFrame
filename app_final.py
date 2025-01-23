from flask import Flask, render_template, request, session, redirect, url_for
import os
from io import BytesIO
from werkzeug.utils import secure_filename
import base64

app = Flask(__name__)

app.secret_key = os.urandom(24)

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
            filename = secure_filename(profile_pic.filename)

            image_data = BytesIO(profile_pic.read())
            encoded_image = base64.b64encode(image_data.getvalue()).decode('utf-8')

            session['profile_pic'] = encoded_image
            return redirect(url_for('index')) 
    return "No file uploaded"

@app.route('/clear_session', methods=['GET'])
def clear_session():
    session.pop('profile_pic', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
