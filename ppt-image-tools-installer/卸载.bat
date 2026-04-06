@echo off
chcp 65001 >nul
title PPT图片处理工具 - 卸载

echo.
echo ╔══════════════════════════════════════════╗
echo ║     PPT图片处理工具 - 卸载               ║
echo ╚══════════════════════════════════════════╝
echo.

set /p CONFIRM="确定要卸载吗？(Y/N): "
if /i not "%CONFIRM%"=="Y" (
    echo 已取消卸载
    pause
    exit /b
)

echo.
echo [卸载] 删除注册表项...
reg delete "HKCU\Software\Microsoft\Office\16.0\WEF\TrustedCatalogs\{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}" /f >nul 2>&1
echo        √ 注册表已清理

echo.
echo [卸载] 删除程序文件...
rd /s /q "%LOCALAPPDATA%\PPTImageTools" 2>nul
echo        √ 文件已删除

echo.
echo [卸载] 删除桌面快捷方式...
del /q "%USERPROFILE%\Desktop\PPT图片工具.lnk" 2>nul
echo        √ 快捷方式已删除

echo.
echo ╔══════════════════════════════════════════╗
echo ║            卸载完成！                    ║
echo ╚══════════════════════════════════════════╝
echo.
pause