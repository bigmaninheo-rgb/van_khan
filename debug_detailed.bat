@echo off
echo ========================================
echo    DETAILED VERCEL DEBUG
echo ========================================
echo.

cd /d "C:\Users\Admin\Desktop\app văn khấn\van-khan"

echo ✅ Kiem tra file path...

REM Kiem tra absolute path
echo Current directory: %CD%
echo.

REM Kiem tra file co ton tai khong
echo === CHECK FILES ===
if exist "main.py" (
    echo ✅ main.py: TON TAI
    dir "main.py"
) else (
    echo ❌ main.py: KHONG TON TAI
)

if exist "pyproject.toml" (
    echo ✅ pyproject.toml: TON TAI
    type "pyproject.toml"
) else (
    echo ❌ pyproject.toml: KHONG TON TAI
)

if exist "index.html" (
    echo ✅ index.html: TON TAI
) else (
    echo ❌ index.html: KHONG TON TAI
)

echo.
echo === CHECK CORE FOLDER ===
if exist "core\logic.py" (
    echo ✅ core\logic.py: TON TAI
    echo Noi dung file:
    type "core\logic.py" | findstr /C:"simple_lunar_date" /n
) else (
    echo ❌ core\logic.py: KHONG TON TAI
)

echo.
echo === CHECK DATABASE ===
if exist "data\vankhan.db" (
    echo ✅ vankhan.db: TON TAI
    dir "data\vankhan.db"
) else (
    echo ❌ vankhan.db: KHONG TON TAI
)

echo.
echo 📝 Dang commit len GitHub...
git add .
git commit -m "Detailed debug - check file paths and content"
git push origin main

echo.
echo ✅ Da push! Cho Vercel deploy...
echo 🔗 Link: https://van-khan-git-main-bigmaninheo-rgbs-projects.vercel.app
echo.
pause
