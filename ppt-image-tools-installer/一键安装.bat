@echo off
chcp 65001 >nul
title PPT图片处理工具 - 一键安装

echo.
echo ╔══════════════════════════════════════════╗
echo ║     PPT图片处理工具 - 一键安装           ║
echo ╚══════════════════════════════════════════╝
echo.

:: 设置安装目录
set "INSTALL_DIR=%LOCALAPPDATA%\PPTImageTools"
set "ADDON_DIR=%INSTALL_DIR%\addon"

:: 检查Python
echo [检查] Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [错误] 未检测到Python！
    echo.
    echo 请先安装Python 3.9或更高版本
    echo 下载地址: https://www.python.org/downloads/
    echo.
    echo 安装Python时请勾选 "Add Python to PATH"
    echo.
    pause
    exit /b 1
)
echo        √ Python已安装

:: 创建目录
echo.
echo [安装] 创建程序目录...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
if not exist "%INSTALL_DIR%\backend" mkdir "%INSTALL_DIR%\backend"
if not exist "%INSTALL_DIR%\backend\models" mkdir "%INSTALL_DIR%\backend\models"
if not exist "%INSTALL_DIR%\backend\temp" mkdir "%INSTALL_DIR%\backend\temp"
if not exist "%INSTALL_DIR%\backend\outputs" mkdir "%INSTALL_DIR%\backend\outputs"
echo        √ 目录创建完成

:: 复制文件
echo.
echo [安装] 复制程序文件...
xcopy /E /I /Y /Q "%~dp0backend\app" "%INSTALL_DIR%\backend\app" >nul
xcopy /E /I /Y /Q "%~dp0addon" "%ADDON_DIR%" >nul
copy /Y "%~dp0backend\requirements.txt" "%INSTALL_DIR%\backend\" >nul
echo        √ 文件复制完成

:: 安装依赖
echo.
echo [安装] 安装Python依赖（可能需要几分钟）...
cd /d "%INSTALL_DIR%\backend"
pip install -r requirements.txt -q 2>nul
if errorlevel 1 (
    echo        ! 部分依赖安装失败，首次运行时会自动安装
) else (
    echo        √ 依赖安装完成
)

:: 注册PPT插件
echo.
echo [安装] 注册PPT插件...
:: 写入注册表
reg add "HKCU\Software\Microsoft\Office\16.0\WEF\TrustedCatalogs\{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}" /v "Id" /t REG_SZ /d "{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}" /f >nul 2>&1
reg add "HKCU\Software\Microsoft\Office\16.0\WEF\TrustedCatalogs\{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}" /v "Url" /t REG_SZ /d "%ADDON_DIR%" /f >nul 2>&1
reg add "HKCU\Software\Microsoft\Office\16.0\WEF\TrustedCatalogs\{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}" /v "Name" /t REG_SZ /d "PPT图片处理工具" /f >nul 2>&1
reg add "HKCU\Software\Microsoft\Office\16.0\WEF\TrustedCatalogs\{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}" /v "Enable" /t REG_DWORD /d 1 /f >nul 2>&1
echo        √ 插件注册完成

:: 创建启动脚本
echo.
echo [安装] 创建快捷方式...
echo @echo off > "%INSTALL_DIR%\启动服务.bat"
echo cd /d "%INSTALL_DIR%\backend" >> "%INSTALL_DIR%\启动服务.bat"
echo start "" python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 >> "%INSTALL_DIR%\启动服务.bat"
echo echo 服务已启动: http://localhost:8000 >> "%INSTALL_DIR%\启动服务.bat"
echo timeout /t 3 ^>nul >> "%INSTALL_DIR%\启动服务.bat"

:: 创建桌面快捷方式
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut([Environment]::GetFolderPath('Desktop')+'\PPT图片工具.lnk'); $s.TargetPath = '%INSTALL_DIR%\启动服务.bat'; $s.WorkingDirectory = '%INSTALL_DIR%'; $s.Save()" 2>nul
echo        √ 快捷方式已创建

:: 完成
echo.
echo ╔══════════════════════════════════════════╗
echo ║            安装完成！                    ║
echo ╚══════════════════════════════════════════╝
echo.
echo 使用方法:
echo   1. 双击桌面 "PPT图片工具" 启动服务
echo   2. 打开 PowerPoint
echo   3. 插入 ^> 获取加载项 ^> 管理我的加载项
echo   4. 选择 "图片处理工具"
echo.
echo 首次使用需要等待模型下载（约500MB）
echo.
echo 安装位置: %INSTALL_DIR%
echo.

:: 询问是否立即启动
set /p START="是否立即启动服务？(Y/N): "
if /i "%START%"=="Y" (
    echo.
    echo 正在启动服务...
    start "" python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
    timeout /t 3 >nul
    start http://localhost:8000/docs
)

pause