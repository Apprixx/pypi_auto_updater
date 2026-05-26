@echo off
chcp 65001 >nul
title 删除 PyPI Auto Updater 计划任务

set "TASK_NAME=PyPI_Auto_Updater"

echo.
echo ============================================
echo   删除 Windows 计划任务：%TASK_NAME%
echo ============================================
echo.

:: 检查是否存在此任务
schtasks /query /tn "%TASK_NAME%" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ 未找到任务 "%TASK_NAME%"
    echo 无需删除。
    echo.
    pause
    exit /b 0
)

:: 删除任务
echo 🗑️ 正在删除任务 "%TASK_NAME%" ...
schtasks /delete /tn "%TASK_NAME%" /f >nul 2>&1

if %errorlevel%==0 (
    echo ✅ 已成功删除任务 "%TASK_NAME%"
) else (
    echo ❌ 删除失败，请以管理员身份运行此脚本。
)

echo.
pause
