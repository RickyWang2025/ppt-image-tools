"""抠图服务 - rembg"""
import numpy as np
from PIL import Image
from loguru import logger
from typing import Optional

class RemoveBgService:
    """背景移除服务"""

    # 支持的模型
    MODELS = {
        "u2net": "通用场景，平衡质量和速度",
        "u2netp": "轻量版，速度最快",
        "u2net_human_seg": "人像专用",
        "u2net_cloth_seg": "服装分割",
        "isnet-general-use": "高质量通用",
        "sam": "Segment Anything Model（需额外安装）"
    }

    def __init__(self):
        self._session = None

    def _get_session(self, model: str = "u2net"):
        """获取模型会话"""
        from rembg import new_session
        if self._session is None or self._session.model_name != model:
            self._session = new_session(model)
            logger.info(f"加载rembg模型: {model}")
        return self._session

    def remove_background(
        self,
        image: Image.Image,
        model: str = "u2net",
        alpha_matting: bool = False,
        bgcolor: Optional[tuple] = None
    ) -> Image.Image:
        """
        移除背景

        Args:
            image: 输入图片
            model: 模型名称
            alpha_matting: 是否使用alpha matting优化边缘
            bgcolor: 替换背景颜色 (R, G, B)，None表示透明

        Returns:
            去背景后的图片
        """
        from rembg import remove

        # 转换图片格式
        if image.mode != "RGB":
            image = image.convert("RGB")

        try:
            # 执行抠图
            session = self._get_session(model)
            output = remove(
                image,
                session=session,
                alpha_matting=alpha_matting,
                alpha_matting_foreground_threshold=240,
                alpha_matting_background_threshold=10,
                alpha_matting_erode_size=10
            )

            # 替换背景颜色
            if bgcolor and output.mode == "RGBA":
                background = Image.new("RGBA", output.size, (*bgcolor, 255))
                output = Image.alpha_composite(background, output)

            logger.info(f"抠图完成: {model}")
            return output

        except Exception as e:
            logger.error(f"抠图失败: {e}")
            raise

    def remove_background_simple(self, image: Image.Image) -> Image.Image:
        """简单抠图（使用默认模型）"""
        from rembg import remove
        return remove(image)

    def get_available_models(self) -> dict:
        """获取可用模型列表"""
        return self.MODELS


# 单例
remove_bg_service = RemoveBgService()