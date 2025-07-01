from ultralytics import YOLO
import os
import cv2


class ObjectDetector:
    def __init__(self, model_path="models/_best.pt", threshold=0.5):
        try:
            abs_path = os.path.join(os.path.dirname(__file__), model_path)
            self.model = YOLO(abs_path)
            self.threshold = threshold
            print(f"[INFO] Model loaded successfully: {abs_path}")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            raise

    def detect_objects_in_folder(self, input_folder="static/frames", output_folder="static/annotated_frames"):
        os.makedirs(output_folder, exist_ok=True)

        if not os.path.exists(input_folder):
            print(f"❌ Input folder not found: {input_folder}")
            return

        image_files = sorted([
            f for f in os.listdir(input_folder)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ])[:10]


        if not image_files:
            print(f"❌ No image files found in: {input_folder}")
            return

        print(f"[INFO] Processing {len(image_files)} images...")

        for filename in image_files:
            image_path = os.path.join(input_folder, filename)

            try:
                results = self.model(image_path, conf=self.threshold)
                result = results[0]
                if result.boxes is None or len(result.boxes) == 0:
                    print(f"[NO DETECTIONS] {filename}")
                    continue

                original_image = cv2.imread(image_path)
                if original_image is None:
                    print(f"❌ Could not load image: {filename}")
                    continue

                boxes = result.boxes.data.cpu().numpy()
                drone_count = len(boxes)

                for box in boxes:
                    x1, y1, x2, y2, conf, cls = box
                    x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
                    cv2.rectangle(original_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    label = f"Drone: {conf:.2f}"
                    cv2.putText(original_image, label, (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

                cv2.putText(original_image, f"Detected: {drone_count}", (10, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)

                output_path = os.path.join(output_folder, filename)
                cv2.imwrite(output_path, original_image)
                print(f"[SAVED] {output_path} ({drone_count} objects)")

            except Exception as e:
                print(f"❌ Error processing {filename}: {e}")
                continue

    # 🔴 For live webcam frame detection (Nano model)
    def detect_frame_array(self, frame_array):
        try:
            results = self.model(frame_array, conf=self.threshold)
            return results
        except Exception as e:
            print(f"❌ Error during frame array detection: {e}")
            return None

    def annotate_frame(self, frame, results):
        if results is None or len(results) == 0 or results[0].boxes is None:
            return frame

        boxes = results[0].boxes.data.cpu().numpy()
        for box in boxes:
            x1, y1, x2, y2, conf, cls = box
            x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            label = f"Drone: {conf:.2f}"
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        cv2.putText(frame, f"Detected: {len(boxes)}", (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)

        return frame
