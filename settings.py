import tkinter as tk
from tkinter import ttk, colorchooser, font
import json
import os
import sys

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


class SettingsWindow:
    def __init__(self, parent=None):
        """初始化设置窗口"""
        self.parent = parent
        self.config = self.load_config()
        
        # 创建主窗口
        self.window = tk.Toplevel()
        self.window.title("设置")
        
        # 根据DPI缩放调整窗口大小和字体
        scale_factor = 1.0
        if parent and hasattr(parent, 'ScaleFactor'):
            scale_factor = getattr(parent, 'ScaleFactor', 1.0)
        
        # 调整窗口大小
        window_width = int(500 * scale_factor)
        window_height = int(650 * scale_factor)
        self.window.geometry(f"{window_width}x{window_height}")
        self.window.resizable(False, False)
        
        # 设置窗口置顶
        self.window.attributes('-topmost', True)
        
        # 设置窗口位置在屏幕左上角，考虑DPI缩放
        x_pos = int(100 * scale_factor)
        y_pos = int(100 * scale_factor)
        self.window.geometry(f"+{x_pos}+{y_pos}")
        
        # 绑定窗口关闭事件
        self.window.protocol("WM_DELETE_WINDOW", self.close_settings)
        
        self.create_widgets()
        self.load_settings_to_form()
        
    def scale_fonts(self, scale_factor):
        """根据缩放因子调整字体大小"""
        if scale_factor != 1.0:
            # 存储缩放因子供后续使用
            self.scale_factor = scale_factor
            
            # 调整不同类型的控件字体
            self._scale_widget_fonts(self.window, scale_factor)
    
    def _scale_widget_fonts(self, parent, scale_factor):
        """递归调整容器内所有控件的字体"""
        for widget in parent.winfo_children():
            # 根据控件类型调整字体
            if isinstance(widget, (ttk.Label, ttk.Button)):
                self._adjust_widget_font(widget, scale_factor)
            elif isinstance(widget, (ttk.Entry, ttk.Spinbox)):
                self._adjust_widget_font(widget, scale_factor, base_size=9)  # 输入类控件基础字体小一些
            elif isinstance(widget, ttk.Frame):
                # 对特殊框架进行处理
                if hasattr(widget, 'winfo_children'):
                    self._scale_widget_fonts(widget, scale_factor)
                    
    def _adjust_widget_font(self, widget, scale_factor, base_size=None):
        """调整单个控件的字体"""
        try:
            # 获取当前字体
            current_font = font.nametofont(str(widget['font'])) if widget['font'] else None
            
            if current_font:
                # 使用控件当前字体的大小作为基准
                actual_size = current_font.actual()['size']
                if actual_size > 0:  # 只有当字体大小有效时才缩放
                    new_size = max(8, int(abs(actual_size) * scale_factor))  # 最小字体大小为8
                    current_font.configure(size=new_size)
            else:
                # 如果没有指定字体，则基于基础大小计算
                if base_size is None:
                    base_size = 10
                new_size = max(8, int(base_size * scale_factor))
                widget.configure(font=(self.config.get('font_name', 'Microsoft YaHei'), new_size))
                
        except Exception as e:
            print(f"调整控件字体时出错: {e}")

    def center_window(self):
        """将窗口居中显示"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')

    def load_config(self):
        """加载配置文件"""
        config_file = get_config_path()
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return {**DEFAULT_CONFIG, **json.load(f)}
            except Exception:
                return DEFAULT_CONFIG.copy()
        else:
            self.save_config(DEFAULT_CONFIG)
            return DEFAULT_CONFIG.copy()

    def save_config(self, config):
        """保存配置到文件"""
        config_file = get_config_path()
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)

    def create_widgets(self):
        """创建设置界面控件"""
        # 创建主框架
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 定义字体大小（参考示例中的16号字体）
        label_font = ('Microsoft YaHei', 16)  # 标签字体
        entry_font = ('Microsoft YaHei', 16)  # 输入框字体
        
        # 日志文件路径设置
        ttk.Label(main_frame, text="日志文件路径:", font=label_font).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.log_file_var = tk.StringVar()
        log_file_entry = ttk.Entry(main_frame, textvariable=self.log_file_var, width=30, font=entry_font)
        log_file_entry.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 字体设置
        ttk.Label(main_frame, text="字体:", font=label_font).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.font_name_var = tk.StringVar()
        font_names = ["Microsoft YaHei", "SimSun", "SimHei", "KaiTi", "FangSong"]
        font_name_combo = ttk.Combobox(main_frame, textvariable=self.font_name_var, values=font_names, state="readonly", width=15, font=entry_font)
        font_name_combo.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 字体大小设置
        ttk.Label(main_frame, text="字体大小:", font=label_font).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.font_size_var = tk.IntVar()
        font_size_spinbox = ttk.Spinbox(main_frame, from_=8, to=72, textvariable=self.font_size_var, width=10, font=entry_font)
        font_size_spinbox.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # 窗口宽度设置
        ttk.Label(main_frame, text="窗口宽度:", font=label_font).grid(row=3, column=0, sticky=tk.W, pady=5)
        self.width_var = tk.IntVar()
        width_spinbox = ttk.Spinbox(main_frame, from_=100, to=2000, textvariable=self.width_var, width=10, font=entry_font)
        width_spinbox.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # 窗口高度设置
        ttk.Label(main_frame, text="窗口高度:", font=label_font).grid(row=4, column=0, sticky=tk.W, pady=5)
        self.height_var = tk.IntVar()
        height_spinbox = ttk.Spinbox(main_frame, from_=30, to=500, textvariable=self.height_var, width=10, font=entry_font)
        height_spinbox.grid(row=4, column=1, sticky=tk.W, pady=5)
        
        # 窗口X坐标设置
        ttk.Label(main_frame, text="窗口X坐标:", font=label_font).grid(row=5, column=0, sticky=tk.W, pady=5)
        self.x_var = tk.IntVar()
        x_spinbox = ttk.Spinbox(main_frame, from_=0, to=5000, textvariable=self.x_var, width=10, font=entry_font)
        x_spinbox.grid(row=5, column=1, sticky=tk.W, pady=5)
        
        # 窗口Y坐标设置
        ttk.Label(main_frame, text="窗口Y坐标:", font=label_font).grid(row=6, column=0, sticky=tk.W, pady=5)
        self.y_var = tk.IntVar()
        y_spinbox = ttk.Spinbox(main_frame, from_=0, to=5000, textvariable=self.y_var, width=10, font=entry_font)
        y_spinbox.grid(row=6, column=1, sticky=tk.W, pady=5)
        
        # 背景颜色设置
        ttk.Label(main_frame, text="背景颜色:", font=label_font).grid(row=7, column=0, sticky=tk.W, pady=5)
        self.bg_color_var = tk.StringVar()
        bg_color_frame = ttk.Frame(main_frame)
        bg_color_frame.grid(row=7, column=1, sticky=tk.W, pady=5)
        self.bg_color_preview = tk.Label(bg_color_frame, width=3, relief=tk.RAISED, font=entry_font)
        self.bg_color_preview.pack(side=tk.LEFT, padx=(0, 5))
        bg_color_button = ttk.Button(bg_color_frame, text="选择颜色", command=self.choose_bg_color, style='Small.TButton')
        bg_color_button.pack(side=tk.LEFT)
        
        # 字体颜色设置
        ttk.Label(main_frame, text="字体颜色:", font=('Microsoft YaHei', 16)).grid(row=8, column=0, sticky=tk.W, pady=5)
        self.font_color_var = tk.StringVar()
        font_color_frame = ttk.Frame(main_frame)
        font_color_frame.grid(row=8, column=1, sticky=tk.W, pady=5)
        self.font_color_preview = tk.Label(font_color_frame, width=3, relief=tk.RAISED, font=('Microsoft YaHei', 16))
        self.font_color_preview.pack(side=tk.LEFT, padx=(0, 5))
        font_color_button = ttk.Button(font_color_frame, text="选择颜色", command=self.choose_font_color, style='Small.TButton')
        font_color_button.pack(side=tk.LEFT)
        
        # 备注设置
        ttk.Label(main_frame, text="备注:", font=('Microsoft YaHei', 16)).grid(row=9, column=0, sticky=tk.W, pady=5)
        self.remark_var = tk.StringVar()
        remark_entry = ttk.Entry(main_frame, textvariable=self.remark_var, width=30, font=('Microsoft YaHei', 16))
        remark_entry.grid(row=9, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 备注字体大小设置
        ttk.Label(main_frame, text="备注字体大小:", font=('Microsoft YaHei', 16)).grid(row=10, column=0, sticky=tk.W, pady=5)
        self.remark_font_size_var = tk.IntVar()
        remark_font_size_spinbox = ttk.Spinbox(main_frame, from_=8, to=72, textvariable=self.remark_font_size_var, width=10, font=('Microsoft YaHei', 16))
        remark_font_size_spinbox.grid(row=10, column=1, sticky=tk.W, pady=5)
        
        # 备注颜色设置
        ttk.Label(main_frame, text="备注颜色:", font=('Microsoft YaHei', 16)).grid(row=11, column=0, sticky=tk.W, pady=5)
        self.remark_color_var = tk.StringVar()
        remark_color_frame = ttk.Frame(main_frame)
        remark_color_frame.grid(row=11, column=1, sticky=tk.W, pady=5)
        self.remark_color_preview = tk.Label(remark_color_frame, width=3, relief=tk.RAISED, font=('Microsoft YaHei', 16))
        self.remark_color_preview.pack(side=tk.LEFT, padx=(0, 5))
        remark_color_button = ttk.Button(remark_color_frame, text="选择颜色", command=self.choose_remark_color, style='Small.TButton')
        remark_color_button.pack(side=tk.LEFT)
        
        # 窗口透明度设置
        ttk.Label(main_frame, text="窗口透明度:", font=('Microsoft YaHei', 16)).grid(row=12, column=0, sticky=tk.W, pady=5)
        self.window_alpha_var = tk.DoubleVar()
        window_alpha_scale = ttk.Scale(main_frame, from_=0.1, to=1.0, variable=self.window_alpha_var, orient=tk.HORIZONTAL, length=200, command=self.on_alpha_change)
        window_alpha_scale.grid(row=12, column=1, sticky=tk.W, pady=5)
        self.window_alpha_label = ttk.Label(main_frame, text="0.8", font=('Microsoft YaHei', 16))
        self.window_alpha_label.grid(row=12, column=2, sticky=tk.W, pady=5, padx=(5, 0))
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=13, column=0, columnspan=3, pady=20)
        
        # 保存按钮
        save_button = ttk.Button(button_frame, text="保存设置", command=self.save_settings, style='Large.TButton')
        save_button.pack(side=tk.LEFT, padx=5)
        
        # 应用按钮
        apply_button = ttk.Button(button_frame, text="应用", command=self.apply_settings, style='Large.TButton')
        apply_button.pack(side=tk.LEFT, padx=5)
        
        # 关闭按钮
        close_button = ttk.Button(button_frame, text="关闭", command=self.close_settings, style='Large.TButton')
        close_button.pack(side=tk.LEFT, padx=5)
        
        # 设置按钮样式
        self.setup_styles()
        
        # 配置网格权重
        main_frame.columnconfigure(1, weight=1)
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)

    def load_settings_to_form(self):
        """将配置加载到表单"""
        self.log_file_var.set(self.config.get("log_file_path", r".\runtime.log"))
        self.font_name_var.set(self.config.get("font_name", "Microsoft YaHei"))
        self.font_size_var.set(self.config.get("font_size", 24))
        self.width_var.set(self.config.get("window_width", 550))
        self.height_var.set(self.config.get("window_height", 60))
        self.x_var.set(self.config.get("window_x", 1000))
        self.y_var.set(self.config.get("window_y", 1000))
        self.bg_color_var.set(self.config.get("background_color", "#80ff80"))
        self.font_color_var.set(self.config.get("font_color", "#000000"))
        self.remark_font_size_var.set(self.config.get("remark_font_size", 20))
        self.remark_color_var.set(self.config.get("remark_color", "#0000ff"))
        self.window_alpha_var.set(self.config.get("window_alpha", 1.0))
        self.remark_var.set(self.config.get("remark", "账号1"))
        
        # 更新颜色预览和透明度标签
        self.update_color_previews()
        self.window_alpha_label.config(text=f"{self.window_alpha_var.get():.1f}")

    def update_color_previews(self):
        """更新颜色预览"""
        bg_color = self.bg_color_var.get()
        try:
            self.bg_color_preview.config(bg=bg_color)
        except tk.TclError:
            self.bg_color_preview.config(bg="#80FF80")
            
        font_color = self.font_color_var.get()
        try:
            self.font_color_preview.config(bg=font_color)
        except tk.TclError:
            self.font_color_preview.config(bg="#000000")
            
        remark_color = self.remark_color_var.get()
        try:
            self.remark_color_preview.config(bg=remark_color)
        except tk.TclError:
            self.remark_color_preview.config(bg="#0000FF")

    def choose_bg_color(self):
        """选择背景颜色"""
        color = colorchooser.askcolor(title="选择背景颜色", color=self.bg_color_var.get())
        if color[1]:  # 用户选择了颜色而不是取消
            self.bg_color_var.set(color[1])
            self.update_color_previews()

    def choose_font_color(self):
        """选择字体颜色"""
        color = colorchooser.askcolor(title="选择字体颜色", color=self.font_color_var.get())
        if color[1]:  # 用户选择了颜色而不是取消
            self.font_color_var.set(color[1])
            self.update_color_previews()

    def choose_remark_color(self):
        """选择备注颜色"""
        color = colorchooser.askcolor(title="选择备注颜色", color=self.remark_color_var.get())
        if color[1]:  # 用户选择了颜色而不是取消
            self.remark_color_var.set(color[1])
            self.update_color_previews()

    def on_alpha_change(self, value):
        """窗口透明度变化时的回调函数"""
        # 更新透明度标签显示
        alpha_value = float(value)
        self.window_alpha_label.config(text=f"{alpha_value:.1f}")
        
        # 如果有父窗口，实时预览透明度变化
        if hasattr(self.parent, 'root'):
            try:
                self.parent.root.attributes('-alpha', alpha_value)
            except tk.TclError:
                pass

    def on_setting_change(self, *args):
        """设置发生变化时的回调函数"""
        # 实时预览颜色和字体变化
        if hasattr(self.parent, 'reload_config'):
            self.parent.reload_config()

    def on_window_geometry_change(self, *args):
        """窗口几何属性变化时的回调函数"""
        # 实时预览窗口大小和位置变化
        if hasattr(self.parent, 'root'):
            try:
                self.parent.root.geometry(f"{self.width_var.get()}x{self.height_var.get()}+"
                                        f"{self.x_var.get()}+{self.y_var.get()}")
            except tk.TclError:
                pass

    def close_window(self):
        """处理窗口销毁"""
        # 销毁窗口
        self.window.destroy()
        if self.parent is None:
            # 如果是独立运行，退出程序
            try:
                self.window.quit()
            except tk.TclError:
                pass

    def close_settings(self):
        """关闭设置窗口时重新加载主窗口配置"""
        try:
            if hasattr(self.parent, 'reload_config'):
                self.parent.reload_config()
        except:
            pass
            
        # 正确关闭窗口
        try:
            self.window.destroy()
        except:
            pass

    def save_settings(self):
        """保存设置到配置文件"""
        self.apply_settings()
        # 正确关闭窗口
        try:
            self.window.destroy()
        except:
            pass

    def apply_settings(self):
        """应用设置"""
        new_config = {
            "log_file_path": self.log_file_var.get(),
            "font_name": self.font_name_var.get(),
            "font_size": self.font_size_var.get(),
            "background_color": self.bg_color_var.get(),
            "font_color": self.font_color_var.get(),
            "remark_font_size": self.remark_font_size_var.get(),
            "remark_color": self.remark_color_var.get(),
            "window_width": self.width_var.get(),
            "window_height": self.height_var.get(),
            "window_x": self.x_var.get(),
            "window_y": self.y_var.get(),
            "window_alpha": self.window_alpha_var.get(),
            "remark": self.remark_var.get()
        }
        
        self.save_config(new_config)
        self.config = new_config
        
        # 如果有父窗口，通知它重新加载配置
        if hasattr(self.parent, 'reload_config'):
            self.parent.reload_config()
            
        # 实时预览各种设置变化
        if hasattr(self.parent, 'root'):
            try:
                root = self.parent.root
                
                # 实时预览透明度变化
                root.attributes('-alpha', new_config['window_alpha'])
                
                # 实时预览窗口大小和位置变化
                root.geometry(f"{new_config['window_width']}x{new_config['window_height']}+"
                             f"{new_config['window_x']}+{new_config['window_y']}")
                
                # 实时预览背景颜色和字体颜色变化
                root.configure(bg=new_config['background_color'])
                
                # 假设主窗口有一个 text_label 用于显示文本
                if hasattr(self.parent, 'countdown_label') and self.parent.countdown_label:
                    font_spec = (new_config['font_name'], new_config['font_size'], 'bold')
                    self.parent.countdown_label.configure(
                        fg=new_config['font_color'],
                        bg=new_config['background_color'],
                        font=font_spec
                    )
                
                # 假设主窗口有一个 remark_label 用于显示备注
                if hasattr(self.parent, 'remark_label') and self.parent.remark_label:
                    remark_font_spec = (new_config['font_name'], new_config['remark_font_size'], 'bold')
                    self.parent.remark_label.configure(
                        fg=new_config['remark_color'],
                        bg=new_config['background_color'],
                        font=remark_font_spec,
                        text=new_config['remark']
                    )
                    
            except (tk.TclError, AttributeError) as e:
                print(f"实时预览设置时出错: {e}")

    def setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()
        # 设置按钮字体大小（稍小于标签字体）
        style.configure('Large.TButton', font=('Microsoft YaHei', 14))
        style.configure('Small.TButton', font=('Microsoft YaHei', 12))
        
        # 确保所有控件使用合适的字体
        style.configure('TLabel', font=('Microsoft YaHei', 16))
        style.configure('TEntry', font=('Microsoft YaHei', 16))
        style.configure('TSpinbox', font=('Microsoft YaHei', 16))
        style.configure('TCombobox', font=('Microsoft YaHei', 16))
