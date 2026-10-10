from ultralytics import YOLO

model = YOLO('yolov8n.pt', verbose=False)

def detect_objects(image_path, confidence_threshold=0.5):
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

def is_sensitive(detections, sensitive_labels=["person"]):
    found = [d["label"] for d in detections if d["label"] in sensitive_labels]
    return len(found) > 0, found

if __name__ == "__main__":
    detections = detect_objects("C:/Privacy-Shield/yolo1.png", confidence_threshold=0.2)
    print(detections)
    print(is_sensitive(detections, sensitive_labels=["person", "dog"]))