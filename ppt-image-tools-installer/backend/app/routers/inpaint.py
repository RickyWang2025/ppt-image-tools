"""物体擦除/图片修复API路由"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import Response
from PIL import Image
from loguru import logger
from typing import Optional
import json

from app.services.inpaint_service import inpaint_service
from app.utils.image_utils import save_upload_file, save_output_image, image_to_bytes

router = APIRouter()


@router.post("/")
async def inpaint_image(
    file: UploadFile = File(..., description="原始图片"),
    mask: UploadFile = File(..., description="遮罩图片（白色区域为需要擦除的部分）"),
    model: str = Form("lama", description="修复模型")
):
    """
    图片修复/物体擦除

    - **mask**: 遮罩图片，白色区域表示需要修复/擦除的部分
    - **model**: 修复模型
        - lama: LaMa模型，适合大面积修复
        - mat: MAT模型，更高质量
        - cv2: OpenCV传统算法，速度快
    """
    try:
        # 读取图片和遮罩
        _, image = await save_upload_file(file)
        _, mask_image = await save_upload_file(mask)

        # 执行修复
        result = inpaint_service.inpaint(image, mask_image, model)

        # 返回结果
        url, _ = save_output_image(result)

        return {
            "success": True,
            "model": model,
            "url": url
        }

    except Exception as e:
        logger.error(f"修复失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/brush")
async def inpaint_with_brush(
    file: UploadFile = File(..., description="原始图片"),
    points: str = Form(..., description="绘制点坐标JSON数组"),
    brush_size: int = Form(20, description="笔刷大小"),
    model: str = Form("lama", description="修复模型")
):
    """
    通过绘制点进行擦除

    - **points**: JSON格式坐标数组，如 [[x1,y1],[x2,y2],...]
    - **brush_size**: 笔刷大小（像素）
    """
    try:
        # 读取图片
        _, image = await save_upload_file(file)

        # 解析绘制点
        try:
            points_list = json.loads(points)
            points_tuples = [(p[0], p[1]) for p in points_list]
        except:
            raise HTTPException(status_code=400, detail="points格式错误")

        # 创建遮罩
        mask = inpaint_service.create_mask_from_points(
            image.size,
            points_tuples,
            brush_size
        )

        # 执行修复
        result = inpaint_service.inpaint(image, mask, model)

        # 返回结果
        url, _ = save_output_image(result)

        return {
            "success": True,
            "brush_size": brush_size,
            "points_count": len(points_tuples),
            "url": url
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"修复失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auto-watermark")
async def auto_remove_watermark(
    file: UploadFile = File(..., description="包含水印的图片"),
    threshold: float = Form(0.8, description="检测阈值")
):
    """
    自动检测并移除水印

    Note: 效果有限，复杂水印建议使用brush接口手动标注
    """
    try:
        _, image = await save_upload_file(file)

        # 自动检测水印区域
        mask = inpaint_service.auto_detect_watermark(image, threshold)

        # 执行修复
        result = inpaint_service.inpaint(image, mask, "lama")

        url, _ = save_output_image(result)

        return {
            "success": True,
            "url": url,
            "note": "自动检测效果有限，建议复杂场景使用手动标注"
        }

    except Exception as e:
        logger.error(f"水印移除失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models")
async def list_models():
    """列出可用的修复模型"""
    return {
        "models": [
            {"name": k, "description": v}
            for k, v in inpaint_service.MODELS.items()
        ]
    }