@echo off
echo ========================================
echo    UPLOAD GITHUB - SIMPLE VERSION
echo ========================================
echo.

cd /d "C:\Users\Admin\Desktop\app văn khấn\van-khan"

echo ✅ Folder: %CD%

REM Git init trong folder dung
git init

REM Add tat ca file
git add .

REM Config user
git config user.name "Van Khan App"
git config user.email "vankhan@example.com"

echo.
echo 📝 Dang commit...
git commit -m "Fix Vercel deployment - main.py entrypoint"

echo.
echo 📤 Dang push...
git remote add origin https://github.com/bigmaninheo-rgb/van_khan.git
git branch -M main
git push -u origin main --force

echo.
echo ✅ Ket qua:
if errorlevel 1 (
    echo ❌ Loi khi push!
    echo Kiem tra:
    echo 1. Internet connection?
    echo 2. GitHub URL dung?
    echo 3. Repo co ton tai?
) else (
    echo ✅ Thanh cong!
    echo 📱 Vercel se auto-deploy
    echo 🔗 Link: https://van-khan-xxx.vercel.app
)

echo.
pause
