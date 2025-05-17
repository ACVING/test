import tkinter as tk
from tkinter import messagebox, ttk
from amzqr import amzqr
import os
from tkinter import filedialog

class QRGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Amazing-QR 二维码生成器")
        self.root.geometry("650x600")
        self.root.resizable(width=False, height=True)
        
        # 全局样式配置
        self.font = ("SimHei", 10)
        self.pad = (10, 5)  # 修改为元组格式
        self.frame_pad = (15, 10)  # 修改为元组格式
        
        # 获取prompt文件夹路径
        self.prompt_dir = self.get_prompt_dir()
        
        # 创建主框架
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 配置 ttk 样式
        style = ttk.Style()
        style.configure("QR.TRadiobutton", font=self.font)  # 为单选按钮创建样式
        style.configure("TLabel", font=self.font)  # 为标签创建样式
        # 修改按钮文字颜色为纯黑色
        style.configure("TButton", font=self.font, foreground="black")
        
        # ====================== 类型选择 ======================
        ttk.Label(main_frame, text="二维码类型:").grid(row=0, column=0, sticky=tk.W, padx=self.pad[0], pady=self.pad[1])
        self.qr_type = tk.StringVar(value="普通")
        qr_types = ["普通", "艺术", "动态"]
        ttk.Combobox(main_frame, textvariable=self.qr_type, values=qr_types, 
                     state="readonly", width=25).grid(row=0, column=1, sticky=tk.W, padx=self.pad[0], pady=self.pad[1])
        
        # ====================== 内容输入 ======================
        ttk.Label(main_frame, text="内容（URL）:").grid(row=1, column=0, sticky=tk.W, padx=self.pad[0], pady=self.pad[1])
        self.words_entry = ttk.Entry(main_frame, width=50)
        self.words_entry.grid(row=1, column=1, sticky=tk.W, padx=self.pad[0], pady=self.pad[1])
        self.words_entry.insert(0, "https://example.com")
        
        # ====================== 版本设置 ======================
        version_frame = ttk.Frame(main_frame)
        version_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=self.pad[0], pady=self.pad[1])
        
        ttk.Label(version_frame, text="大小 (1-40):").pack(side=tk.LEFT)
        self.version = tk.IntVar(value=3)
        version_scale = ttk.Scale(version_frame, from_=1, to=40, variable=self.version, 
                                 orient=tk.HORIZONTAL, length=200)
        version_scale.pack(side=tk.LEFT, padx=10)
        
        version_value = ttk.Label(version_frame, textvariable=self.version)
        version_value.pack(side=tk.LEFT, padx=5)
        
        # ====================== 纠错级别 ======================
        ec_frame = ttk.Frame(main_frame)
        ec_frame.grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=self.pad[0], pady=self.pad[1])
        
        ttk.Label(ec_frame, text="细节:").pack(side=tk.LEFT, padx=5)
        self.level = tk.StringVar(value="H")
        
        for idx, (text, value) in enumerate([("L (低)", "L"), ("M (中)", "M"), 
                                             ("Q (较高)", "Q"), ("H (高)", "H")]):
            # 使用自定义样式设置字体
            ttk.Radiobutton(ec_frame, text=text, variable=self.level, value=value,
                           style="QR.TRadiobutton").pack(side=tk.LEFT, padx=10)
        
        # ====================== 图片/GIF设置（动态显示） ======================
        self.image_frame = ttk.LabelFrame(main_frame, text="图片路径", padding=self.frame_pad)
        self.picture_path = tk.StringVar()
        
        path_entry = ttk.Entry(self.image_frame, textvariable=self.picture_path, width=40)
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 修改按钮文字颜色为纯黑色
        browse_btn = ttk.Button(self.image_frame, text="浏览", command=self.browse_file, width=10)
        browse_btn.pack(side=tk.RIGHT, padx=5)
        
        # ====================== 图片调整（动态显示） ======================
        self.adjust_frame = ttk.LabelFrame(main_frame, text="参数调整", padding=self.frame_pad)
        
        # 亮度
        brightness_frame = ttk.Frame(self.adjust_frame)
        ttk.Label(brightness_frame, text="亮度:").pack(side=tk.LEFT, padx=5)
        self.brightness = tk.DoubleVar(value=1.0)
        ttk.Scale(brightness_frame, from_=0.1, to=3.0, variable=self.brightness, 
                  orient=tk.HORIZONTAL, length=200).pack(side=tk.LEFT, padx=5)
        brightness_frame.pack(fill=tk.X, pady=5)

        # 对比度
        contrast_frame = ttk.Frame(self.adjust_frame)
        ttk.Label(contrast_frame, text="对比度:").pack(side=tk.LEFT, padx=5)
        self.contrast = tk.DoubleVar(value=1.0)
        ttk.Scale(contrast_frame, from_=0.1, to=3.0, variable=self.contrast, 
                  orient=tk.HORIZONTAL, length=200).pack(side=tk.LEFT, padx=5)
        contrast_frame.pack(fill=tk.X, pady=5)
        

        # ====================== 输出设置 ======================
        output_frame = ttk.LabelFrame(main_frame, text="输出设置", padding=self.frame_pad)
        output_frame.grid(row=6, column=0, columnspan=2, sticky=tk.NSEW, padx=self.pad[0], pady=self.pad[1])
        
        # 文件名
        ttk.Label(output_frame, text="文件名:").grid(row=0, column=0, sticky=tk.W, padx=self.pad[0], pady=self.pad[1])
        self.save_name = tk.StringVar(value="qrcode.png")
        ttk.Entry(output_frame, textvariable=self.save_name, width=40).grid(row=0, column=1, sticky=tk.W, padx=self.pad[0], pady=self.pad[1])
        
        # 目录 - 自动设置为output文件夹
        self.save_dir = tk.StringVar(value=self.get_output_dir())
        ttk.Label(output_frame, text="保存目录:").grid(row=1, column=0, sticky=tk.W, padx=self.pad[0], pady=self.pad[1])
        ttk.Entry(output_frame, textvariable=self.save_dir, width=40).grid(row=1, column=1, sticky=tk.W, padx=self.pad[0], pady=self.pad[1])
        
        # 修改按钮文字颜色为纯黑色
        dir_browse_btn = ttk.Button(output_frame, text="浏览", command=self.browse_dir, width=10)
        dir_browse_btn.grid(row=1, column=2, sticky=tk.E, padx=self.pad[0], pady=self.pad[1])
        
        # ====================== 生成按钮 ======================
        # 修改按钮文字颜色为纯黑色
        generate_btn = ttk.Button(main_frame, text="生成二维码", command=self.generate_qr,
                                 width=20)
        generate_btn.grid(row=7, column=0, columnspan=2, pady=20)
        
        # 配置其他样式
        style.configure("TButton", foreground="black", background="#4A90E2", 
                       padding=5, relief="flat")
        style.map("TButton", background=[("active", "#357ABD")])
        
        # 动态布局绑定
        self.qr_type.trace_add("write", self.update_layout)
        self.update_layout()  # 初始化布局
        
        # 如果prompt文件夹存在且有图片，设置默认图片
        if self.prompt_dir and self.get_first_image(self.prompt_dir):
            default_image = self.get_first_image(self.prompt_dir)
            self.picture_path.set(default_image)
            self.qr_type.set("动态" if default_image.lower().endswith('.gif') else "艺术")
    
    def get_output_dir(self):
        """获取或创建output文件夹路径"""
        output_dir = os.path.join(os.getcwd(), "output")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        return output_dir
    
    def get_prompt_dir(self):
        """获取prompt文件夹路径，如果不存在则返回None"""
        prompt_dir = os.path.join(os.getcwd(), "prompt")
        if os.path.exists(prompt_dir) and os.path.isdir(prompt_dir):
            return prompt_dir
        return None
    
    def get_first_image(self, directory):
        """获取目录中的第一个图片文件"""
        if not directory:
            return None
            
        image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.gif']
        for file in os.listdir(directory):
            if any(file.lower().endswith(ext) for ext in image_extensions):
                return os.path.join(directory, file)
        return None
    
    def update_layout(self, *args):
        qr_type = self.qr_type.get()
        is_art = qr_type in ["艺术", "动态"]
        
        if is_art:
            self.image_frame.grid(row=4, column=0, columnspan=2, sticky=tk.NSEW, padx=self.pad[0], pady=self.pad[1])
            self.adjust_frame.grid(row=5, column=0, columnspan=2, sticky=tk.NSEW, padx=self.pad[0], pady=self.pad[1])
            ext = ".gif" if qr_type == "动态" else ".png"
            self.save_name.set(f"qrcode{ext}")
        else:
            self.image_frame.grid_remove()
            self.adjust_frame.grid_remove()
            self.save_name.set("qrcode.png")
    
    def browse_file(self):
        initial_dir = self.prompt_dir if self.prompt_dir else os.getcwd()
        file_types = [("图片", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
        path = filedialog.askopenfilename(filetypes=file_types, initialdir=initial_dir)
        
        if path:
            self.picture_path.set(path)
            ext = os.path.splitext(path)[1].lower()
            self.qr_type.set("动态" if ext == ".gif" else "艺术")
    
    def browse_dir(self):
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.save_dir.set(dir_path)
    
    def generate_qr(self):
        words = self.words_entry.get().strip()
        version = self.version.get()
        level = self.level.get()
        
        # 确保output文件夹存在
        output_dir = self.get_output_dir()
        self.save_dir.set(output_dir)
        
        save_path = os.path.join(output_dir, self.save_name.get())
        
        if not words:
            return messagebox.showerror("错误", "请输入二维码内容！")
        
        picture = self.picture_path.get() if self.qr_type.get() != "普通" else None
        colorized = self.qr_type.get() != "普通"
        contrast = self.contrast.get() if colorized else 1.0
        brightness = self.brightness.get() if colorized else 1.0
        
        try:
            amzqr.run(
                words=words,
                version=version,
                level=level,
                picture=picture,
                colorized=colorized,
                contrast=contrast,
                brightness=brightness,
                save_name=os.path.basename(save_path),
                save_dir=output_dir
            )
            messagebox.showinfo("成功", f"二维码已生成:\n{save_path}")
            self.words_entry.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("错误", f"生成失败:\n{str(e)}")
            print(f"错误详情: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = QRGeneratorApp(root)
    root.mainloop()