# 🛰️ AI-Driven Real-Time Drone Detection and Monitoring via Web Interface

This project is a Flask-based web application designed to detect drones in uploaded videos, images, and live webcam streams using custom-trained YOLOv11 models. Users can upload footage or access the real-time detection mode, after which the app automatically extracts frames, performs drone detection, and visually annotates the results through a responsive dashboard interface.

---

## 🚀 Features

The system includes the following main features:

* 📤 Upload support for both video (`.mp4`, `.avi`) and image (`.jpg`, `.png`) files
* 🎞️ Frame-by-frame extraction using ImageIO or OpenCV
* 🎯 Drone detection using custom-trained YOLOv11m (for uploads) and YOLOv11n (for live webcam)
* 🖼️ Annotated frames with bounding boxes and confidence scores
* 📊 Detection summaries for frame-level analysis
* 🔍 Click-to-zoom modal previews for inspection of frames
* 🖥️ Clean, responsive, dark-themed UI dashboard

---

## 🛠️ Tech Stack

**🔧 Backend Technologies:**

* 🧪 Flask – API routing and detection backend
* 🤖 YOLOv11 (Ultralytics) – custom-trained drone detection models
* 🔥 PyTorch – for YOLO model inference
* 👁️ OpenCV – used for webcam input and optional frame extraction
* 🐍 Python Libraries – `imageio`, `Pillow`, `os`, `uuid`, `shutil`, etc.

**🎨 Frontend Technologies:**

* 🧱 HTML5 + CSS3 – layout and modern dark UI
* ⚡ JavaScript – Fetch API for asynchronous data loading and preview updates

---

## 📁 Project Structure
```
<pre>
├── app.py                       # Flask backend server
├── detector.py                  # YOLOv11 object detection logic
├── render.yaml                  # Script to deploy on Render
├── requirements.txt             # Required Python dependencies
├── models/
│   ├── Nano_Model/
│       ├── 1_nano.pt            # Base YOLOv11n model (from Ultralytics)
│       ├── 2_nano.pt            # Base YOLOv11n model (from Ultralytics - Better)
│   ├── 1_best.pt                 # Custom-trained YOLOv11m model (final version) 
│   ├── 2_best.pt                # Custom-trained YOLOv11m model (final version - Better) 
├── static/
│   ├── annotated_frames/        # YOLO-annotated output images
│   ├── css/
│   │   └── style.css            # Dashboard styling
│   ├── frames/                  # Extracted frames from uploaded media
│   ├── js/
│   │   └── script.js            # Frontend logic (media display, zoom, etc.)
│   └── uploads/                 # Uploaded raw media files
├── templates/
│   └── index.html               # Main dashboard layout (HTML template)
</pre>
```

---

## ⚙️ Setup Instructions

1. 🧩 Clone the repository:  
   `git clone https://github.com/your-username/drone-vision-system.git`

2. 📁 Navigate to the folder:  
   `cd drone-vision-system`

3. 📦 Install dependencies:  
   `pip install -r requirements.txt`

4. 🛠️ Run the Flask app:  
   `python app.py`

5. 🌐 Open your browser:  
   Visit `http://127.0.0.1:5000`
#The server currently runs on local host only.
---

## 📸 Live-Webcam Detection Mode (Not yet implemented)

To run real-time webcam-based detection using the YOLOv11n model:
- Launch the webcam script (if separate), or
- Select “Live Detection” from the interface if enabled.
  
> 🔧 **Planned Feature:**
- Real-time drone detection using live webcam input (to be added in future versions).
- Planned deployment on platforms like Render or Replit to enable public access and real-time online testing.

---

## 📜 License

This project is licensed under the **MIT License**. See the `LICENSE` file for full details.

