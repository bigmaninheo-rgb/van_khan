@echo off
echo ========================================
echo    DEBUG VERCEL DEPLOYMENT
echo ========================================
echo.

cd /d "C:\Users\Admin\Desktop\app văn khấn\van-khan"

echo ✅ Kiem tra file quan trong build...

if exist "main.py" (
    echo ✅ main.py - OK
) else (
    echo ❌ main.py - THIEU!
)

if exist "pyproject.toml" (
    echo ✅ pyproject.toml - OK
) else (
    echo ❌ pyproject.toml - THIEU!
)

if exist "index.html" (
    echo ✅ index.html - OK
) else (
    echo ❌ index.html - THIEU!
)

if exist "python.js" (
    echo ✅ python.js - OK
) else (
    echo ❌ python.js - THIEU!
)

if exist "core\logic.py" (
    echo ✅ core\logic.py - OK
) else (
    echo ❌ core\logic.py - THIEU!
)

if exist "data\vankhan.db" (
    echo ✅ vankhan.db - OK
) else (
    echo ❌ vankhan.db - THIEU!
)

echo.
echo 🔧 Dang kiem tra noi dung logic.py...
findstr /C:"lunardate" "core\logic.py" >nul 2>&1
if errorlevel 1 (
    echo ✅ logic.py - KHONG CO lunardate
) else (
    echo ❌ logic.py - VAN CO CON lunardate!
)

echo.
echo 📝 Dang commit fix...
git add .
git commit -m "Fix HTTP 500 error - check all files"
git push

echo.
echo ✅ Da push len GitHub!
echo 📱 Vercel se auto-deploy trong 1-2 phut
echo 🔗 Link: https://van-khan-git-main-bigmaninheo-rgbs-projects.vercel.app
echo.
pause
