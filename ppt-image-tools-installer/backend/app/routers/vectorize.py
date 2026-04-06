"""图片矢量化API路由"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import Response
from PIL import Image
from loguru import logger
from typing import Optional

from app.services.vectorize_service import vectorize_service
from app.utils.image_utils import save_upload_file, save_output_svg

router = APIRouter()


@router.post("/")
async def vectorize_image(
    file: UploadFile = File(..., description="要矢量化的图片"),
    preset: Optional[str] = Form(None, description="预设配置"),
    color_mode: str = Form("color", description="颜色模式: color 或 bw"),
    filter_speckle: int = Form(4, description="斑点过滤阈值"),
    color_precision: int = Form(8, description="颜色精度"),
    corner_threshold: int = Form(60, description="角落阈值")
):
    """
    图片矢量化（转SVG）

    - **preset**: 预设配置，可选值: color, bw, posterized, detailed, simple
    - **color_mode**: 颜色模式
        - color: 彩色
        - bw: 黑白
    - **filter_speckle**: 值越大，去除的小噪点越多
    - **color_precision**: 颜色精度，值越小颜色越少
    - **corner_threshold**: 角落阈值，值越大拐角越锐利
    """
    try:
        # 读取图片
        _, image = await save_upload_file(file)

        # 执行矢量化
        svg_string = vectorize_service.vectorize(
            image,
            color_mode=color_mode,
            filter_speckle=filter_speckle,
            color_precision=color_precision,
            corner_threshold=corner_threshold,
            preset=preset
        )

        # 保存并返回
        url, _ = save_output_svg(svg_string)

        return {
            "success": True,
            "preset": preset,
            "color_mode": color_mode,
            "url": url,
            "svg_length": len(svg_string)
        }

    except Exception as e:
        logger.error(f"矢量化失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/download")
async def vectorize_download(
    file: UploadFile = File(...),
    preset: Optional[str] = Form(None),
    color_mode: str = Form("color")
):
    """矢量化并直接返回SVG文件"""
    try:
        _, image = await save_upload_file(file)

        svg_string = vectorize_service.vectorize(
            image,
            color_mode=color_mode,
            preset=preset
        )

        return Response(
            content=svg_string.encode("utf-8"),
            media_type="image/svg+xml",
            headers={
                "Content-Disposition": "attachment; filename=vectorized.svg"
            }
        )

    except Exception as e:
        logger.error(f"矢量化失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/text")
async def vectorize_text(
    file: UploadFile = File(..., description="包含文字的图片")
):
    """
    文字矢量化专用

    针对文字图片优化的参数，输出黑白矢量
    """
    try:
        _, image = await save_upload_file(file)

        svg_string = vectorize_service.vectorize_text(image)

        url, _ = save_output_svg(svg_string)

        return {
            "success": True,
            "mode": "text_optimized",
            "url": url
        }

    except Exception as e:
        logger.error(f"文字矢量化失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/presets")
async def list_presets():
    """列出可用的预设配置"""
    return {
        "presets": [
            {
                "name": "color",
                "description": "彩色模式，适合照片和插图",
                "color_mode": "color"
            },
            {
                "name": "bw",
                "description": "黑白模式，适合线条和文字",
                "color_mode": "bw"
            },
            {
                "name": "posterized",
                "description": "海报风格，颜色更少更鲜艳",
                "color_mode": "color"
            },
            {
                "name": "detailed",
                "description": "细节优先，适合复杂图像",
                "color_mode": "color"
            },
            {
                "name": "simple",
                "description": "简洁风格，适合简单图形",
                "color_mode": "color"
            }
        ]
    }