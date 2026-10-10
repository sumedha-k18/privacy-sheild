import easyocr
import cv2

reader = easyocr.Reader(['en'], verbose=False)

def extract_text(image_path, box):
    image = cv2.imread(image_path)
    x1, y1, x2, y2 = [int(coord) for coord in box]
    h, w = image.shape[:2]
    x1 = max(0, x1)
    y1 = max(0, y1)
    x2 = min(w, x2)
    y2 = min(h, y2)
    cropped = image[y1:y2, x1:x2]
    result = reader.readtext(cropped)
    texts = []
    for (_, text, confidence) in result:
        if confidence > 0.1:
            texts.append({"text": text, "confidence": confidence})
    return texts

if __name__ == "__main__":
    box = [355.132080078125, 207.90252685546875, 451.9322509765625, 269.84246826171875]
    print(extract_text("C:/Privacy-Shield/lisenceplate.png", box))