@echo off
chcp 65001 >nul
title PPT图片处理工具 - 一键安装（免Python版）

echo.
echo ╔══════════════════════════════════════════╗
echo ║   PPT图片处理工具 - 一键安装（免Python）  ║
echo ╚══════════════════════════════════════════╝
echo.

:: 设置安装目录
set "INSTALL_DIR=%LOCALAPPDATA%\PPTImageTools"
set "ADDON_DIR=%INSTALL_DIR%\addon"

:: 创建目录
echo [1/3] 创建程序目录...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
if not exist "%INSTALL_DIR%\models" mkdir "%INSTALL_DIR%\models"
if not exist "%INSTALL_DIR%\temp" mkdir "%INSTALL_DIR%\temp"
if not exist "%INSTALL_DIR%\outputs" mkdir "%INSTALL_DIR%\outputs"
echo        √ 完成

:: 复制文件
echo.
echo [2/3] 复制程序文件...
xcopy /E /I /Y /Q "%~dp0addon" "%ADDON_DIR%" >nul
copy /Y "%~dp0PPT图片工具.exe" "%INSTALL_DIR%\" >nul
echo        √ 完成

:: 注册PPT插件
echo.
echo [3/3] 注册PPT插件...
reg add "HKCU\Software\Microsoft\Office\16.0\WEF\TrustedCatalogs\{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}" /v "Id" /t REG_SZ /d "{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}" /f >nul 2>&1
reg add "HKCU\Software\Microsoft\Office\16.0\WEF\TrustedCatalogs\{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}" /v "Url" /t REG_SZ /d "%ADDON_DIR%" /f >nul 2>&1
reg add "HKCU\Software\Microsoft\Office\16.0\WEF\TrustedCatalogs\{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}" /v "Name" /t REG_SZ /d "PPT图片处理工具" /f >nul 2>&1
reg add "HKCU\Software\Microsoft\Office\16.0\WEF\TrustedCatalogs\{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}" /v "Enable" /t REG_DWORD /d 1 /f >nul 2>&1
echo        √ 完成

:: 创建桌面快捷方式
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut([Environment]::GetFolderPath('Desktop')+'\PPT图片工具.lnk'); $s.TargetPath = '%INSTALL_DIR%\PPT图片工具.exe'; $s.WorkingDirectory = '%INSTALL_DIR%'; $s.Save()" 2>nul

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
echo 安装位置: %INSTALL_DIR%
echo.

:: 询问是否立即启动
set /p START="是否立即启动？(Y/N): "
if /i "%START%"=="Y" (
    start "" "%INSTALL_DIR%\PPT图片工具.exe"
    timeout /t 3 >nul
    start http://localhost:8000/docs
)

pause