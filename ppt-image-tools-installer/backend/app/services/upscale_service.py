"""图片放大服务 - Real-ESRGAN"""
import os
from pathlib import Path
from typing import Optional
import numpy as np
from PIL import Image
from loguru import logger

# 模型目录
MODELS_DIR = Path(__file__).resolve().parent.parent.parent / "models"

class UpscaleService:
    """Real-ESRGAN 图片放大服务"""

    def __init__(self):
        self.model = None
        self.model_name = "RealESRGAN_x4plus"
        self.device = "cpu"

    def _load_model(self):
        """懒加载模型"""
        if self.model is not None:
            return

        try:
            from basicsr.archs.rrdbnet_arch import RRDBNet
            from realesrgan import RealESRGANer

            # 模型配置
            model_path = MODELS_DIR / f"{self.model_name}.pth"

            # 如果模型不存在，会自动下载
            if not model_path.exists():
                logger.info(f"模型不存在，将自动下载: {self.model_name}")

            # 初始化网络
            model = RRDBNet(
                num_in_ch=3,
                num_out_ch=3,
                num_feat=64,
                num_block=23,
                num_grow_ch=32,
                scale=4
            )

            # 检测GPU
            try:
                import torch
                if torch.cuda.is_available():
                    self.device = "cuda"
                    logger.info("检测到GPU，使用CUDA加速")
            except:
                pass

            # 创建推理器
            self.model = RealESRGANer(
                scale=4,
                model_path=str(model_path) if model_path.exists() else None,
                model=model,
                tile=0,  # 0表示不分割，适合大显存
                tile_pad=10,
                pre_pad=0,
                half=False,  # FP16可能有问题，保持FP32
                device=self.device
            )

            logger.info(f"Real-ESRGAN模型加载完成，设备: {self.device}")

        except Exception as e:
            logger.error(f"模型加载失败: {e}")
            raise

    def upscale(
        self,
        image: Image.Image,
        scale: int = 2,
        model_type: str = "general"
    ) -> Image.Image:
        """
        图片放大

        Args:
            image: 输入图片
            scale: 放大倍数 (2 或 4)
            model_type: 模型类型 (general/anime)

        Returns:
            放大后的图片
        """
        self._load_model()

        # 转换为numpy数组
        img_array = np.array(image)

        # 确保是RGB格式
        if len(img_array.shape) == 2:
            img_array = np.stack([img_array] * 3, axis=-1)
        elif img_array.shape[-1] == 4:
            img_array = img_array[:, :, :3]

        try:
            # 执行放大
            output, _ = self.model.enhance(img_array, outscale=scale)

            logger.info(f"图片放大完成: {image.size} -> {output.shape[:2]}")

            return Image.fromarray(output)

        except Exception as e:
            logger.error(f"图片放大失败: {e}")
            raise

    def upscale_with_face_enhance(
        self,
        image: Image.Image,
        scale: int = 2
    ) -> Image.Image:
        """
        带人脸增强的放大（适用于人像）
        """
        try:
            from gfpgan import GFPGANer

            self._load_model()

            # 先用Real-ESRGAN放大
            upscaled = self.upscale(image, scale)

            # 加载GFPGAN进行人脸增强
            gfpgan_path = MODELS_DIR / "GFPGANv1.4.pth"
            if not gfpgan_path.exists():
                logger.warning("GFPGAN模型不存在，跳过人脸增强")
                return upscaled

            face_enhancer = GFPGANer(
                model_path=str(gfpgan_path),
                upscale=1,  # 已经放大过了
                arch='clean',
                channel_multiplier=2,
                bg_upsampler=None,
                device=self.device
            )

            # 人脸增强
            _, _, output = face_enhancer.enhance(
                np.array(upscaled),
                has_aligned=False,
                only_center_face=False,
                paste_back=True
            )

            logger.info("人脸增强完成")
            return Image.fromarray(output)

        except ImportError:
            logger.warning("GFPGAN未安装，使用普通放大")
            return self.upscale(image, scale)
        except Exception as e:
            logger.warning(f"人脸增强失败: {e}，返回普通放大结果")
            return self.upscale(image, scale)


# 单例
upscale_service = UpscaleService()