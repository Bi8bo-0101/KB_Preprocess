import numpy as np
from paddleocr import PPStructureV3
from PIL import Image

def run_ocr(image: Image.Image):
    ocr_engine = PPStructureV3(layout=True, show_log=True)
    image_np = np.array(image)
    result = ocr_engine(image_np)
    result.sort(key=lambda x: (x.get("bbox", [0, 0, 0, 0])[1], x.get("bbox", [0, 0, 0, 0])[0]))
    return result