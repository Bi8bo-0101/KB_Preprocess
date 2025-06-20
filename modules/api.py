# modules/api.py
import os
from requests_toolbelt.multipart.encoder import MultipartEncoder
import requests
import json

# 可配置 API 参数（如后续加入 config.yaml，可从中读取）
DIFY_API_URL = "https://dify.medicalunion.cn/v1/workflows/run"
DIFY_API_KEY = "app-PqDDjiDo6tX8VmleHzAGJSd8"
DIFY_UPLOAD_URL = "https://dify.medicalunion.cn/v1/files/upload"
DIFY_USER = "ocr-user"

def upload_file_to_dify(image_path: str):
    """上传图片到 Dify 文件接口，返回 file_id"""
    if not os.path.exists(image_path):
        print(f"[上传失败] 路径不存在: {image_path}")
        return None

    m = MultipartEncoder(
        fields={
            "file": ("image.png", open(image_path, "rb"), "image/png"),
            "user": DIFY_USER
        }
    )
    headers = {
        "Authorization": f"Bearer {DIFY_API_KEY}",
        "Content-Type": m.content_type
    }
    response = requests.post(DIFY_UPLOAD_URL, headers=headers, data=m)

    if response.status_code in (200, 201):
        file_id = response.json().get("id")
        print(f"[上传成功] 文件 ID: {file_id}")
        return file_id
    else:
        print(f"[UPLOAD ERROR] 状态码: {response.status_code}, 响应: {response.text}")
        return None

def get_image_description_dify(image_path: str) -> str:
    """调用大模型对图片进行描述"""
    file_id = upload_file_to_dify(image_path)
    if not file_id:
        return "上传失败，未获取文件 ID"

    headers = {
        "Authorization": f"Bearer {DIFY_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "inputs": {
            "file": [
                {
                    "transfer_method": "local_file",
                    "upload_file_id": file_id,
                    "type": "image"
                }
            ]
        },
        "response_mode": "blocking",
        "user": DIFY_USER
    }

    response = requests.post(DIFY_API_URL, headers=headers, data=json.dumps(payload))

    if response.status_code != 200:
        print(f"[DIFY ERROR] 状态码: {response.status_code}, 响应: {response.text}")
        return "调用失败：" + response.text

    try:
        response_json = response.json()
        text = response_json.get("data", {}).get("outputs", {}).get("text", "")
        return text.strip() if isinstance(text, str) else "未能识别"
    except Exception as e:
        print(f"[解析失败] 错误: {e}")
        return "未能识别"