@echo off
echo ========================================
echo    UPLOAD ROOT FOLDER LEN GITHUB
echo ========================================
echo.

cd /d "C:\Users\Admin\Desktop\app văn khấn\van-khan"

echo ✅ Folder hien tai: %CD%

echo ✅ Folder root da san sang:
echo    - main.py (entrypoint)
echo    - pyproject.toml (config)
echo    - index.html (trang chinh)
echo    - python.js, flutter_bootstrap.js (scripts)
echo    - core/logic.py (fix lunardate)
echo    - data/vankhan.db (database)
echo    - assets/, pyodide/ (Flutter & Python)
echo.

REM Kiem tra git
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Git chua duoc cai dat!
    echo Vao git-scm.com de cai Git
    pause
    exit /b 1
)

echo ✅ Git da san sang

REM Fix git config
git config --global --add safe.directory "%CD%"

REM Nhap repository URL
set /p repo_url="Nhap GitHub repository URL: "
if "%repo_url%"=="" (
    echo ❌ Ban phai nhap URL!
    pause
    exit /b 1
)

echo.
echo 🔧 Dang cau hinh Git...
git init
git add .
git config user.name "Van Khan App"
git config user.email "vankhan@example.com"

echo.
echo 📝 Dang commit...
git commit -m "Fix Vercel entrypoint - use main.py instead of app.py"

echo.
echo 📤 Dang push len GitHub...
git remote add origin %repo_url%
git branch -M main
git push -u origin main

if errorlevel 1 (
    echo.
    echo ❌ Loi khi push!
    echo Kiem tra lai:
    echo 1. URL co dung khong?
    echo 2. Ban co quyen truy cap repo?
    pause
    exit /b 1
)

echo.
echo ✅ Thanh cong! App da len GitHub
echo.
echo 📱 Tiep theo:
echo 1. Vercel se auto-deploy
echo 2. Link: https://van-khan-xxx.vercel.app
echo 3. Entrypoint: main.py
echo.
pause
