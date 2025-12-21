import tkinter as tk
from tkinter import ttk
import json
import os
import re
from datetime import datetime, timedelta
import threading
import time
import sys

def resource_path(relative_path):
    """获取资源文件的绝对路径"""
    try:
        # PyInstaller创建临时文件夹，将路径存储在_MEIPASS中
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

def get_config_path():
    """获取配置文件路径"""
    try:
        # PyInstaller环境下
        base_path = sys._MEIPASS
        # 在打包环境中，配置文件应该在可执行文件同级目录
        config_path = os.path.join(os.path.dirname(sys.executable), "config.json")
        if os.path.exists(config_path):
            return config_path
    except Exception:
        pass
    
    # 开发环境或配置文件在当前目录
    return "config.json"

# 添加当前目录到sys.path以便导入settings模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import settings
except ImportError:
    settings = None

# 默认配置
DEFAULT_CONFIG = {
    "log_file_path": r".\runtime.log",
    "font_name": "Microsoft YaHei",
    "font_size": 24,
    "background_color": "#80ff80",
    "font_color": "#000000",
    "remark_font_size": 20,
    "remark_color": "#0000ff",
    "window_width": 550,
    "window_height": 60,
    "window_x": 1000,
    "window_y": 1000,
    "window_alpha": 1.0,
    "remark": "账号1"
}

CONFIG_FILE = "config.json"


class MowerTimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("mower定时器")
        ScaleFactor = 1
        if sys.platform == "win32":
            from ctypes import windll

            windll.shcore.SetProcessDpiAwareness(1)
            ScaleFactor = windll.shcore.GetScaleFactorForDevice(0) / 100
        
        # 设置窗口无边框
        self.root.overrideredirect(True)
        
        # 加载配置
        self.config = self.load_config()
        
        # 设置初始窗口大小和位置
        self.root.geometry(f"{self.config['window_width']}x{self.config['window_height']}+"
                          f"{self.config['window_x']}+{self.config['window_y']}")
        
        # 设置窗口透明度和置顶
        self.root.attributes('-alpha', self.config['window_alpha'])
        self.root.attributes('-topmost', True)
        
        self.next_mowing_time = None
        
        # 创建主框架
        self.main_frame = tk.Frame(self.root, bg=self.config['background_color'])
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 整个内容区域使用grid布局以便更好地控制元素位置
        self.content_frame = tk.Frame(self.main_frame, bg=self.config['background_color'])
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        self.content_frame.columnconfigure(0, weight=1)  # 左侧倒计时区域
        self.content_frame.columnconfigure(1, weight=0)  # 右侧按钮区域
        self.content_frame.rowconfigure(0, weight=1)     # 垂直居中
        
        # 左侧倒计时标签
        self.countdown_label = tk.Label(
            self.content_frame,
            text="正在加载...",
            bg=self.config['background_color'],
            fg=self.config['font_color'],
            font=(self.config['font_name'], self.config['font_size'], 'bold')
        )
        self.countdown_label.grid(row=0, column=0, sticky='w', padx=10, pady=10)
        
        # 右侧按钮框架
        self.button_frame = tk.Frame(self.content_frame, bg=self.config['background_color'])
        self.button_frame.grid(row=0, column=1, sticky='', padx=5, pady=5)
        
        # 备注标签
        self.remark_label = tk.Label(
            self.button_frame,
            text=self.config['remark'],
            bg=self.config['background_color'],
            fg=self.config['remark_color'],
            font=(self.config['font_name'], self.config['remark_font_size'], 'bold')
        )
        self.remark_label.pack(side=tk.LEFT, padx=2)
        
        # 设置按钮
        if settings:
            self.settings_button = tk.Button(
                self.button_frame,
                text='⚙',
                bg='#3333ff',
                fg='white',
                font=('Arial', max(self.config['font_size'] - 6, 2), 'bold'),
                bd=0,
                command=self.open_settings,
                width=3,
                height=1
            )
            self.settings_button.pack(side=tk.LEFT, padx=2)
        
        # 关闭按钮
        self.close_button = tk.Button(
            self.button_frame,
            text='×',
            bg='#ff3333',
            fg='white',
            font=('Arial', max(self.config['font_size'] - 6, 2), 'bold'),
            bd=0,
            command=self.root.quit,
            width=3,
            height=1
        )
        self.close_button.pack(side=tk.LEFT, padx=2)
        
        # 绑定事件：允许拖动窗口（绑定到整个窗口）
        self.root.bind('<Button-1>', self.start_move)
        self.root.bind('<B1-Motion>', self.do_move)
        self.main_frame.bind('<Button-1>', self.start_move)
        self.main_frame.bind('<B1-Motion>', self.do_move)
        self.content_frame.bind('<Button-1>', self.start_move)
        self.content_frame.bind('<B1-Motion>', self.do_move)
        self.button_frame.bind('<Button-1>', self.start_move)
        self.button_frame.bind('<B1-Motion>', self.do_move)
        self.remark_label.bind('<Button-1>', self.start_move)
        self.remark_label.bind('<B1-Motion>', self.do_move)
        self.countdown_label.bind('<Button-1>', self.start_move)
        self.countdown_label.bind('<B1-Motion>', self.do_move)
        
        # 初始化移动变量
        self.x = 0
        self.y = 0
        
        # 启动后台线程读取日志和更新倒计时
        self.running = True
        self.log_thread = threading.Thread(target=self.log_reader_loop, daemon=True)
        self.log_thread.start()
        
        # 启动更新UI线程
        self.ui_thread = threading.Thread(target=self.update_ui_loop, daemon=True)
        self.ui_thread.start()

    def update_ui_loop(self):
        """更新UI界面"""
        while self.running:
            self.update_countdown_display()
            time.sleep(1)  # 每秒更新一次界面

    def start_move(self, event):
        """记录开始移动的位置"""
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        """处理窗口移动"""
        deltax = event.x - self.x
        dely = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + dely
        self.root.geometry(f"+{x}+{y}")
        # 更新配置中的位置信息
        self.config['window_x'] = x
        self.config['window_y'] = y

    def load_config(self):
        """加载配置文件，如果不存在则创建默认配置"""
        config_file = get_config_path()
        
        # 默认配置
        default_config = {
            "log_file_path": r".\runtime.log",
            "font_name": "Microsoft YaHei",
            "font_size": 24,
            "background_color": "#80ff80",
            "font_color": "#000000",
            "remark_font_size": 20,
            "remark_color": "#0000ff",
            "window_width": 550,
            "window_height": 60,
            "window_x": 1000,
            "window_y": 1000,
            "window_alpha": 1.0,
            "remark": "账号1"
        }
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 合并默认配置和文件配置，确保新字段存在
                    default_config.update(config)
                    return default_config
            except Exception as e:
                print(f"读取配置文件出错: {e}")
                return default_config
        else:
            # 如果配置文件不存在，创建默认配置文件
            self.save_config(default_config)
            return default_config

    def save_config(self, config):
        """保存配置到文件"""
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)

    def reload_config(self):
        """重新加载配置并更新界面"""
        self.config = self.load_config()
        
        # 更新窗口大小和位置
        self.root.geometry(f"{self.config['window_width']}x{self.config['window_height']}+"
                          f"{self.config['window_x']}+{self.config['window_y']}")
        
        # 更新背景颜色
        self.main_frame.config(bg=self.config['background_color'])
        self.content_frame.config(bg=self.config['background_color'])
        self.button_frame.config(bg=self.config['background_color'])
        
        # 更新备注文本和倒计时标签的字体和颜色
        self.remark_label.config(
            text=self.config['remark'],
            fg=self.config['remark_color'],
            font=(self.config['font_name'], self.config['remark_font_size'], 'bold'),
            bg=self.config['background_color']
        )
        
        self.countdown_label.config(
            fg=self.config['font_color'],
            font=(self.config['font_name'], self.config['font_size'], 'bold'),
            bg=self.config['background_color']
        )

    def open_settings(self):
        """打开设置窗口"""
        if settings:
            settings_window = settings.SettingsWindow(self)
            # 移除模态限制以支持实时预览
            # self.root.wait_window(settings_window.window)
            # 重新加载配置
            # self.reload_config()

    def parse_next_mowing_time(self, log_content):
        """
        解析日志内容获取下次任务时间
        假设日志中有类似格式: "休息 12 分钟，到15:16:53开始工作"
        或者格式: "休息 1 小时 4 分钟，到16:47:18开始工作"
        或者格式: "等待跑单 XX.X 秒"
        """
        all_times = []
        
        # 查找"等待跑单 XX.X 秒"格式
        pattern_wait_mowing = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d+ .*?: 等待跑单 (\d+\.?\d*) 秒"
        matches_wait_mowing = re.findall(pattern_wait_mowing, log_content)
        
        for timestamp_str, seconds_str in matches_wait_mowing:
            try:
                # 解析时间戳
                timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                # 添加等待的秒数得到下次任务时间
                next_time = timestamp + timedelta(seconds=float(seconds_str))
                all_times.append(next_time)
            except ValueError:
                pass
        
        # 查找带日期时间戳的"休息 X 小时 Y 分钟，到HH:MM:SS开始工作"格式
        pattern_timestamped = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d+ .*?: 休息 \d+ 小时 \d+ 分钟，到(\d{2}:\d{2}:\d{2})开始工作"
        matches_timestamped = re.findall(pattern_timestamped, log_content)
        
        for timestamp_str, time_str in matches_timestamped:
            try:
                # 解析时间戳中的日期
                timestamp_date = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S").date()
                # 组合日期和时间
                next_time = datetime.strptime(time_str, "%H:%M:%S").time()
                next_datetime = datetime.combine(timestamp_date, next_time)
                all_times.append(next_datetime)
            except ValueError:
                pass
        
        # 查找带日期时间戳的"休息 X 分钟，到HH:MM:SS开始工作"格式
        pattern_timestamped_min = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d+ .*?: 休息 \d+ 分钟，到(\d{2}:\d{2}:\d{2})开始工作"
        matches_timestamped_min = re.findall(pattern_timestamped_min, log_content)
        
        for timestamp_str, time_str in matches_timestamped_min:
            try:
                # 解析时间戳中的日期
                timestamp_date = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S").date()
                # 组合日期和时间
                next_time = datetime.strptime(time_str, "%H:%M:%S").time()
                next_datetime = datetime.combine(timestamp_date, next_time)
                all_times.append(next_datetime)
            except ValueError:
                pass
        
        # 返回所有找到的时间中最晚的一个（最新的时间）
        if all_times:
            return max(all_times)
        
        return None

    def read_log_file(self):
        """读取日志文件并解析下次任务时间"""
        if not os.path.exists(self.config['log_file_path']):
            return None
            
        try:
            with open(self.config['log_file_path'], 'r', encoding='utf-8') as f:
                content = f.read()
                return self.parse_next_mowing_time(content)
        except Exception:
            return None

    def log_reader_loop(self):
        """循环读取日志文件"""
        while self.running:
            # 只有在没有设置下次任务时间或者时间已过时才读取日志
            if self.next_mowing_time is None:
                self.next_mowing_time = self.read_log_file()
            elif self.next_mowing_time <= datetime.now():
                # 时间已过，需要重新读取日志获取新的时间
                self.next_mowing_time = self.read_log_file()
            
            time.sleep(5)  # 每5秒检查一次是否需要读取日志

    def update_countdown_display(self):
        """更新倒计时显示"""
        self.root.lift()
        if self.next_mowing_time is None:
            display_text = "运行中..."
        else:
            now = datetime.now()
            if self.next_mowing_time > now:
                # 检查是否来自"等待跑单"的日志
                log_content = ""
                try:
                    with open(self.config['log_file_path'], 'r', encoding='utf-8') as f:
                        log_content = f.read()
                except Exception:
                    pass
                
                # 检查是否存在最近的"等待跑单"日志条目
                pattern_wait_mowing = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d+ .*?: 等待跑单 (\d+\.?\d*) 秒"
                matches_wait_mowing = re.findall(pattern_wait_mowing, log_content)
                
                is_waiting_mowing = False
                if matches_wait_mowing:
                    # 取最后一个匹配项（最新的时间）
                    timestamp_str, seconds_str = matches_wait_mowing[-1]
                    try:
                        # 解析时间戳
                        log_time = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                        # 检查该日志是否是当前有效的倒计时来源
                        next_time = log_time + timedelta(seconds=float(seconds_str))
                        if abs((next_time - self.next_mowing_time).total_seconds()) < 1:
                            is_waiting_mowing = True
                            # 显示剩余秒数
                            diff_seconds = (self.next_mowing_time - now).total_seconds()
                            display_text = f"跑单中……还有{int(diff_seconds)}秒"
                    except ValueError:
                        pass
                
                # 如果不是"等待跑单"的情况，则使用原有显示方式
                if not is_waiting_mowing:
                    # 计算剩余时间
                    diff = self.next_mowing_time - now
                    days = diff.days
                    hours, remainder = divmod(diff.seconds, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    
                    if days > 0:
                        display_text = f"{days}天 {hours:02d}:{minutes:02d}:{seconds:02d}后开始运行"
                    else:
                        display_text = f"{hours:02d}:{minutes:02d}:{seconds:02d}后开始运行"
            else:
                # 如果已经过了计划时间，则显示运行中，并立即重新读取日志
                display_text = "运行中..."
                self.next_mowing_time = self.read_log_file()
        
        # 在主线程中更新UI
        try:
            self.countdown_label.config(text=display_text)
        except tk.TclError:
            # 窗口已关闭
            pass

    def quit_app(self):
        """退出应用程序"""
        self.running = False
        self.root.quit()


def main():
    root = tk.Tk()
    app = MowerTimerApp(root)
    
    # 处理关闭事件
    root.protocol("WM_DELETE_WINDOW", app.quit_app)
    
    # 启动GUI主循环
    root.mainloop()


if __name__ == "__main__":
    main()