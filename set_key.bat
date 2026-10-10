@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo.
echo  Paste your DeepSeek API key below, then press Enter.
echo  (Get it from platform.deepseek.com - API Keys)
echo.
.venv\Scripts\python.exe set_key.py
echo.
pause
