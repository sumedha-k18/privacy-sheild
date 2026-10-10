import sys
import json
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline import analyze_image

# Define your test cases
# Format: (image_path, expected_sensitive, expected_reasons_contain)
TEST_CASES = [
    # License plates (lp_01 to lp_10)
    ("test/lp_01.jpg", True, ["license plate"]),
    ("test/lp_02.jpg", True, ["license plate"]),
    ("test/lp_03.jpg", True, ["license plate"]),
    ("test/lp_04.jpg", True, ["license plate"]),
    ("test/lp_05.jpg", True, ["license plate"]),
    ("test/lp_06.jpg", True, ["license plate"]),
    ("test/lp_07.png", True, ["license plate"]),
    ("test/lp_08.png", True, ["license plate"]),
    ("test/lp_09.png", True, ["license plate"]),
    ("test/lp_10.png", True, ["license plate"]),

    # EXIF metadata (exif_01 to exif_03)
    ("test/exif_01.jpg", True, ["metadata"]),
    ("test/exif_02.jpg", True, ["metadata"]),
    ("test/exif_03.jpg", True, ["metadata"]),

    # Aadhaar cards (aadhaarcard1 to aadhaarcard3)
    ("test/aadharcard1.jpg", True, ["aadhaar"]),
    ("test/aadharcard2.jpg", True, ["aadhaar"]),
    ("test/aadharcard3.jpg", True, ["aadhaar"]),

    # Bank related (bank_01)
    ("test/bank_01.jpg", True, ["sensitive text"]),

    # Selfies (selfie_01 to selfie_05)
    ("test/selfie_01.png", True, ["face"]),
    ("test/selfie_02.png", True, ["face"]),
    ("test/selfie_03.png", True, ["face"]),
    ("test/selfie_04.png", True, ["face"]),
    ("test/selfie_05.jpg", True, ["face"]),

    # Safe images (safe_01 to safe_09)
    ("test/safe_01.png", False, []),
    ("test/safe_02.png", False, []),
    ("test/safe_03.png", False, []),
    ("test/safe_04.png", False, []),
    ("test/safe_05.png", False, []),
    ("test/safe_06.png", False, []),
    ("test/safe_07.png", False, []),
    ("test/safe_08.png", False, []),
    ("test/safe_09.png", False, []),

    # Birth certificates (birth_01 to birth_02)
    ("test/birth_01.jpg", True, ["sensitive text"]),
    ("test/birth_02.jpg", True, ["sensitive text"]),

    # Credit cards (credit_01 to credit_04)
    ("test/credit_01.jpg", True, ["sensitive text"]),
    ("test/credit_02.jpg", True, ["sensitive text"]),
    ("test/credit_03.jpg", True, ["sensitive text"]),
    ("test/credit_04.jpg", True, ["sensitive text"]),

    # Documents (document_01 to document_03)
    ("test/document_01.jpg", True, ["sensitive text"]),
    ("test/document_02.jpg", True, ["sensitive text"]),
    ("test/document_03.jpg", True, ["sensitive text"]),
]

def evaluate():
    results = {
        "total": 0,
        "correct": 0,
        "false_positives": [],
        "false_negatives": [],
        "details": []
    }
    
    for image_path, expected_sensitive, _ in TEST_CASES:
        full_path = os.path.join(os.path.dirname(__file__), image_path)
        
        try:
            result = analyze_image(full_path)
            predicted_sensitive = result["is_sensitive"]
            correct = predicted_sensitive == expected_sensitive
            
            results["total"] += 1
            if correct:
                results["correct"] += 1
            elif predicted_sensitive and not expected_sensitive:
                results["false_positives"].append(image_path)
            elif not predicted_sensitive and expected_sensitive:
                results["false_negatives"].append(image_path)
                
            results["details"].append({
                "image": image_path,
                "expected": expected_sensitive,
                "predicted": predicted_sensitive,
                "correct": correct,
                "reasons": result["reasons"]
            })
            print(f"{'✓' if correct else '✗'} {image_path}: predicted={predicted_sensitive}, expected={expected_sensitive}")
            
        except Exception as e:
            print(f"ERROR on {image_path}: {e}")
    
    accuracy = results["correct"] / results["total"] * 100
    print(f"\n--- RESULTS ---")
    print(f"Accuracy: {accuracy:.1f}% ({results['correct']}/{results['total']})")
    print(f"False positives: {len(results['false_positives'])}")
    print(f"False negatives: {len(results['false_negatives'])}")
    
    if results["false_positives"]:
        print(f"\nFalse positives (flagged but shouldn't be):")
        for fp in results["false_positives"]:
            print(f"  - {fp}")
    
    if results["false_negatives"]:
        print(f"\nFalse negatives (missed but should have been flagged):")
        for fn in results["false_negatives"]:
            print(f"  - {fn}")
    
    # Save full results
    with open("evaluation_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nFull results saved to evaluation_results.json")

if __name__ == "__main__":
    evaluate()