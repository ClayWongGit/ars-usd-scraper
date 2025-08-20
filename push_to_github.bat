@echo off
echo 📤 推送到GitHub...

echo.
echo 请输入您的GitHub仓库地址（例如：https://github.com/用户名/ars-usd-scraper.git）:
set /p repo_url="仓库地址: "

echo.
echo 正在添加远程仓库...
"D:\download\Git\cmd\git.exe" remote add origin %repo_url%

echo.
echo 正在设置主分支...
"D:\download\Git\cmd\git.exe" branch -M main

echo.
echo 正在推送到GitHub...
"D:\download\Git\cmd\git.exe" push -u origin main

echo.
if %errorlevel% equ 0 (
    echo ✅ 推送成功！
    echo.
    echo 🎉 GitHub Actions 现在将每日自动运行！
    echo 📊 查看运行状态：您的仓库 → Actions 标签
    echo 📥 下载数据：您的仓库 → data/rates.csv
    echo.
) else (
    echo ❌ 推送失败，可能需要：
    echo 1. 检查仓库地址是否正确
    echo 2. 确保您有仓库的推送权限
    echo 3. 可能需要GitHub个人访问令牌
)

pause

