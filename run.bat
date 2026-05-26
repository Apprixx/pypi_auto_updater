@echo off
chcp 65001 >nul
echo 开始运行 pypi_auto_updater...

cd /d "%~dp0"

REM 检查并安装 requests 包
python -c "import requests" 2>nul || pip install requests

REM 运行主程序
python main.py

echo 运行完成
exit 0