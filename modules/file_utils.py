import os
from PIL import Image


def save_crop_image(image, bbox, save_path):
    if not isinstance(bbox, (list, tuple)):
        print(f"[WARNING] bbox 不是列表格式: {bbox}，跳过截图")
        return None
    if not bbox or len(bbox) < 4:
        print(f"[WARNING] 无效的 bbox: {bbox}，跳过截图")
        return None
    if isinstance(bbox[0], (list, tuple)):
        x_min = min([point[0] for point in bbox])
        y_min = min([point[1] for point in bbox])
        x_max = max([point[0] for point in bbox])
        y_max = max([point[1] for point in bbox])
    else:
        x_min, y_min, x_max, y_max = bbox

    cropped_image = image.crop((x_min, y_min, x_max, y_max))
    cropped_image.save(save_path)
    return save_path


# def save_crop_image(image, bbox, save_path):
#     return save_crop(image, bbox, save_path)


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def init_dirs(*dirs):
    for d in dirs:
        os.makedirs(d, exist_ok=True)
    return dirs[-1] if dirs else None


def get_upload_path(base_name, filename):
    upload_dir = os.path.join("./uploaded_files", base_name)
    os.makedirs(upload_dir, exist_ok=True)
    return os.path.join(upload_dir, filename)


def get_md_output_path(base_name):
    md_output_dir = os.path.join("./md_outputs", base_name)
    os.makedirs(md_output_dir, exist_ok=True)
    md_output_path = os.path.join(md_output_dir, f"{base_name}.md")
    return md_output_path