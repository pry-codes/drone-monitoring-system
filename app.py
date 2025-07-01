print("✅ app.py is running", flush=True)
from flask import Flask, request, jsonify, send_from_directory, render_template
from werkzeug.utils import secure_filename
import os
import uuid
import imageio
from PIL import Image
import shutil
from detector import ObjectDetector  # ✅ Ensure this class exists

app = Flask(__name__)

# Absolute paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
FRAME_FOLDER = os.path.join(BASE_DIR, 'static', 'frames')
ANNOTATED_FOLDER = os.path.join(BASE_DIR, 'static', 'annotated_frames')

ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv', 'webm', 'jpg', 'jpeg', 'png', 'webp'}

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(FRAME_FOLDER, exist_ok=True)
os.makedirs(ANNOTATED_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['FRAME_FOLDER'] = FRAME_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_free_space_mb(folder):
    total, used, free = shutil.disk_usage(folder)
    return free // (1024 * 1024)

@app.route("/")
def index():
    return render_template("index.html")  # ✅ Make sure this file exists

@app.route("/ping")
def ping():
    return "pong", 200

@app.route("/upload", methods=["POST"])
def upload_file():
    try:
        print("📥 Received upload request", flush=True)

        if "media" not in request.files:
            return jsonify({"error": "No file part"}), 400

        file = request.files["media"]
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400

        if file and allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = secure_filename(f"{uuid.uuid4()}.{ext}")
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)

            media_url = "/static/uploads/" + filename
            frame_urls = []

            # Clear previous frames
            for f in os.listdir(FRAME_FOLDER):
                os.remove(os.path.join(FRAME_FOLDER, f))
            for f in os.listdir(ANNOTATED_FOLDER):
                os.remove(os.path.join(ANNOTATED_FOLDER, f))

            # Check free disk space
            if get_free_space_mb(FRAME_FOLDER) < 100:
                return jsonify({"error": "Not enough disk space (min 100MB required)"}), 500

            # Extract frames from video
            if ext in ["mp4", "mov", "avi", "mkv"]:
                try:
                    print("🎞 Extracting frames from video...", flush=True)
                    reader = imageio.get_reader(filepath)
                    fps = reader.get_meta_data().get("fps", 30)
                    frame_interval = int(fps) if fps > 0 else 30
                    max_frames = 180
                    saved_frame_count = 0

                    for i, frame in enumerate(reader):
                        if i % frame_interval == 0:
                            frame_img = Image.fromarray(frame)
                            frame_filename = f"{uuid.uuid4()}.jpg"
                            frame_path = os.path.join(FRAME_FOLDER, frame_filename)
                            frame_img.save(frame_path)
                            frame_urls.append(f"/static/frames/{frame_filename}")
                            saved_frame_count += 1
                        if saved_frame_count >= max_frames:
                            break
                except Exception as e:
                    return jsonify({"error": f"Failed to extract frames: {str(e)}"}), 500

            elif ext in ["jpg", "jpeg", "png", "webp"]:
                try:
                    print("🖼️ Processing image frame...", flush=True)
                    img = Image.open(filepath)
                    frame_filename = f"{uuid.uuid4()}.jpg"
                    frame_path = os.path.join(FRAME_FOLDER, frame_filename)
                    img.save(frame_path)
                    frame_urls.append(f"/static/frames/{frame_filename}")
                except Exception as e:
                    return jsonify({"error": f"Failed to process image: {str(e)}"}), 500

            # 🔍 Run YOLO detection
            try:
                print("🤖 Running YOLOv8 detection...", flush=True)
                detector = ObjectDetector(model_path="models/2_best.pt")
                detector.detect_objects_in_folder(
                    input_folder=FRAME_FOLDER,
                    output_folder=ANNOTATED_FOLDER
                )

                annotated_urls = [
                    f"/static/annotated_frames/{f}" for f in os.listdir(ANNOTATED_FOLDER)
                    if f.lower().endswith((".jpg", ".jpeg", ".png"))
                ]

                total_frames = len(frame_urls)
                frames_with_detections = len(annotated_urls)
                detection_summary = f"Drones detected in {frames_with_detections} out of {total_frames} frames"

                print("✅ Detection complete", flush=True)

            except Exception as e:
                return jsonify({"error": f"Detection failed: {str(e)}"}), 500

            return jsonify({
                "filename": filename,
                "mediaUrl": media_url,
                "frameUrls": frame_urls,
                "annotatedFrameUrls": annotated_urls,
                "summary": detection_summary
            })

        return jsonify({"error": "File type not supported"}), 400

    except Exception as e:
        print(f"❌ Unhandled exception in upload: {e}", flush=True)
        return jsonify({"error": "Server crashed during processing"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
