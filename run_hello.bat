@echo off
chcp 65001 >nul
cd /d "%~dp0"
.venv\Scripts\python.exe week01\hello_llm.py
echo.
pause
