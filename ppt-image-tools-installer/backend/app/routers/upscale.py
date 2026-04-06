"""图片放大API路由"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import Response
from PIL import Image
from typing import Optional
from loguru import logger

from app.services.upscale_service import upscale_service
from app.utils.image_utils import save_upload_file, save_output_image, image_to_bytes

router = APIRouter()


@router.post("/")
async def upscale_image(
    file: UploadFile = File(..., description="要放大的图片"),
    scale: int = Form(2, description="放大倍数 (2 或 4)"),
    model_type: str = Form("general", description="模型类型: general 或 anime"),
    face_enhance: bool = Form(False, description="是否启用人脸增强")
):
    """
    图片高清放大

    - **scale**: 放大倍数，支持2倍或4倍
    - **model_type**: general为通用模型，anime为动漫专用
    - **face_enhance**: 人像图片建议开启，会进行人脸修复增强
    """
    try:
        # 读取图片
        _, image = await save_upload_file(file)

        # 执行放大
        if face_enhance:
            result = upscale_service.upscale_with_face_enhance(image, scale)
        else:
            result = upscale_service.upscale(image, scale, model_type)

        # 返回结果
        url, _ = save_output_image(result)

        return {
            "success": True,
            "original_size": image.size,
            "output_size": result.size,
            "scale": scale,
            "url": url
        }

    except Exception as e:
        logger.error(f"放大失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/download")
async def upscale_download(
    file: UploadFile = File(...),
    scale: int = Form(2),
    model_type: str = Form("general"),
    face_enhance: bool = Form(False)
):
    """
    放大并直接返回图片文件
    """
    try:
        _, image = await save_upload_file(file)

        if face_enhance:
            result = upscale_service.upscale_with_face_enhance(image, scale)
        else:
            result = upscale_service.upscale(image, scale, model_type)

        # 直接返回图片
        img_bytes = image_to_bytes(result)

        return Response(
            content=img_bytes,
            media_type="image/png",
            headers={
                "Content-Disposition": f"attachment; filename=upscaled_{scale}x.png"
            }
        )

    except Exception as e:
        logger.error(f"放大失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models")
async def list_models():
    """列出可用的放大模型"""
    return {
        "models": [
            {
                "name": "RealESRGAN_x4plus",
                "description": "通用放大模型，适合大多数场景",
                "scale": 4
            },
            {
                "name": "RealESRGAN_x4plus_anime",
                "description": "动漫专用模型",
                "scale": 4
            },
            {
                "name": "GFPGAN",
                "description": "人脸修复增强",
                "scale": 1
            }
        ]
    }