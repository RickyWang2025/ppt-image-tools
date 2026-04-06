"""抠图API路由"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import Response
from PIL import Image
from loguru import logger
from typing import Optional

from app.services.remove_bg_service import remove_bg_service
from app.utils.image_utils import save_upload_file, save_output_image, image_to_bytes

router = APIRouter()


@router.post("/")
async def remove_background(
    file: UploadFile = File(..., description="要处理的图片"),
    model: str = Form("u2net", description="抠图模型"),
    bgcolor: Optional[str] = Form(None, description="替换背景颜色，格式: R,G,B 如 255,255,255")
):
    """
    智能抠图/背景移除

    - **model**: 抠图模型选择
        - u2net: 通用场景，平衡质量和速度
        - u2netp: 轻量版，速度最快
        - u2net_human_seg: 人像专用
        - isnet-general-use: 高质量通用
    - **bgcolor**: 替换背景颜色，如 "255,255,255" 表示白色背景
    """
    try:
        # 读取图片
        _, image = await save_upload_file(file)

        # 解析背景颜色
        bg_color = None
        if bgcolor:
            try:
                bg_color = tuple(int(c.strip()) for c in bgcolor.split(","))
                if len(bg_color) != 3:
                    raise ValueError("颜色格式错误")
            except:
                raise HTTPException(status_code=400, detail="bgcolor格式错误，应为 R,G,B 格式")

        # 执行抠图
        result = remove_bg_service.remove_background(
            image,
            model=model,
            bgcolor=bg_color
        )

        # 返回结果
        url, _ = save_output_image(result)

        return {
            "success": True,
            "model": model,
            "has_transparency": result.mode == "RGBA",
            "url": url
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"抠图失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/download")
async def remove_bg_download(
    file: UploadFile = File(...),
    model: str = Form("u2net"),
    bgcolor: Optional[str] = Form(None)
):
    """抠图并直接返回PNG文件"""
    try:
        _, image = await save_upload_file(file)

        bg_color = None
        if bgcolor:
            bg_color = tuple(int(c.strip()) for c in bgcolor.split(","))

        result = remove_bg_service.remove_background(image, model, bgcolor=bg_color)

        img_bytes = image_to_bytes(result, "PNG")

        return Response(
            content=img_bytes,
            media_type="image/png",
            headers={
                "Content-Disposition": "attachment; filename=removed_bg.png"
            }
        )

    except Exception as e:
        logger.error(f"抠图失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models")
async def list_models():
    """列出可用的抠图模型"""
    models = remove_bg_service.get_available_models()
    return {
        "models": [
            {"name": k, "description": v}
            for k, v in models.items()
        ]
    }