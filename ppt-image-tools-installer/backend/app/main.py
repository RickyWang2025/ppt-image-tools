"""
PPT图片处理工具 - FastAPI后端
"""
import os
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger

# 配置日志
logger.add("logs/app.log", rotation="10 MB", retention="7 days")

# 获取基础目录
BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"
TEMP_DIR = BASE_DIR / "temp"
OUTPUT_DIR = BASE_DIR / "outputs"

# 查找插件目录（可能在同级或上级）
ADDON_DIR = None
for candidate in [
    BASE_DIR.parent / "addon",  # 安装后的结构
    BASE_DIR / "addon",  # 开发时的结构
]:
    if candidate.exists():
        ADDON_DIR = candidate
        break

# 创建必要目录
for d in [MODELS_DIR, TEMP_DIR, OUTPUT_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# 创建FastAPI应用
app = FastAPI(
    title="PPT图片处理工具 API",
    description="图片放大、抠图、擦除、矢量化",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS配置（允许PPT插件访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务
app.mount("/outputs", StaticFiles(directory=str(OUTPUT_DIR)), name="outputs")

if ADDON_DIR:
    app.mount("/static", StaticFiles(directory=str(ADDON_DIR)), name="static")
    logger.info(f"插件目录: {ADDON_DIR}")

# 注册路由
from app.routers import upscale, remove_bg, inpaint, vectorize

app.include_router(upscale.router, prefix="/api/upscale", tags=["图片放大"])
app.include_router(remove_bg.router, prefix="/api/remove-bg", tags=["抠图"])
app.include_router(inpaint.router, prefix="/api/inpaint", tags=["物体擦除"])
app.include_router(vectorize.router, prefix="/api/vectorize", tags=["矢量化"])


@app.get("/")
async def root():
    return {
        "name": "PPT图片处理工具 API",
        "version": "1.0.0",
        "endpoints": {
            "upscale": "/api/upscale",
            "remove_bg": "/api/remove-bg",
            "inpaint": "/api/inpaint",
            "vectorize": "/api/vectorize"
        }
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)