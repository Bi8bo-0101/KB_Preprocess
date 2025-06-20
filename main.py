from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import os
from modules.pdf2md import process_pdf
from modules.doc2md import process_word
from PIL import Image
from paddleocr import PPStructureV3
import numpy as np
from pdf2image import convert_from_path, pdfinfo_from_path
from modules.file_utils import init_dirs

app = FastAPI()
UPLOAD_DIR = "./uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/process-structured/")
async def process_structured(file: UploadFile = File(...)):
    base_name = os.path.splitext(file.filename)[0]
    file_dir = init_dirs(UPLOAD_DIR, base_name)
    file_path = os.path.join(file_dir, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    result_data = []

    if file.filename.lower().endswith(".pdf"):
        result_data = process_pdf(file_path, file_dir)
    elif file.filename.lower().endswith((".doc", ".docx")):
        result_data = process_word(file_path, file_dir)
    else:
        # 默认处理为图片
        image = Image.open(file_path)
        image_np = np.array(image)
        ocr = PPStructureV3(layout=True, show_log=True)
        result = ocr(image_np)
        result.sort(key=lambda x: (x.get("bbox", [0, 0, 0, 0])[1], x.get("bbox", [0, 0, 0, 0])[0]))

        from modules.LLMTrans import get_image_description_dify
        for idx, item in enumerate(result):
            block_type = item['type']
            bbox = item['bbox']
            if block_type == 'text':
                content = ' '.join([r['text'] for r in item['res']])
                result_data.append({"类型": "text", "内容": content})
            elif block_type in ['table', 'figure']:
                save_path = os.path.join(file_dir, f"{block_type}_{idx}.png")
                image.crop((bbox[0], bbox[1], bbox[2], bbox[3])).save(save_path)
                description = get_image_description_dify(save_path)
                result_data.append({"类型": block_type, "截图路径": save_path, "识别描述": description})

    return JSONResponse(content={"results": result_data})
