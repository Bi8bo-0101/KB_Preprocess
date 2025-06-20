import os
import tempfile
import shutil
from docx2pdf import convert as docx2pdf_convert
from pdf2image import convert_from_path, pdfinfo_from_path
import numpy as np
from modules.ocr import run_ocr
from modules.LLMTrans import get_image_description_dify
from modules.file_utils import save_crop_image
from PIL import Image


def process_word(file_path: str, output_dir: str) -> str:
    """
    将 Word 文件转换为 Markdown 格式。
    """
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    file_output_dir = os.path.join(output_dir, base_name)
    os.makedirs(file_output_dir, exist_ok=True)

    # 临时转换为 PDF 以提取页面图像
    temp_pdf_dir = tempfile.mkdtemp()
    pdf_output_path = os.path.join(temp_pdf_dir, f"{base_name}.pdf")
    docx2pdf_convert(file_path, pdf_output_path)

    data = []
    num_pages = pdfinfo_from_path(pdf_output_path)["Pages"]
    for page_num in range(num_pages):
        print(f"[Word->PDF] 正在处理第 {page_num+1}/{num_pages} 页")
        page_image = convert_from_path(pdf_output_path, first_page=page_num+1, last_page=page_num+1)[0]
        image_np = np.array(page_image)
        result = run_ocr(image_np)

        for idx, item in enumerate(result):
            block_type = item['type']
            bbox = item['bbox']
            if block_type == 'text':
                text_content = ' '.join([res['text'] for res in item['res']])
                data.append({
                    '页面': page_num + 1,
                    '类型': 'text',
                    '内容': text_content
                })
            elif block_type in ['table', 'figure']:
                crop_path = os.path.join(file_output_dir, f"{block_type}_wordpage{page_num+1}_{idx}.png")
                saved_path = save_crop_image(page_image, bbox, crop_path)
                if saved_path:
                    description = get_image_description_dify(saved_path)
                    data.append({
                        '页面': page_num + 1,
                        '类型': block_type,
                        '截图路径': saved_path,
                        '识别描述': description
                    })

        del page_image
        del image_np

    shutil.rmtree(temp_pdf_dir)

    # 生成 Markdown
    md_output_dir = os.path.join("./md_outputs", base_name)
    os.makedirs(md_output_dir, exist_ok=True)
    md_output_path = os.path.join(md_output_dir, f"{base_name}.md")

    md_lines = []
    for item in data:
        block_type = item.get("类型", "")
        section = []

        desc = item.get("识别描述", "").strip()
        if desc:
            section.append(desc)

        if block_type == "text":
            content = item.get("内容", "").strip()
            if content:
                section.append(content)

        if section:
            md_lines.extend(section)
            md_lines.append("\n---\n")

    with open(md_output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    print(f"[输出] Markdown 文件已生成: {md_output_path}")
    return md_output_path