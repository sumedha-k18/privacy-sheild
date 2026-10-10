import re
from src.detect_faces import detect_faces
from src.detect_licenseplate import detect_licenseplate
from src.metadata import read_exif
from src.ocr import extract_text

SENSITIVE_KEYWORDS = [
    "aadhaar", "aadhar", "dob", "date of birth", "pan", "passport",
    "address", "phone", "mobile", "email", "account", "credit",
    "certificate", "birth certificate", "voter", "driving licence",
    "uid", "enrolment", "government of india", "income tax", "bank",
    "banking", "balance", "valid", "HSBC", "Mastercard", "HDFC",
    "ICICI", "VISA", "business"
]

def contains_sensitive_text(ocr_results):
    for item in ocr_results:
        text = item["text"].lower()
        if any(keyword in text for keyword in SENSITIVE_KEYWORDS):
            return True, item["text"]
    return False, None

NAME_PATTERNS = [
    r"name\s*:\s*([A-Za-z\s]+)",
    r"s/o\s+([A-Za-z\s]+)",
    r"d/o\s+([A-Za-z\s]+)",
    r"w/o\s+([A-Za-z\s]+)",
    r"husband\s*:\s*([A-Za-z\s]+)",
]

def detect_name_patterns(ocr_text):
    for pattern in NAME_PATTERNS:
        match = re.search(pattern, ocr_text, re.IGNORECASE)
        if match:
            return True, match.group(0)
    return False, None

def detect_aadhaar_number(ocr_text):
    pattern = r'\b\d{4}\s?\d{4}\s?\d{4}\b'
    match = re.search(pattern, ocr_text)
    if match:
        return True, match.group(0)
    return False, None

def is_valid_plate_text(ocr_results):
    """
    Checks if OCR text from a detected region looks like a real Indian license plate.
    Indian plates follow patterns like MH12AB1234 or KA-03-MX-4567
    """
    plate_pattern = r'^[A-Z]{2}[\s\-]?\d{2}[\s\-]?[A-Z]{1,2}[\s\-]?\d{4}$'
    for item in ocr_results:
        text = item["text"].upper().strip().replace(" ", "").replace("-", "")
        if re.match(plate_pattern, text):
            return True
    return False

def analyze_image(image_path):
    results = {
        "image_path": image_path,
        "is_sensitive": False,
        "reasons": [],
        "detections": [],
        "ocr_results": [],
        "sensitive_text_found": False,
        "metadata": {},
        "has_metadata": False
    }

    # Step 1: detect faces
    face_detections = detect_faces(image_path, min_neighbors=8)
    if face_detections:
        count = len(face_detections)
        results["reasons"].append(f"{count} face(s) detected")
        results["is_sensitive"] = True
    results["detections"].extend(face_detections)

    # Step 2: detect license plates with validation
    plate_detections = detect_licenseplate(image_path, confidence_threshold=0.4)
    for d in plate_detections:
        # Run OCR on plate region first
        plate_ocr = extract_text(image_path, d["box"])
        results["ocr_results"].extend(plate_ocr)

        # Only flag if OCR matches plate pattern OR confidence is very high
        if is_valid_plate_text(plate_ocr) or d["confidence"] > 0.7:
            results["reasons"].append(f"license plate detected ({d['confidence']:.0%} confidence)")
            results["is_sensitive"] = True
            results["detections"].append(d)

    # Step 3: run OCR on whole image
    full_image_ocr = extract_text(image_path, [0, 0, 99999, 99999])
    results["ocr_results"].extend(full_image_ocr)

    # Step 4: check keywords and name patterns
    found, matched_text = contains_sensitive_text(full_image_ocr)
    if found:
        results["reasons"].append(f"sensitive text found: '{matched_text}'")
        results["sensitive_text_found"] = True
        results["is_sensitive"] = True

    full_ocr_text = " ".join([item["text"] for item in full_image_ocr])

    name_found, matched_pattern = detect_name_patterns(full_ocr_text)
    if name_found:
        results["reasons"].append(f"personal name pattern found: '{matched_pattern}'")
        results["is_sensitive"] = True

    aadhaar_found, aadhaar_num = detect_aadhaar_number(full_ocr_text)
    if aadhaar_found:
        results["reasons"].append(f"Aadhaar number pattern detected: '{aadhaar_num}'")
        results["is_sensitive"] = True

    # Step 5: check metadata
    exif = read_exif(image_path)
    if exif:
        results["metadata"] = exif
        results["has_metadata"] = True
        results["reasons"].append("EXIF metadata found (may contain GPS/device info)")
        results["is_sensitive"] = True

    return results

if __name__ == "__main__":
    import json
    result = analyze_image("C:/Privacy-Shield/METAA.jpg")
    print(json.dumps({
        "is_sensitive": result["is_sensitive"],
        "reasons": result["reasons"],
        "ocr_results": result["ocr_results"],
        "has_metadata": result["has_metadata"]
    }, indent=2))