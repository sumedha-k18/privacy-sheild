from huggingface_hub import hf_hub_download
from ultralytics import YOLO

model_path = hf_hub_download(
    repo_id="Koushim/yolov8-license-plate-detection",
    filename="best.pt"
)
model = YOLO(model_path, verbose=False)

def detect_licenseplate(image_path, confidence_threshold=0.15):
    results = model.predict(source=image_path, conf=confidence_threshold, verbose=False)
    result = results[0]
    flagged = []
    for box in result.boxes:
        class_id = int(box.cls[0])
        class_name = model.names[class_id]
        confidence = float(box.conf[0])
        coordinates = box.xyxy[0].tolist()
        flagged.append({"label": class_name, "confidence": confidence, "box": coordinates})
    return flagged

if __name__ == "__main__":
    detections = detect_licenseplate("C:/Privacy-Shield/lisenceplate.png")
    print(detections)