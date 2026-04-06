"""图片修复/物体擦除服务 - IOPaint"""
import numpy as np
from PIL import Image
from loguru import logger
from typing import Optional

class InpaintService:
    """图片修复服务"""

    # 支持的模型
    MODELS = {
        "lama": "LaMa - 大面积遮罩修复，速度快",
        "mat": "MAT - 高质量修复",
        "sd1.5": "Stable Diffusion 1.5 - 生成式填充",
        "cv2": "OpenCV Inpaint - 传统算法，速度快"
    }

    def __init__(self):
        self._model = None
        self._device = "cpu"

    def _detect_device(self):
        """检测可用设备"""
        try:
            import torch
            if torch.cuda.is_available():
                self._device = "cuda"
                logger.info("检测到GPU，使用CUDA加速")
        except:
            pass

    def _load_lama(self):
        """加载LaMa模型"""
        if self._model is not None:
            return

        try:
            from iopaint.model.lama import LaMa

            self._detect_device()
            self._model = LaMa(device=self._device)
            logger.info("LaMa模型加载完成")

        except ImportError:
            logger.warning("IOPaint未安装，使用OpenCV后备方案")
            self._model = "cv2"

    def inpaint(
        self,
        image: Image.Image,
        mask: Image.Image,
        model: str = "lama"
    ) -> Image.Image:
        """
        图片修复

        Args:
            image: 原始图片
            mask: 遮罩图片（白色区域为需要修复的部分）
            model: 模型名称

        Returns:
            修复后的图片
        """
        # 确保图片格式正确
        if image.mode != "RGB":
            image = image.convert("RGB")

        # 处理遮罩
        if mask.mode != "L":
            mask = mask.convert("L")

        # 转换为numpy数组
        img_array = np.array(image)
        mask_array = np.array(mask)

        # 确保遮罩是二值图
        mask_array = (mask_array > 127).astype(np.uint8) * 255

        if model == "cv2" or model not in self.MODELS:
            return self._inpaint_cv2(img_array, mask_array)

        try:
            # 加载模型
            if self._model is None or isinstance(self._model, str):
                self._load_lama()

            if isinstance(self._model, str):
                return self._inpaint_cv2(img_array, mask_array)

            # 执行修复
            result = self._model(img_array, mask_array)

            logger.info(f"图片修复完成: {model}")
            return Image.fromarray(result)

        except Exception as e:
            logger.warning(f"AI修复失败: {e}，使用OpenCV后备")
            return self._inpaint_cv2(img_array, mask_array)

    def _inpaint_cv2(self, image: np.ndarray, mask: np.ndarray) -> Image.Image:
        """OpenCV修复（后备方案）"""
        import cv2

        result = cv2.inpaint(
            image,
            mask,
            inpaintRadius=3,
            flags=cv2.INPAINT_TELEA
        )

        logger.info("OpenCV修复完成")
        return Image.fromarray(result)

    def create_mask_from_points(
        self,
        image_size: tuple,
        points: list,
        brush_size: int = 20
    ) -> Image.Image:
        """
        从点击/绘制点创建遮罩

        Args:
            image_size: (width, height)
            points: [(x1, y1), (x2, y2), ...] 绘制路径
            brush_size: 笔刷大小

        Returns:
            遮罩图片
        """
        import cv2

        mask = np.zeros((image_size[1], image_size[0]), dtype=np.uint8)

        for i in range(len(points) - 1):
            cv2.line(
                mask,
                points[i],
                points[i + 1],
                255,
                brush_size
            )

        # 最后一个点也画上
        if points:
            cv2.circle(mask, points[-1], brush_size // 2, 255, -1)

        return Image.fromarray(mask)

    def auto_detect_watermark(
        self,
        image: Image.Image,
        threshold: float = 0.8
    ) -> Image.Image:
        """
        自动检测水印区域（简单实现）

        Note: 复杂场景建议手动标注遮罩
        """
        import cv2

        img_array = np.array(image.convert("RGB"))
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

        # 使用边缘检测找水印
        edges = cv2.Canny(gray, 50, 150)

        # 膨胀操作
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.dilate(edges, kernel, iterations=2)

        logger.info("自动检测水印完成")
        return Image.fromarray(mask)


# 单例
inpaint_service = InpaintService()