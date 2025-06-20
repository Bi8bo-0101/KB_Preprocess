import os
import json
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder

from .api import DIFY_API_URL, DIFY_API_KEY

def upload_file_to_dify(image_path):
    m = MultipartEncoder(
        fields={
            "file": (os.path.basename(image_path), open(image_path, "rb"), "image/png"),
            "user": "ocr-user"
        }
    )

    headers = {
        "Authorization": f"Bearer {DIFY_API_KEY}",
        "Content-Type": m.content_type
    }

    response = requests.post("https://dify.medicalunion.cn/v1/files/upload", headers=headers, data=m)
    if response.status_code in (200, 201):
        file_id = response.json().get("id")
        print(f"[上传成功] 文件 ID: {file_id}")
        return file_id
    else:
        print(f"[UPLOAD ERROR] 状态码: {response.status_code}, 响应: {response.text}")
        return None

def get_image_description_dify(image_path):
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
        "user": "ocr-user"
    }

    response = requests.post(DIFY_API_URL, headers=headers, data=json.dumps(payload))

    if response.status_code != 200:
        print(f"[DIFY ERROR] 状态码: {response.status_code}, 响应: {response.text}")
        return "调用失败：" + response.text

    response_json = response.json()
    print("[DEBUG] 模型完整响应：", json.dumps(response_json, ensure_ascii=False, indent=2))
    text = ""
    try:
        text = response_json.get("data", {}).get("outputs", {}).get("text", "")
    except Exception as e:
        print(f"[解析错误] 无法提取 text 字段：{e}")
    text = text.strip() if isinstance(text, str) else ""
    return text if text else "未能识别"