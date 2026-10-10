import cv2

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def detect_faces(image_path, min_neighbors=5):
    """
    Detects faces in an image using OpenCV Haar cascade.
    Returns a list of dicts: [{"label": "face", "confidence": None, "box": [x, y, x+w, y+h]}, ...]
    """
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=min_neighbors)
    
    detections = []
    for (x, y, w, h) in faces:
        detections.append({
            "label": "face",
            "confidence": None,
            "box": [x, y, x+w, y+h]
        })
    
    return detections

if __name__ == "__main__":
    results = detect_faces("C:/Privacy-Shield/amma_selfie.jpeg",min_neighbors=8)
    print(f"Faces found: {len(results)}")
    print(results)