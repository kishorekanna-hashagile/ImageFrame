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

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)
os.makedirs(FRAME_FOLDER, exist_ok=True) 

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        logging.info("Received a POST request.")

        profile_pic = request.files.get('profile_pic')
        selected_frame = request.form.get('selected_frame')

        if not profile_pic or not selected_frame:
            logging.error("Profile picture or frame not selected.")
            return jsonify({"error": "Profile picture and a frame are required"}), 400

        if profile_pic.filename == '':
            logging.error("Empty file name detected for profile picture.")
            return jsonify({"error": "Profile picture name cannot be empty"}), 400

        profile_path = os.path.join(UPLOAD_FOLDER, profile_pic.filename)
        template_path = os.path.join(FRAME_FOLDER, selected_frame)

        profile_pic.save(profile_path)
        logging.info("Profile picture saved successfully.")

        try:
            result_path = process_images(profile_path, template_path)
            logging.info(f"Image processing completed. Result saved at {result_path}")
            return render_template('index.html', result_image=result_path, frames=get_frame_list())
        except Exception as e:
            logging.error(f"Error during image processing: {e}")
            return jsonify({"error": "Error processing images"}), 500

    return render_template('index.html', result_image=None, frames=get_frame_list())


def get_frame_list():
    return [f for f in os.listdir(FRAME_FOLDER) if f.lower().endswith(('png', 'svg'))]


def process_images(profile_path, template_path):
    logging.info("Starting image processing...")
    profile_image = Image.open(profile_path).convert("RGBA")
    template_image = Image.open(template_path).convert("RGBA")

    profile_width, profile_height = profile_image.size
    min_dim = min(profile_width, profile_height)
    profile_image = profile_image.crop((
        (profile_width - min_dim) // 2,
        (profile_height - min_dim) // 2,
        (profile_width + min_dim) // 2,
        (profile_height + min_dim) // 2
    ))

    profile_image = profile_image.resize((template_image.width, template_image.height), Image.Resampling.LANCZOS)

    combined_image = Image.new("RGBA", template_image.size)
    combined_image.paste(profile_image, (0, 0))
    combined_image.paste(template_image, (0, 0), template_image)

    combined_image_rgb = combined_image.convert("RGB")
    
    result_image_path = os.path.join(RESULT_FOLDER, 'result_image.jpg')
    combined_image_rgb.save(result_image_path, "JPEG")

    logging.info("Image processing complete.")
    return 'result/result_image.jpg'

@app.route('/download')
def download():
    result_image_path = os.path.join(RESULT_FOLDER, 'result_image.jpg')
    if os.path.exists(result_image_path):
        logging.info("File ready for download.")
        return send_file(result_image_path, as_attachment=True)
    else:
        logging.error("Result image not found for download.")
        return jsonify({"error": "Result image not found"}), 404


if __name__ == '__main__':
    app.run(debug=True)
