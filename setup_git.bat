@echo off
echo 🚀 开始设置GitHub仓库...

echo.
echo 请输入您的GitHub用户名:
set /p username="用户名: "

echo.
echo 请输入您的GitHub邮箱:
set /p email="邮箱: "

echo.
echo 正在配置Git用户信息...
"D:\download\Git\cmd\git.exe" config --global user.name "%username%"
"D:\download\Git\cmd\git.exe" config --global user.email "%email%"

echo.
echo 正在初始化仓库...
"D:\download\Git\cmd\git.exe" init

echo.
echo 正在添加文件...
"D:\download\Git\cmd\git.exe" add .

echo.
echo 正在创建初始提交...
"D:\download\Git\cmd\git.exe" commit -m "初始化ARS to USD汇率抓取器项目"

echo.
echo ✅ 本地仓库设置完成！
echo.
echo 📋 下一步操作：
echo 1. 在GitHub上创建新仓库（名称建议：ars-usd-scraper）
echo 2. 复制仓库地址（如：https://github.com/您的用户名/ars-usd-scraper.git）
echo 3. 运行以下命令推送到GitHub：
echo.
echo "D:\download\Git\cmd\git.exe" remote add origin https://github.com/您的用户名/ars-usd-scraper.git
echo "D:\download\Git\cmd\git.exe" branch -M main
echo "D:\download\Git\cmd\git.exe" push -u origin main
echo.
pause
