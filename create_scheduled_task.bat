@echo off
chcp 65001 >nul

echo.
echo ===================================
echo  PyPI Auto Updater 计划任务添加程序
echo ===================================
echo.

cd /d "%~dp0"

REM 检查并安装 requests 包
python -c "import requests" 2>nul || pip install requests

REM 运行
python create_scheduled_task.py

echo 运行完成
pause