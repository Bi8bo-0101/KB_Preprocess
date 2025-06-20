import os
import numpy as np
from pdf2image import convert_from_path, pdfinfo_from_path
from modules.ocr import run_ocr
from modules.LLMTrans import get_image_description_dify
from modules.md_writer import write_markdown
from modules.file_utils import save_crop_image, ensure_dir


def process_pdf(file_path: str, output_dir: str) -> str:
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    pdf_image_dir = os.path.join(output_dir, base_name)
    ensure_dir(pdf_image_dir)

    num_pages = pdfinfo_from_path(file_path)["Pages"]
    all_blocks = []

    for page_num in range(num_pages):
        print(f"[PDF] 正在处理第 {page_num + 1}/{num_pages} 页")
        page_image = convert_from_path(file_path, first_page=page_num + 1, last_page=page_num + 1)[0]
        image_np = np.array(page_image)
        blocks = run_ocr(image_np)

        for idx, block in enumerate(blocks):
            btype = block['type']
            item = {"页面": page_num + 1, "类型": btype}

            if btype == 'text':
                item['内容'] = ' '.join([res['text'] for res in block['res']])
            elif btype in ['table', 'figure']:
                crop_path = os.path.join(pdf_image_dir, f"{btype}_page{page_num + 1}_{idx}.png")
                saved = save_crop_image(page_image, block['bbox'], crop_path)
                if saved:
                    item['截图路径'] = crop_path
                    item['识别描述'] = get_image_description_dify(crop_path)

            all_blocks.append(item)

    markdown_text = write_markdown(output_dir, base_name, all_blocks)
    return markdown_text