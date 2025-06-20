# 📄 文档结构化识别与图像理解接口系统

本项目基于 FastAPI、PaddleOCR 和 Dify 多模态模型，提供一个用于文档结构识别与图像理解的接口系统，支持 PDF、Word、图片文件上传，输出结构化 JSON 和 Markdown 格式内容，适用于知识提取、归档整理、辅助理解等场景。

---

## 接口说明

### `POST /process-structured/`

文档上传识别接口。

#### 请求参数

| 参数名  | 类型   | 是否必填 | 说明                 |
|------|------|------|--------------------|
| file | file | ✅ 是  | 上传的 PDF、Word、图片等文件 |

#### 请求示例

```bash
curl -X POST http://localhost:1408/process-structured/ \
  -F "file=@/path/to/your/file.pdf"
```

#### 安装依赖
```bash
pip install -r requirements.txt
```

#### 运行命令
```bash
uvicorn ocr2:app --host 0.0.0.0 --port 1408
```

#### 输入文件夹
```
./uploaded_file
```

#### 输出文件夹
```
./md_outputs
```