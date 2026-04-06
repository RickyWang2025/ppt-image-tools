# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller 打包配置文件
使用方法: pyinstaller ppt-tools.spec
"""

import sys
from pathlib import Path

block_cipher = None

# 基础路径
backend_dir = Path('backend')
app_dir = backend_dir / 'app'

a = Analysis(
    [str(backend_dir / 'app' / 'main.py')],
    pathex=[],
    binaries=[],
    datas=[
        (str(backend_dir / 'app' / 'routers'), 'app/routers'),
        (str(backend_dir / 'app' / 'services'), 'app/services'),
        (str(backend_dir / 'app' / 'utils'), 'app/utils'),
        ('addon', 'addon'),
    ],
    hiddenimports=[
        'uvicorn.logging',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'fastapi',
        'fastapi.middleware.cors',
        'fastapi.staticfiles',
        'loguru',
        'PIL',
        'PIL.Image',
        'numpy',
        'rembg',
        'rembg.bg',
        'cv2',
        'onnxruntime',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'pandas'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PPT图片工具',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',  # 如果有图标
)