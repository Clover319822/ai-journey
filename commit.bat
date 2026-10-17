@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0"

set MSG=%*
if "%MSG%"=="" set /p MSG=写一句今天干了啥（中文就行，直接回车会用默认说明）:
if "%MSG%"=="" set MSG=chore: 日常提交

echo.
echo ---- 1/3 加入暂存 ----
git add -A
if errorlevel 1 goto fail

echo ---- 2/3 提交 ----
git commit -m "%MSG%"
if errorlevel 1 goto fail

echo ---- 3/3 推送到 GitHub ----
git push origin main
if errorlevel 1 goto fail

echo.
echo 成功。去 https://github.com/Clover319822/ai-journey 看一眼有没有更新。
echo.
pause
exit /b 0

:fail
echo.
echo 出错了，把上面红色/黑色的字整段复制发给我。
echo.
pause
exit /b 1
