import os
import sys
import subprocess
import shutil

def build_with_pyinstaller():
    """使用PyInstaller打包程序"""
    print("正在准备打包环境...")
    
    # 确保dist和build目录不存在
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("MowerTimer.spec"):
        os.remove("MowerTimer.spec")
    
    print("正在使用PyInstaller打包程序...")
    
    # PyInstaller命令
    cmd = [
        "pyinstaller",
        "--noconfirm",           # 不询问确认
        "--onedir",              # 打包成目录形式
        "--windowed",            # 窗口模式（不显示控制台）
        "--name=MowerTimer",     # 可执行文件名
        "--icon=NONE",           # 不使用图标
        "--add-data",            # 添加数据文件
        "config.json;.",         # 添加配置文件
        "--hidden-import",       # 隐藏导入
        "tkinter",               # 导入tkinter
        "main.py"                # 主程序文件
    ]
    
    try:
        # 执行打包命令
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("打包成功完成！")
        print(f"可执行文件位于: {os.path.join(os.getcwd(), 'dist', 'MowerTimer')}")
        return True
    except subprocess.CalledProcessError as e:
        print("打包失败！")
        print(f"错误信息: {e}")
        print(f"stderr: {e.stderr}")
        return False
    except FileNotFoundError:
        print("错误: 未找到PyInstaller。请先安装PyInstaller:")
        print("pip install pyinstaller")
        return False

if __name__ == "__main__":
    build_with_pyinstaller()