@echo off
echo 正在安装依赖...
pip install -r requirements.txt
echo.

echo 正在使用PyInstaller打包程序...
pyinstaller --noconfirm --onedir --windowed --name=MowerTimer --icon=NONE --add-data "config.json;." --hidden-import tkinter main.py
echo.

echo 打包完成！可执行文件位于 dist\MowerTimer 目录中
echo.
pause