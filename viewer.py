"""
ImageViewer - 简洁好用的看图软件
MIT License
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

try:
    from PIL import Image, ImageTk, ExifTags
except ImportError:
    messagebox.showerror("缺少依赖", "请先安装 Pillow：\npip install Pillow")
    sys.exit(1)

SUPPORTED_EXTS = {
    ".jpg", ".jpeg", ".png", ".gif", ".bmp",
    ".webp", ".tiff", ".tif", ".ico", ".ppm",
    ".pgm", ".pbm", ".pnm", ".svg"
}

APP_TITLE = "ImageViewer"
VERSION = "1.0.0"
BG_COLOR = "#1e1e1e"
PANEL_COLOR = "#2d2d2d"
BTN_COLOR = "#3a3a3a"
BTN_HOVER = "#505050"
TEXT_COLOR = "#e0e0e0"
ACCENT_COLOR = "#5b9bd5"


class ImageViewer:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("1100x750")
        self.root.minsize(600, 400)
        self.root.configure(bg=BG_COLOR)

        # 状态变量
        self.image_list: list[Path] = []
        self.current_index: int = -1
        self.original_image: Image.Image | None = None
        self.photo_image: ImageTk.PhotoImage | None = None
        self.zoom_factor: float = 1.0
        self.rotation: int = 0
        self.fit_mode: bool = True           # 适应窗口
        self.slideshow_running: bool = False
        self.slideshow_delay: int = 3000     # ms
        self._slideshow_job = None
        self._drag_start = None
        self._canvas_offset = [0, 0]

        self._build_ui()
        self._bind_keys()

        # 支持拖拽文件进入
        try:
            self.root.drop_target_register("DND_Files")  # type: ignore
            self.root.dnd_bind("<<Drop>>", self._on_drop)  # type: ignore
        except Exception:
            pass  # tkinterdnd2 未安装则跳过

    # ──────────────────────────── UI 构建 ────────────────────────────

    def _build_ui(self):
        # 顶部工具栏
        toolbar = tk.Frame(self.root, bg=PANEL_COLOR, height=46)
        toolbar.pack(fill=tk.X, side=tk.TOP)
        toolbar.pack_propagate(False)

        btn_cfg = dict(bg=BTN_COLOR, fg=TEXT_COLOR, relief=tk.FLAT,
                       font=("微软雅黑", 10), padx=8, pady=4,
                       activebackground=BTN_HOVER, activeforeground=TEXT_COLOR,
                       cursor="hand2", bd=0)

        tk.Button(toolbar, text="📂 打开文件", command=self.open_file, **btn_cfg).pack(side=tk.LEFT, padx=(8, 2), pady=5)
        tk.Button(toolbar, text="📁 打开文件夹", command=self.open_folder, **btn_cfg).pack(side=tk.LEFT, padx=2, pady=5)

        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=6, pady=8)

        tk.Button(toolbar, text="⬅ 上一张", command=self.prev_image, **btn_cfg).pack(side=tk.LEFT, padx=2, pady=5)
        tk.Button(toolbar, text="➡ 下一张", command=self.next_image, **btn_cfg).pack(side=tk.LEFT, padx=2, pady=5)

        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=6, pady=8)

        tk.Button(toolbar, text="🔍+", command=self.zoom_in, **btn_cfg).pack(side=tk.LEFT, padx=2, pady=5)
        tk.Button(toolbar, text="🔍−", command=self.zoom_out, **btn_cfg).pack(side=tk.LEFT, padx=2, pady=5)
        tk.Button(toolbar, text="⬜ 适应", command=self.fit_window, **btn_cfg).pack(side=tk.LEFT, padx=2, pady=5)
        tk.Button(toolbar, text="1:1", command=self.zoom_100, **btn_cfg).pack(side=tk.LEFT, padx=2, pady=5)

        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=6, pady=8)

        tk.Button(toolbar, text="↺ 左转", command=self.rotate_left, **btn_cfg).pack(side=tk.LEFT, padx=2, pady=5)
        tk.Button(toolbar, text="↻ 右转", command=self.rotate_right, **btn_cfg).pack(side=tk.LEFT, padx=2, pady=5)

        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=6, pady=8)

        self.slideshow_btn = tk.Button(toolbar, text="▶ 幻灯片", command=self.toggle_slideshow, **btn_cfg)
        self.slideshow_btn.pack(side=tk.LEFT, padx=2, pady=5)

        tk.Button(toolbar, text="⛶ 全屏", command=self.toggle_fullscreen, **btn_cfg).pack(side=tk.LEFT, padx=2, pady=5)

        tk.Button(toolbar, text="ℹ 信息", command=self.show_info, **btn_cfg).pack(side=tk.RIGHT, padx=(2, 8), pady=5)
        tk.Button(toolbar, text="🗑 删除", command=self.delete_image, **btn_cfg).pack(side=tk.RIGHT, padx=2, pady=5)

        # 主区域：左侧缩略图栏 + 右侧画布
        main_frame = tk.Frame(self.root, bg=BG_COLOR)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 左侧缩略图面板
        self.thumb_frame = tk.Frame(main_frame, bg=PANEL_COLOR, width=110)
        self.thumb_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.thumb_frame.pack_propagate(False)

        thumb_header = tk.Label(self.thumb_frame, text="缩略图", bg=PANEL_COLOR,
                                fg=TEXT_COLOR, font=("微软雅黑", 9))
        thumb_header.pack(pady=(6, 2))

        self.thumb_canvas = tk.Canvas(self.thumb_frame, bg=PANEL_COLOR,
                                      highlightthickness=0, width=104)
        self.thumb_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        thumb_scroll = ttk.Scrollbar(self.thumb_frame, orient=tk.VERTICAL,
                                     command=self.thumb_canvas.yview)
        thumb_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.thumb_canvas.configure(yscrollcommand=thumb_scroll.set)

        self.thumb_inner = tk.Frame(self.thumb_canvas, bg=PANEL_COLOR)
        self.thumb_canvas.create_window((0, 0), window=self.thumb_inner, anchor="nw")
        self.thumb_inner.bind("<Configure>",
                              lambda e: self.thumb_canvas.configure(
                                  scrollregion=self.thumb_canvas.bbox("all")))
        self._thumb_images: list = []
        self._thumb_buttons: list = []

        # 右侧画布
        canvas_frame = tk.Frame(main_frame, bg=BG_COLOR)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(canvas_frame, bg=BG_COLOR,
                                highlightthickness=0, cursor="crosshair")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<ButtonPress-1>", self._drag_start_cb)
        self.canvas.bind("<B1-Motion>", self._drag_move_cb)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Button-4>", self._on_mousewheel)   # Linux
        self.canvas.bind("<Button-5>", self._on_mousewheel)   # Linux
        self.canvas.bind("<Configure>", self._on_canvas_resize)

        # 状态栏
        status_bar = tk.Frame(self.root, bg=PANEL_COLOR, height=24)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        status_bar.pack_propagate(False)
        self.status_var = tk.StringVar(value="就绪 — 打开文件或文件夹开始浏览")
        tk.Label(status_bar, textvariable=self.status_var,
                 bg=PANEL_COLOR, fg=TEXT_COLOR,
                 font=("微软雅黑", 9), anchor="w").pack(side=tk.LEFT, padx=8)
        self.zoom_var = tk.StringVar(value="100%")
        tk.Label(status_bar, textvariable=self.zoom_var,
                 bg=PANEL_COLOR, fg=ACCENT_COLOR,
                 font=("微软雅黑", 9)).pack(side=tk.RIGHT, padx=8)

        # 欢迎画面
        self._show_welcome()

    def _show_welcome(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width() or 800
        h = self.canvas.winfo_height() or 600
        cx, cy = w // 2, h // 2
        self.canvas.create_text(cx, cy - 30, text="🖼",
                                font=("Arial", 48), fill="#555")
        self.canvas.create_text(cx, cy + 30,
                                text="ImageViewer  v" + VERSION,
                                font=("微软雅黑", 16, "bold"), fill="#666")
        self.canvas.create_text(cx, cy + 60,
                                text="打开文件 / 文件夹，或将图片拖入此窗口",
                                font=("微软雅黑", 11), fill="#555")

    # ──────────────────────────── 键盘绑定 ────────────────────────────

    def _bind_keys(self):
        self.root.bind("<Left>", lambda e: self.prev_image())
        self.root.bind("<Right>", lambda e: self.next_image())
        self.root.bind("<Up>", lambda e: self.zoom_in())
        self.root.bind("<Down>", lambda e: self.zoom_out())
        self.root.bind("<F11>", lambda e: self.toggle_fullscreen())
        self.root.bind("<Escape>", self._on_escape)
        self.root.bind("<Delete>", lambda e: self.delete_image())
        self.root.bind("<space>", lambda e: self.next_image())
        self.root.bind("<r>", lambda e: self.rotate_right())
        self.root.bind("<l>", lambda e: self.rotate_left())
        self.root.bind("<f>", lambda e: self.fit_window())
        self.root.bind("<1>", lambda e: self.zoom_100())
        self.root.bind("<s>", lambda e: self.toggle_slideshow())
        self.root.bind("<Control-o>", lambda e: self.open_file())

    # ──────────────────────────── 文件操作 ────────────────────────────

    def open_file(self):
        filetypes = [
            ("图片文件", " ".join(f"*{e}" for e in SUPPORTED_EXTS)),
            ("所有文件", "*.*")
        ]
        path = filedialog.askopenfilename(title="打开图片", filetypes=filetypes)
        if path:
            p = Path(path)
            # 加载同目录下的所有图片
            self._load_folder(p.parent)
            idx = next((i for i, x in enumerate(self.image_list) if x == p), 0)
            self.show_image(idx)

    def open_folder(self):
        folder = filedialog.askdirectory(title="打开文件夹")
        if folder:
            self._load_folder(Path(folder))
            if self.image_list:
                self.show_image(0)

    def _load_folder(self, folder: Path):
        files = sorted(
            [f for f in folder.iterdir()
             if f.is_file() and f.suffix.lower() in SUPPORTED_EXTS],
            key=lambda x: x.name.lower()
        )
        self.image_list = files
        self._build_thumbnails()

    def _on_drop(self, event):
        raw = event.data
        # tkinterdnd2 格式
        paths = self.root.tk.splitlist(raw)
        if paths:
            p = Path(paths[0])
            if p.is_dir():
                self._load_folder(p)
                if self.image_list:
                    self.show_image(0)
            elif p.suffix.lower() in SUPPORTED_EXTS:
                self._load_folder(p.parent)
                idx = next((i for i, x in enumerate(self.image_list) if x == p), 0)
                self.show_image(idx)

    # ──────────────────────────── 图片显示 ────────────────────────────

    def show_image(self, index: int):
        if not self.image_list:
            return
        index = index % len(self.image_list)
        self.current_index = index
        path = self.image_list[index]

        try:
            img = Image.open(path)
            # 处理 EXIF 旋转
            img = self._fix_exif_rotation(img)
            img = img.convert("RGBA") if img.mode in ("P", "LA") else img
            self.original_image = img
        except Exception as e:
            messagebox.showerror("打开失败", f"无法打开图片：\n{e}")
            return

        self.rotation = 0
        if self.fit_mode:
            self.zoom_factor = self._calc_fit_zoom()
        self._canvas_offset = [0, 0]
        self._render()
        self._update_status()
        self._highlight_thumb(index)

    def _fix_exif_rotation(self, img: Image.Image) -> Image.Image:
        try:
            exif = img._getexif()  # type: ignore
            if exif:
                for tag, val in exif.items():
                    if ExifTags.TAGS.get(tag) == "Orientation":
                        if val == 3:
                            img = img.rotate(180, expand=True)
                        elif val == 6:
                            img = img.rotate(270, expand=True)
                        elif val == 8:
                            img = img.rotate(90, expand=True)
                        break
        except Exception:
            pass
        return img

    def _calc_fit_zoom(self) -> float:
        if not self.original_image:
            return 1.0
        cw = self.canvas.winfo_width() or 800
        ch = self.canvas.winfo_height() or 600
        iw, ih = self.original_image.size
        if self.rotation in (90, 270):
            iw, ih = ih, iw
        zx = cw / iw
        zy = ch / ih
        return min(zx, zy, 1.5)

    def _render(self):
        if not self.original_image:
            return
        img = self.original_image.copy()
        if self.rotation:
            img = img.rotate(-self.rotation, expand=True)

        iw, ih = img.size
        new_w = max(1, int(iw * self.zoom_factor))
        new_h = max(1, int(ih * self.zoom_factor))

        resample = Image.LANCZOS if (self.zoom_factor < 1 or self.zoom_factor > 2) else Image.NEAREST
        img = img.resize((new_w, new_h), resample)

        self.photo_image = ImageTk.PhotoImage(img)
        cw = self.canvas.winfo_width() or 800
        ch = self.canvas.winfo_height() or 600
        x = cw // 2 + self._canvas_offset[0]
        y = ch // 2 + self._canvas_offset[1]

        self.canvas.delete("all")
        self.canvas.create_image(x, y, image=self.photo_image, anchor="center", tags="img")
        self.zoom_var.set(f"{int(self.zoom_factor * 100)}%")

    def _on_canvas_resize(self, event):
        if self.fit_mode and self.original_image:
            self.zoom_factor = self._calc_fit_zoom()
            self._canvas_offset = [0, 0]
            self._render()

    # ──────────────────────────── 导航 ────────────────────────────────

    def prev_image(self):
        if self.image_list:
            self.show_image(self.current_index - 1)

    def next_image(self):
        if self.image_list:
            self.show_image(self.current_index + 1)

    # ──────────────────────────── 缩放 ────────────────────────────────

    def zoom_in(self):
        self.fit_mode = False
        self.zoom_factor = min(self.zoom_factor * 1.25, 20.0)
        self._render()

    def zoom_out(self):
        self.fit_mode = False
        self.zoom_factor = max(self.zoom_factor / 1.25, 0.02)
        self._render()

    def fit_window(self):
        self.fit_mode = True
        self._canvas_offset = [0, 0]
        self.zoom_factor = self._calc_fit_zoom()
        self._render()

    def zoom_100(self):
        self.fit_mode = False
        self._canvas_offset = [0, 0]
        self.zoom_factor = 1.0
        self._render()

    def _on_mousewheel(self, event):
        if not self.original_image:
            return
        self.fit_mode = False
        if hasattr(event, "delta"):
            factor = 1.15 if event.delta > 0 else 1 / 1.15
        else:
            factor = 1.15 if event.num == 4 else 1 / 1.15
        self.zoom_factor = max(0.02, min(self.zoom_factor * factor, 20.0))
        self._render()

    # ──────────────────────────── 旋转 ────────────────────────────────

    def rotate_left(self):
        self.rotation = (self.rotation - 90) % 360
        if self.fit_mode:
            self.zoom_factor = self._calc_fit_zoom()
        self._render()

    def rotate_right(self):
        self.rotation = (self.rotation + 90) % 360
        if self.fit_mode:
            self.zoom_factor = self._calc_fit_zoom()
        self._render()

    # ──────────────────────────── 拖拽 ────────────────────────────────

    def _drag_start_cb(self, event):
        self._drag_start = (event.x, event.y)

    def _drag_move_cb(self, event):
        if self._drag_start:
            dx = event.x - self._drag_start[0]
            dy = event.y - self._drag_start[1]
            self._drag_start = (event.x, event.y)
            self._canvas_offset[0] += dx
            self._canvas_offset[1] += dy
            self.fit_mode = False
            self._render()

    # ──────────────────────────── 全屏 ────────────────────────────────

    def toggle_fullscreen(self):
        state = self.root.attributes("-fullscreen")
        self.root.attributes("-fullscreen", not state)

    def _on_escape(self, event):
        if self.root.attributes("-fullscreen"):
            self.root.attributes("-fullscreen", False)

    # ──────────────────────────── 幻灯片 ──────────────────────────────

    def toggle_slideshow(self):
        self.slideshow_running = not self.slideshow_running
        if self.slideshow_running:
            self.slideshow_btn.config(text="⏹ 停止")
            self._advance_slideshow()
        else:
            self.slideshow_btn.config(text="▶ 幻灯片")
            if self._slideshow_job:
                self.root.after_cancel(self._slideshow_job)

    def _advance_slideshow(self):
        if not self.slideshow_running:
            return
        self.next_image()
        self._slideshow_job = self.root.after(self.slideshow_delay, self._advance_slideshow)

    # ──────────────────────────── 缩略图 ──────────────────────────────

    def _build_thumbnails(self):
        for w in self.thumb_inner.winfo_children():
            w.destroy()
        self._thumb_images.clear()
        self._thumb_buttons.clear()

        for i, path in enumerate(self.image_list):
            self._add_thumb(i, path)

    def _add_thumb(self, index: int, path: Path):
        try:
            img = Image.open(path)
            img.thumbnail((80, 80))
            photo = ImageTk.PhotoImage(img)
        except Exception:
            photo = None

        btn = tk.Button(
            self.thumb_inner,
            image=photo if photo else None,
            text="" if photo else path.name[:8],
            compound=tk.TOP,
            bg=PANEL_COLOR, fg=TEXT_COLOR,
            activebackground=BTN_HOVER,
            relief=tk.FLAT, bd=1,
            cursor="hand2",
            command=lambda i=index: self.show_image(i)
        )
        btn.pack(pady=2, padx=4, fill=tk.X)
        self._thumb_images.append(photo)
        self._thumb_buttons.append(btn)

    def _highlight_thumb(self, index: int):
        for i, btn in enumerate(self._thumb_buttons):
            btn.config(bg=ACCENT_COLOR if i == index else PANEL_COLOR)
        # 滚动到当前缩略图
        if 0 <= index < len(self._thumb_buttons):
            btn = self._thumb_buttons[index]
            self.root.update_idletasks()
            y = btn.winfo_y()
            total = self.thumb_inner.winfo_height() or 1
            self.thumb_canvas.yview_moveto(y / total)

    # ──────────────────────────── 信息 & 删除 ────────────────────────

    def show_info(self):
        if not self.original_image or self.current_index < 0:
            messagebox.showinfo("提示", "请先打开一张图片。")
            return
        path = self.image_list[self.current_index]
        stat = path.stat()
        w, h = self.original_image.size
        size_kb = stat.st_size / 1024
        info = (
            f"文件名：{path.name}\n"
            f"路径：{path.parent}\n"
            f"分辨率：{w} × {h} px\n"
            f"文件大小：{size_kb:.1f} KB\n"
            f"格式：{self.original_image.format or '未知'}\n"
            f"色彩模式：{self.original_image.mode}\n"
            f"修改时间：{__import__('datetime').datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}"
        )
        messagebox.showinfo("图片信息", info)

    def delete_image(self):
        if not self.image_list or self.current_index < 0:
            return
        path = self.image_list[self.current_index]
        if not messagebox.askyesno("确认删除", f"确定要删除以下文件吗？\n{path.name}\n\n此操作不可撤销！"):
            return
        try:
            os.remove(path)
        except Exception as e:
            messagebox.showerror("删除失败", str(e))
            return
        self.image_list.pop(self.current_index)
        self._thumb_buttons[self.current_index].destroy()
        self._thumb_buttons.pop(self.current_index)
        self._thumb_images.pop(self.current_index)
        if not self.image_list:
            self.current_index = -1
            self.original_image = None
            self.canvas.delete("all")
            self._show_welcome()
            self._update_status()
        else:
            self.show_image(min(self.current_index, len(self.image_list) - 1))

    # ──────────────────────────── 状态栏 ──────────────────────────────

    def _update_status(self):
        if not self.image_list or self.current_index < 0:
            self.status_var.set("就绪 — 打开文件或文件夹开始浏览")
            return
        path = self.image_list[self.current_index]
        total = len(self.image_list)
        self.status_var.set(
            f"{self.current_index + 1} / {total}  |  {path.name}  |  {path.parent}"
        )


# ──────────────────────────── 入口 ────────────────────────────────────

def main():
    root = tk.Tk()
    root.title(APP_TITLE)

    # 设置窗口图标（如有）
    icon_path = Path(__file__).parent / "icon.ico"
    if icon_path.exists():
        try:
            root.iconbitmap(str(icon_path))
        except Exception:
            pass

    app = ImageViewer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
