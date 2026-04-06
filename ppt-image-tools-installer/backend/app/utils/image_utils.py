"""公共工具函数"""
import uuid
import aiofiles
from pathlib import Path
from PIL import Image
from fastapi import UploadFile
from io import BytesIO
from typing import Tuple

# 目录配置
TEMP_DIR = Path(__file__).resolve().parent.parent.parent / "temp"
OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "outputs"


def generate_filename(extension: str = "png") -> str:
    """生成唯一文件名"""
    return f"{uuid.uuid4().hex}.{extension}"


async def save_upload_file(upload_file: UploadFile) -> Tuple[Path, Image.Image]:
    """
    保存上传文件并返回路径和PIL图片对象

    Returns:
        (文件路径, PIL图片对象)
    """
    # 读取文件内容
    content = await upload_file.read()

    # 解析图片
    image = Image.open(BytesIO(content))

    # 生成保存路径
    ext = upload_file.filename.split(".")[-1] if "." in upload_file.filename else "png"
    if ext.lower() not in ["png", "jpg", "jpeg", "webp", "bmp"]:
        ext = "png"

    filename = generate_filename(ext)
    filepath = TEMP_DIR / filename

    # 保存文件
    async with aiofiles.open(filepath, "wb") as f:
        await f.write(content)

    return filepath, image


def save_output_image(image: Image.Image, format: str = "PNG") -> Tuple[str, Path]:
    """
    保存输出图片

    Returns:
        (文件URL路径, 文件系统路径)
    """
    ext = "png" if format.upper() == "PNG" else "jpg"
    filename = generate_filename(ext)
    filepath = OUTPUT_DIR / filename

    # 保存
    if format.upper() == "JPEG":
        image = image.convert("RGB")
        image.save(filepath, "JPEG", quality=95)
    else:
        image.save(filepath, format)

    return f"/outputs/{filename}", filepath


def save_output_svg(svg_string: str) -> Tuple[str, Path]:
    """保存SVG文件"""
    filename = generate_filename("svg")
    filepath = OUTPUT_DIR / filename

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(svg_string)

    return f"/outputs/{filename}", filepath


def image_to_bytes(image: Image.Image, format: str = "PNG") -> bytes:
    """图片转bytes"""
    buffer = BytesIO()
    if format.upper() == "JPEG":
        image = image.convert("RGB")
    image.save(buffer, format=format)
    return buffer.getvalue()


def cleanup_old_files(directory: Path, max_age_hours: int = 24):
    """清理过期临时文件"""
    import time

    now = time.time()
    max_age_seconds = max_age_hours * 3600

    for file in directory.iterdir():
        if file.is_file():
            if now - file.stat().st_mtime > max_age_seconds:
                file.unlink()