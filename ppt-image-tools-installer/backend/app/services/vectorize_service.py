"""图片矢量化服务 - vtracer"""
import numpy as np
from PIL import Image
from loguru import logger
from typing import Optional
import io

class VectorizeService:
    """图片矢量化服务"""

    # 预设配置
    PRESETS = {
        "color": {"color_mode": "color", "hierarchical": "stacked"},
        "bw": {"color_mode": "bw", "hierarchical": "stacked"},
        "posterized": {"color_mode": "color", "filter_speckle": 4, "color_precision": 6},
        "detailed": {"color_mode": "color", "layer_difference": 8, "mode": "spline"},
        "simple": {"color_mode": "color", "filter_speckle": 16, "corner_threshold": 60}
    }

    def __init__(self):
        pass

    def vectorize(
        self,
        image: Image.Image,
        color_mode: str = "color",
        hierarchical: str = "stacked",
        mode: str = "spline",
        filter_speckle: int = 4,
        color_precision: int = 8,
        layer_difference: int = 16,
        corner_threshold: int = 60,
        corner_rounding: float = 0.7,
        optimization_precision: float = 5.0,
        preset: Optional[str] = None
    ) -> str:
        """
        将图片转换为SVG矢量图

        Args:
            image: 输入图片
            color_mode: 颜色模式 ("color" 或 "bw")
            hierarchical: 层级模式 ("stacked" 或 "cutout")
            mode: 曲线模式 ("spline" 或 "polygon")
            filter_speckle: 斑点过滤阈值
            color_precision: 颜色精度
            layer_difference: 层差异
            corner_threshold: 角落阈值
            corner_rounding: 角落圆滑度
            optimization_precision: 优化精度
            preset: 预设名称，覆盖其他参数

        Returns:
            SVG字符串
        """
        try:
            import vtracer
        except ImportError:
            # 后备方案：使用potrace（仅黑白）
            if color_mode == "bw":
                return self._vectorize_potrace(image)
            raise ImportError("请安装vtracer: pip install vtracer")

        # 应用预设
        if preset and preset in self.PRESETS:
            params = self.PRESETS[preset]
            color_mode = params.get("color_mode", color_mode)
            hierarchical = params.get("hierarchical", hierarchical)
            mode = params.get("mode", mode)
            filter_speckle = params.get("filter_speckle", filter_speckle)
            color_precision = params.get("color_precision", color_precision)
            layer_difference = params.get("layer_difference", layer_difference)
            corner_threshold = params.get("corner_threshold", corner_threshold)

        # 转换图片
        if image.mode == "RGBA":
            # 处理透明通道
            background = Image.new("RGB", image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[3])
            image = background
        elif image.mode != "RGB":
            image = image.convert("RGB")

        # 转换为numpy数组
        img_array = np.array(image)

        try:
            # 执行矢量化
            svg_string = vtracer.convert_pixels_to_svg(
                img_array,
                color_mode=color_mode,
                hierarchical=hierarchical,
                mode=mode,
                filter_speckle=filter_speckle,
                color_precision=color_precision,
                layer_difference=layer_difference,
                corner_threshold=corner_threshold,
                corner_rounding=corner_rounding,
                optimization_precision=optimization_precision
            )

            logger.info(f"矢量化完成: {image.size}, 模式: {color_mode}")
            return svg_string

        except Exception as e:
            logger.error(f"矢量化失败: {e}")
            raise

    def _vectorize_potrace(self, image: Image.Image) -> str:
        """使用potrace进行黑白矢量化（后备方案）"""
        import subprocess
        import tempfile

        # 转换为黑白
        if image.mode != "L":
            image = image.convert("L")

        # 二值化
        image = image.point(lambda x: 255 if x > 128 else 0)

        # 保存临时BMP文件
        with tempfile.NamedTemporaryFile(suffix=".bmp", delete=False) as f:
            bmp_path = f.name
            image.save(bmp_path)

        # 调用potrace
        svg_path = bmp_path.replace(".bmp", ".svg")

        try:
            subprocess.run(
                ["potrace", "-s", "-o", svg_path, bmp_path],
                check=True,
                capture_output=True
            )

            with open(svg_path, "r") as f:
                svg_string = f.read()

            logger.info("Potrace矢量化完成")
            return svg_string

        except FileNotFoundError:
            raise ImportError("potrace未安装，请安装: apt install potrace 或 brew install potrace")
        finally:
            # 清理临时文件
            import os
            if os.path.exists(bmp_path):
                os.remove(bmp_path)
            if os.path.exists(svg_path):
                os.remove(svg_path)

    def vectorize_text(
        self,
        image: Image.Image,
        threshold: int = 128
    ) -> str:
        """
        文字矢量化专用（优化参数）
        """
        return self.vectorize(
            image,
            color_mode="bw",
            hierarchical="stacked",
            mode="spline",
            filter_speckle=2,
            corner_threshold=80,
            corner_rounding=0.5,
            optimization_precision=2.0
        )

    def optimize_svg(self, svg_string: str) -> str:
        """
        优化SVG文件大小
        """
        try:
            import subprocess
            import tempfile

            with tempfile.NamedTemporaryFile(mode="w", suffix=".svg", delete=False) as f:
                f.write(svg_string)
                svg_path = f.name

            output_path = svg_path.replace(".svg", "_opt.svg")

            subprocess.run(
                ["scour", "-i", svg_path, "-o", output_path],
                check=True,
                capture_output=True
            )

            with open(output_path, "r") as f:
                optimized = f.read()

            # 清理
            import os
            os.remove(svg_path)
            os.remove(output_path)

            logger.info("SVG优化完成")
            return optimized

        except (ImportError, FileNotFoundError):
            logger.warning("scour未安装，跳过优化")
            return svg_string


# 单例
vectorize_service = VectorizeService()