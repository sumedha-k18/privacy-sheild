from PIL import Image
from PIL.ExifTags import TAGS

def read_exif(image_path):
    image = Image.open(image_path)
    exif_data = image._getexif()
    if not exif_data:
        return {}
    readable = {}
    for tag_id, value in exif_data.items():
        tag = TAGS.get(tag_id, tag_id)
        readable[tag] = value
    return readable

def strip_metadata(image_path, output_path):
    image = Image.open(image_path)
    clean = Image.new(image.mode, image.size)
    clean.putdata(list(image.get_flattened_data()))
    clean.save(output_path)

if __name__ == "__main__":
    print(read_exif("C:/Privacy-Shield/METAA.jpg"))
    strip_metadata("C:/Privacy-Shield/METAA.jpg", "C:/Privacy-Shield/test_clean.jpg")
    print(read_exif("C:/Privacy-Shield/test_clean.jpg"))