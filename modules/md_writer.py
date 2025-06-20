import os

def write_markdown(md_output_dir: str, base_name: str, data: list):
    os.makedirs(md_output_dir, exist_ok=True)
    md_output_path = os.path.join(md_output_dir, f"{base_name}.md")

    md_lines = []
    for item in data:
        page = item.get("页面", "?")
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

    if md_lines:
        with open(md_output_path, "w", encoding="utf-8") as f_md:
            f_md.write("\n".join(md_lines))
        print(f"[输出] Markdown 文件已生成: {md_output_path}")

    return md_output_path