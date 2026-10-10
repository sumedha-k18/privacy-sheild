import streamlit as st
import tempfile
import os
import cv2
import numpy as np
from PIL import Image
from pipeline import analyze_image
from src.metadata import strip_metadata

st.set_page_config(
    page_title="Privacy Shield",
    page_icon="🔒",
    layout="wide"
)

# Header
st.title("🔒 Privacy Shield")
st.write("Upload an image to check if it contains sensitive information before posting online.")
st.divider()

uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])

def draw_boxes(image_path, detections):
    """Draw bounding boxes on detected regions."""
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    for d in detections:
        if d["box"] is None:
            continue
        x1, y1, x2, y2 = [int(c) for c in d["box"]]
        label = d["label"]
        
        # Different colors per detection type
        if label == "face":
            color = (255, 100, 100)   # red
        elif label == "license_plate":
            color = (255, 165, 0)     # orange
        else:
            color = (100, 100, 255)   # blue
        
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
        cv2.putText(image, label, (x1, y1 - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    
    return image
  
if uploaded_file is not None:
    # Save temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    with st.spinner("Analyzing image..."):
        result = analyze_image(tmp_path)

    # Layout: two columns
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Original Image")
        st.image(tmp_path, use_container_width=True)

        # Annotated image
        if result["detections"]:
            st.subheader("Detected Regions")
            annotated = draw_boxes(tmp_path, result["detections"])
            st.image(annotated, use_container_width=True)

    with col2:
        st.subheader("Analysis Results")

        # Verdict
        if result["is_sensitive"]:
            st.error("⚠️ Not safe to upload — sensitive information detected")
        else:
            st.success("✅ Looks safe to upload")

        # Metrics row
        m1, m2, m3 = st.columns(3)
        m1.metric("Detections", len(result["detections"]))
        m2.metric("Text Regions", len(result["ocr_results"]))
        m3.metric("Metadata", "Yes" if result["has_metadata"] else "No")

        # Issues
        if result["reasons"]:
            st.subheader("Issues Found")
            for reason in result["reasons"]:
                st.warning(f"• {reason}")

        # OCR results
        if result["ocr_results"]:
            with st.expander("Text extracted from image"):
                for item in result["ocr_results"]:
                    conf = item["confidence"]
                    if isinstance(conf, float):
                        st.write(f"• `{item['text']}` ({conf:.0%} confidence)")
                    else:
                        st.write(f"• `{item['text']}`")

        # Metadata
        if result["has_metadata"]:
            with st.expander("EXIF Metadata detected"):
                st.write("This image contains hidden metadata which may include:")
                st.write("• GPS location coordinates")
                st.write("• Device make and model")
                st.write("• Date and time taken")

                # Download clean version
                clean_path = tmp_path + "_clean.jpg"
                strip_metadata(tmp_path, clean_path)
                with open(clean_path, "rb") as f:
                    st.download_button(
                        label="⬇️ Download metadata-stripped version",
                        data=f,
                        file_name="clean_" + uploaded_file.name,
                        mime="image/jpeg"
                    )
                os.unlink(clean_path)

    # Cleanup
    os.unlink(tmp_path)