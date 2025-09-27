@echo off
echo 币安量化交易系统 - 自动打包工具
echo =====================================

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.7+
    pause
    exit /b 1
)

REM 安装打包依赖
echo 正在安装打包依赖...
python -m pip install -r build_requirements.txt

REM 运行打包脚本
echo 开始打包...
python build_exe.py

pause
