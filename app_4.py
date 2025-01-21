from flask import Flask, render_template, request, send_file, jsonify
import os
from PIL import Image
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads/'
RESULT_FOLDER = 'static/result/'
FRAME_FOLDER = 'static/frames/'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = RESULT_FOLDER
app.config['FRAME_FOLDER'] = FRAME_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)
os.makedirs(FRAME_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        logging.info("Received a POST request.")

        profile_pic = request.files.get('profile_pic')
        selected_frame = request.form.get('selected_frame')
        scale = float(request.form.get('scale', 1.0))
        rotation = float(request.form.get('rotation', 0))
        posX = float(request.form.get('posX', 0))
        posY = float(request.form.get('posY', 0))

        if not profile_pic or not selected_frame:
            logging.error("Profile picture or frame not provided.")
            return jsonify({"error": "Profile picture and a frame are required"}), 400

        if profile_pic.filename == '':
            logging.error("Empty file name detected for profile picture.")
            return jsonify({"error": "Profile picture file name cannot be empty"}), 400

        profile_path = os.path.join(app.config['UPLOAD_FOLDER'], profile_pic.filename)
        template_path = os.path.join(app.config['FRAME_FOLDER'], os.path.basename(selected_frame))
        profile_pic.save(profile_path)
        logging.info(f"Profile picture saved at {profile_path}")

        try:
            result_path = process_images(profile_path, template_path, scale, rotation, posX, posY)
            logging.info(f"Image processing completed. Result saved at {result_path}")
            return jsonify({"result_image": result_path})
        except FileNotFoundError as e:
            logging.error(f"File not found: {e}")
            return jsonify({"error": str(e)}), 404
        except Exception as e:
            logging.error(f"Error during image processing: {e}")
            return jsonify({"error": "Error processing image"}), 500

    return render_template('index.html', result_image=None, frames=get_frame_list(), selected_frame=None)

def get_frame_list():
    return [f for f in os.listdir(app.config['FRAME_FOLDER']) if f.lower().endswith(('png', 'jpg', 'jpeg'))]

def process_images(profile_path, template_path, scale, rotation, posX, posY):
    logging.info("Starting image processing...")

    logging.debug(f"Profile path: {profile_path}")
    logging.debug(f"Template path: {template_path}")

    if not os.path.exists(profile_path):
        logging.error(f"Profile picture file does not exist: {profile_path}")
        raise FileNotFoundError(f"Profile picture file not found: {profile_path}")
    profile_image = Image.open(profile_path).convert("RGBA")
    logging.debug(f"Profile exists: {profile_path}")

    if not os.path.exists(template_path):
        logging.error(f"Frame file does not exist: {template_path}")
        raise FileNotFoundError(f"Frame file not found: {template_path}")
    template_image = Image.open(template_path).convert("RGBA")
    logging.debug(f"Frame exists: {template_image}")

    profile_image = profile_image.resize(template_image.size, Image.Resampling.LANCZOS)
    profile_image = profile_image.rotate(-rotation, expand=True)

    scaled_width = int(profile_image.width * scale)
    scaled_height = int(profile_image.height * scale)
    profile_image = profile_image.resize((scaled_width, scaled_height), Image.Resampling.LANCZOS)

    combined_image = Image.new("RGBA", template_image.size)

    posX = int((template_image.width - profile_image.width) / 2 + posX)
    posY = int((template_image.height - profile_image.height) / 2 + posY)

    combined_image.paste(profile_image, (posX, posY), profile_image)

    combined_image.paste(template_image, (0, 0), template_image)

    combined_image_rgb = combined_image.convert("RGB")
    result_image_path = os.path.join(app.config['RESULT_FOLDER'], 'result_image.jpg')
    combined_image_rgb.save(result_image_path, "JPEG")

    logging.info(f"Image processing complete. Result saved at {result_image_path}")
    return result_image_path

@app.route('/download')
def download():
    result_image_path = os.path.join(app.config['RESULT_FOLDER'], 'result_image.jpg')

    if os.path.exists(result_image_path):
        logging.info("File ready for download.")
        return send_file(result_image_path, as_attachment=True)
    else:
        logging.error("Result image not found for download.")
        return jsonify({"error": "Result image not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
