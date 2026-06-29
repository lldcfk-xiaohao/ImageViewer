"""
CFKViewer - 极简看图软件
MIT License
Version: 2.0.1  (CFKViewer 风格重制 + 多语言)
"""

import os
import sys
import json
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Menu
from pathlib import Path

try:
    from PIL import Image, ImageTk, ExifTags, ImageDraw, ImageFont
except ImportError:
    tk.messagebox.showerror("Missing Dependency", "Please install Pillow:\npip install Pillow")
    sys.exit(1)

# ──────────────────────────── 常量 ────────────────────────────

SUPPORTED_EXTS = {
    ".jpg", ".jpeg", ".png", ".gif", ".bmp",
    ".webp", ".tiff", ".tif", ".ico", ".ppm",
    ".pgm", ".pbm", ".pnm", ".svg"
}

APP_TITLE = "CFKViewer"
VERSION = "2.0.1"

# ═══ CFKViewer 风格：亮色主题 ═══
BG_COLOR = "#FFFFFF"
CANVAS_BG = "#F7F7F7"
PANEL_COLOR = "#F0F0F0"
TEXT_PRIMARY = "#333333"
TEXT_SECONDARY = "#888888"
ACCENT_COLOR = "#4A90D9"
BTN_TEXT = "#555555"
BTN_BORDER = "#CCCCCC"
BTN_HOVER_BG = "#E8E8E8"
HOVER_BTN_BG = "#4A90D9"
HOVER_BTN_FG = "#FFFFFF"
MENU_BG = "#FAFAFA"

CONFIG_DIR = Path.home() / ".cfkviewer"
CONFIG_FILE = CONFIG_DIR / "config.json"


# ──────────────────────────── 多语言 ────────────────────────────

class I18n:
    """轻量级国际化，基于字典查表。"""

    LANGUAGES = {
        "zh_CN": "简体中文",
        "en":    "English",
        "zh_TW": "繁體中文",
        "ja":    "日本語",
    }

    STRINGS = {
        # ═══════════ 简体中文 ═════════
        "zh_CN": {
            # 欢迎页
            "welcome_drag":     "拖入图片到这里",
            "welcome_formats":  "支持 HEIC / AVIF / TIFF / RAW 等，右键可进入设置",
            "welcome_open_btn": "打开图片",
            # 右键菜单
            "ctx_copy_image":       "复制图片",
            "ctx_copy_file":        "复制文件",
            "ctx_copy_more":        "复制更多",
            "ctx_save_as":          "另存为...",
            "ctx_print":            "打印...",
            "ctx_open_location":    "打开图片位置",
            "ctx_info":             "图片信息",
            "ctx_settings":         "设置",
            "ctx_delete":           "删除",
            "ctx_always_on_top":    "窗口置顶",
            "ctx_borderless":       "无边框模式",
            "ctx_fullscreen":       "全屏模式",
            "ctx_open_with":        "打开方式",
            "ctx_more":             "更多",
            "ctx_exit":             "退出",
            "ctx_sep1":             None,
            "ctx_sep2":             None,
            "ctx_sep3":             None,
            "ctx_sep4":             None,
            # 复制更多子菜单
            "sub_copy_path":        "复制路径",
            "sub_copy_filename":    "复制文件名",
            "sub_copy_size":        "复制尺寸",
            # 设置对话框
            "dlg_title_settings":   "设置",
            "set_language":         "语言",
            "set_slideshow_speed":  "幻灯片速度（秒）",
            "set_startup_folder":   "启动时打开上次文件夹",
            "set_close":            "关闭",
            "set_ok":               "确定",
            # 信息对话框
            "info_title":           "图片信息",
            "label_filename":       "文件名",
            "label_path":           "路径",
            "label_resolution":     "分辨率",
            "label_filesize":       "文件大小",
            "label_format":         "格式",
            "label_colormode":      "色彩模式",
            "label_modified":       "修改时间",
            "label_unknown":        "未知",
            "info_open_first":      "请先打开一张图片。",
            # 对话框
            "dlg_open_image":       "打开图片",
            "dlg_open_folder":      "打开文件夹",
            "dlg_save_as":          "另存为",
            "ftype_images":         "图片文件",
            "ftype_all":            "所有文件",
            "err_dep_title":        "缺少依赖",
            "err_dep_msg":          "请先安装 Pillow：\npip install Pillow",
            "err_open_title":       "打开失败",
            "err_open_msg":         "无法打开图片：\n{error}",
            "err_del_title":        "删除失败",
            "err_save_title":       "保存失败",
            "err_print_title":      "打印失败",
            "confirm_del":          "确认删除",
            "confirm_del_msg":      "确定要删除以下文件吗？\n{name}\n\n此操作不可撤销！",
            # 状态栏
            "status_ready":         "就绪",
            # 提示
            "hint_copied_img":      "已复制图片到剪贴板",
            "hint_copied_file":     "已复制文件到剪贴板",
            "hint_copied_path":     "已复制路径到剪贴板",
            "hint_saved_as":        "已保存至：{path}",
            "hint_deleted":         "已删除：{name}",
            # 幻灯片
            "slideshow_start":      "开始幻灯片",
            "slideshow_stop":       "停止幻灯片",
        },

        # ═════════ English ═════════
        "en": {
            "welcome_drag":     "Drop images here",
            "welcome_formats":  "Supports HEIC / AVIF / TIFF / RAW etc., right-click for settings",
            "welcome_open_btn": "Open Image",
            "ctx_copy_image":       "Copy Image",
            "ctx_copy_file":        "Copy File",
            "ctx_copy_more":        "Copy More",
            "ctx_save_as":          "Save As...",
            "ctx_print":            "Print...",
            "ctx_open_location":    "Open in Explorer",
            "ctx_info":             "Image Info",
            "ctx_settings":         "Settings",
            "ctx_delete":           "Delete",
            "ctx_always_on_top":    "Always on Top",
            "ctx_borderless":       "Borderless Mode",
            "ctx_fullscreen":       "Fullscreen",
            "ctx_open_with":        "Open With",
            "ctx_more":             "More",
            "ctx_exit":             "Exit",
            "ctx_sep1":             None,
            "ctx_sep2":             None,
            "ctx_sep3":             None,
            "ctx_sep4":             None,
            "sub_copy_path":        "Copy Path",
            "sub_copy_filename":    "Copy Filename",
            "sub_copy_size":        "Copy Dimensions",
            "dlg_title_settings":   "Settings",
            "set_language":         "Language",
            "set_slideshow_speed":  "Slideshow Speed (sec)",
            "set_startup_folder":   "Reopen last folder on startup",
            "set_close":            "Close",
            "set_ok":               "OK",
            "info_title":           "Image Info",
            "label_filename":       "File Name",
            "label_path":           "Path",
            "label_resolution":     "Resolution",
            "label_filesize":       "File Size",
            "label_format":         "Format",
            "label_colormode":      "Color Mode",
            "label_modified":       "Modified",
            "label_unknown":        "Unknown",
            "info_open_first":      "Please open an image first.",
            "dlg_open_image":       "Open Image",
            "dlg_open_folder":      "Open Folder",
            "dlg_save_as":          "Save As",
            "ftype_images":         "Image Files",
            "ftype_all":            "All Files",
            "err_dep_title":        "Missing Dependency",
            "err_dep_msg":          "Please install Pillow:\npip install Pillow",
            "err_open_title":       "Open Failed",
            "err_open_msg":         "Cannot open image:\n{error}",
            "err_del_title":        "Delete Failed",
            "err_save_title":       "Save Failed",
            "err_print_title":      "Print Failed",
            "confirm_del":          "Confirm Delete",
            "confirm_del_msg":      "Are you sure you want to delete?\n{name}\n\nThis cannot be undone!",
            "status_ready":         "Ready",
            "hint_copied_img":      "Image copied to clipboard",
            "hint_copied_file":     "File copied to clipboard",
            "hint_copied_path":     "Path copied to clipboard",
            "hint_saved_as":        "Saved to: {path}",
            "hint_deleted":         "Deleted: {name}",
            "slideshow_start":      "Start Slideshow",
            "slideshow_stop":       "Stop Slideshow",
        },

        # ═════════ 繁體中文 ═════════
        "zh_TW": {
            "welcome_drag":     "拖入圖片到這裡",
            "welcome_formats":  "支援 HEIC / AVIF / TIFF / RAW 等，右鍵可進入設定",
            "welcome_open_btn": "開啟圖片",
            "ctx_copy_image":       "複製圖片",
            "ctx_copy_file":        "複製檔案",
            "ctx_copy_more":        "複製更多",
            "ctx_save_as":          "另存為...",
            "ctx_print":            "列印...",
            "ctx_open_location":    "開啟圖片位置",
            "ctx_info":             "圖片資訊",
            "ctx_settings":         "設定",
            "ctx_delete":           "刪除",
            "ctx_always_on_top":    "視窗置頂",
            "ctx_borderless":       "無邊框模式",
            "ctx_fullscreen":       "全螢幕模式",
            "ctx_open_with":        "開啟方式",
            "ctx_more":             "更多",
            "ctx_exit":             "退出",
            "ctx_sep1":             None,
            "ctx_sep2":             None,
            "ctx_sep3":             None,
            "ctx_sep4":             None,
            "sub_copy_path":        "複製路徑",
            "sub_copy_filename":    "複製檔案名",
            "sub_copy_size":        "複製尺寸",
            "dlg_title_settings":   "設定",
            "set_language":         "語言",
            "set_slideshow_speed":  "投影片速度（秒）",
            "set_startup_folder":   "啟動時開啟上次資料夾",
            "set_close":            "關閉",
            "set_ok":               "確定",
            "info_title":           "圖片資訊",
            "label_filename":       "檔案名稱",
            "label_path":           "路徑",
            "label_resolution":     "解析度",
            "label_filesize":       "檔案大小",
            "label_format":         "格式",
            "label_colormode":      "色彩模式",
            "label_modified":       "修改時間",
            "label_unknown":        "未知",
            "info_open_first":      "請先開啟一張圖片。",
            "dlg_open_image":       "開啟圖片",
            "dlg_open_folder":      "開啟資料夾",
            "dlg_save_as":          "另存為",
            "ftype_images":         "圖片檔案",
            "ftype_all":            "所有檔案",
            "err_dep_title":        "缺少依賴",
            "err_dep_msg":          "請先安裝 Pillow：\npip install Pillow",
            "err_open_title":       "開啟失敗",
            "err_open_msg":         "無法開啟圖片：\n{error}",
            "err_del_title":        "刪除失敗",
            "err_save_title":       "儲存失敗",
            "err_print_title":      "列印失敗",
            "confirm_del":          "確認刪除",
            "confirm_del_msg":      "確定要刪除以下檔案嗎？\n{name}\n\n此操作無法復原！",
            "status_ready":         "就緒",
            "hint_copied_img":      "已複製圖片到剪貼簿",
            "hint_copied_file":     "已複製檔案到剪貼簿",
            "hint_copied_path":     "已複製路徑到剪貼簿",
            "hint_saved_as":        "已儲存至：{path}",
            "hint_deleted":         "已刪除：{name}",
            "slideshow_start":      "開始投影片",
            "slideshow_stop":       "停止投影片",
        },

        # ═════════ 日本語 ═════════
        "ja": {
            "welcome_drag":     "画像をここにドロップ",
            "welcome_formats":  "HEIC / AVIF / TIFF / RAW等に対応。右クリックで設定",
            "welcome_open_btn": "画像を開く",
            "ctx_copy_image":       "画像をコピー",
            "ctx_copy_file":        "ファイルをコピー",
            "ctx_copy_more":        "その他コピー",
            "ctx_save_as":          "名前を付けて保存...",
            "ctx_print":            "印刷...",
            "ctx_open_location":    "エクスプローラーで表示",
            "ctx_info":             "画像情報",
            "ctx_settings":         "設定",
            "ctx_delete":           "削除",
            "ctx_always_on_top":    "常に手前に表示",
            "ctx_borderless":       "ボーダーレスモード",
            "ctx_fullscreen":       "フルスクリーン",
            "ctx_open_with":        "プログラムから開く",
            "ctx_more":             "その他",
            "ctx_exit":             "終了",
            "ctx_sep1":             None,
            "ctx_sep2":             None,
            "ctx_sep3":             None,
            "ctx_sep4":             None,
            "sub_copy_path":        "パスをコピー",
            "sub_copy_filename":    "ファイル名をコピー",
            "sub_copy_size":        "サイズをコピー",
            "dlg_title_settings":   "設定",
            "set_language":         "言語",
            "set_slideshow_speed":  "スライドショー間隔（秒）",
            "set_startup_folder":   "起動時に最後のフォルダを再開",
            "set_close":            "閉じる",
            "set_ok":               "OK",
            "info_title":           "画像情報",
            "label_filename":       "ファイル名",
            "label_path":           "パス",
            "label_resolution":     "解像度",
            "label_filesize":       "ファイルサイズ",
            "label_format":         "形式",
            "label_colormode":      "カラーモード",
            "label_modified":       "更新日時",
            "label_unknown":        "不明",
            "info_open_first":      "まず画像を開いてください。",
            "dlg_open_image":       "画像を開く",
            "dlg_open_folder":      "フォルダを開く",
            "dlg_save_as":          "名前を付けて保存",
            "ftype_images":         "画像ファイル",
            "ftype_all":            "すべてのファイル",
            "err_dep_title":        "依存関係不足",
            "err_dep_msg":          "P をインストールしてください：\npip install Pillow",
            "err_open_title":       "開けません",
            "err_open_msg":         "画像を開けません：\n{error}",
            "err_del_title":        "削除失敗",
            "err_save_title":       "保存失敗",
            "err_print_title":      "印刷失敗",
            "confirm_del":          "削除確認",
            "confirm_del_msg":      "このファイルを削除しますか？\n{name}\n\nこの操作は取り消せません！",
            "status_ready":         "準備完了",
            "hint_copied_img":      "画像をクリップボードにコピーしました",
            "hint_copied_file":     "ファイルをクリップボードにコピーしました",
            "hint_copied_path":     "パスをクリップボードにコピーしました",
            "hint_saved_as":        "保存しました：{path}",
            "hint_deleted":         "削除しました：{name}",
            "slideshow_start":      "スライドショー開始",
            "slideshow_stop":       "スライドショー停止",
        },
    }

    def __init__(self, lang: str = "zh_CN"):
        self.lang = lang if lang in self.LANGUAGES else "zh_CN"

    def t(self, key: str, **kwargs) -> str:
        table = self.STRINGS.get(self.lang, self.STRINGS["en"])
        s = table.get(key, self.STRINGS["en"].get(key, key))
        if kwargs:
            s = s.format(**kwargs)
        return s


# ──────────────────────────── 配置文件 ────────────────────────────

def load_config() -> dict:
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {"language": "zh_CN", "slideshow_speed": 3, "reopen_last_folder": True}


def save_config(config: dict):
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


# ──────────────────────────── 主程序 ────────────────────────────

class CFKViewer:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("900x700")
        self.root.minsize(500, 350)
        self.root.configure(bg=BG_COLOR)

        # 状态变量
        self.image_list: list[Path] = []
        self.current_index: int = -1
        self.original_image: Image.Image | None = None
        self.photo_image: ImageTk.PhotoImage | None = None
        self.zoom_factor: float = 1.0
        self.rotation: int = 0
        self.fit_mode: bool = True
        self.slideshow_running: bool = False
        self._slideshow_job = None
        self._drag_start = None
        self._canvas_offset = [0, 0]
        self.always_on_top = False
        self.borderless_mode = False
        self.last_folder: str | None = None

        # 多语言 & 配置
        self.config = load_config()
        self.i18n = I18n(self.config.get("language", "zh_CN"))
        self.slideshow_delay = int(self.config.get("slideshow_speed", 3)) * 1000

        self._build_ui()
        self._bind_keys()

        # 拖拽支持
        try:
            self.root.drop_target_register("DND_Files")  # type: ignore
            self.root.dnd_bind("<<Drop>>", self._on_drop)  # type: ignore
        except Exception:
            pass

    def t(self, key: str, **kwargs) -> str:
        return self.i18n.t(key, **kwargs)

    @property
    def _sep(self) -> str:
        """标签分隔符"""
        return "\uff1a" if self.i18n.lang in ("zh_CN", "zh_TW", "ja") else ": "

    # ═══════════════════ UI 构建 ═══════════════════

    def _build_ui(self):
        for child in self.root.winfo_children():
            child.destroy()
        self._thumb_images: list = []
        self._thumb_buttons: list = []

        # ── 主画布 ──
        self.canvas = tk.Canvas(self.root, bg=CANVAS_BG,
                                highlightthickness=0, cursor="crosshair")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<ButtonPress-1>", self._drag_start_cb)
        self.canvas.bind("<B1-Motion>", self._drag_move_cb)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Button-4>", self._on_mousewheel)
        self.canvas.bind("<Button-5>", self._on_mousewheel)
        self.canvas.bind("<Configure>", self._on_canvas_resize)
        self.canvas.bind("<Button-3>", self._show_context_menu)  # 右键

        # ── 底部状态栏 ──
        bottom = tk.Frame(self.root, bg=PANEL_COLOR, height=36)
        bottom.pack(fill=tk.X, side=tk.BOTTOM)
        bottom.pack_propagate(False)

        btn_style = dict(bg=PANEL_COLOR, fg=TEXT_PRIMARY, relief=tk.FLAT,
                         font=("Microsoft YaHei UI", 10), padx=10, pady=6,
                         activebackground=BTN_HOVER_BG, activeforeground=TEXT_PRIMARY,
                         cursor="hand2", bd=0)

        hover_style = dict(bg=PANEL_COLOR, fg=TEXT_SECONDARY, relief=tk.FLAT,
                           font=("Segoe UI MDL2 Assets", 12), padx=8, pady=4,
                           activebackground=HOVER_BTN_BG, activeforeground=HOVER_BTN_FG,
                           cursor="hand2", bd=0)

        # 左侧：文件夹 + 导航
        tk.Button(bottom, text="\U000f02a3", command=self.open_folder, **hover_style).pack(side=tk.LEFT, padx=(8, 2), pady=4)
        tk.Button(bottom, text="\u25c0", command=self.prev_image, **hover_style).pack(side=tk.LEFT, padx=2, pady=4)
        tk.Button(bottom, text="\u25b6", command=self.next_image, **hover_style).pack(side=tk.LEFT, padx=2, pady=4)

        # 中间：状态文字
        self.status_var = tk.StringVar(value=self.t("status_ready"))
        status_lbl = tk.Label(bottom, textvariable=self.status_var,
                              bg=PANEL_COLOR, fg=TEXT_SECONDARY,
                              font=("Microsoft YaHei UI", 9))
        status_lbl.pack(side=tk.LEFT, padx=12, expand=True)

        # 右侧：缩放 + 功能按钮
        tk.Button(bottom, text="\u2795", command=self.zoom_in, **hover_style).pack(side=tk.RIGHT, padx=(2, 8), pady=4)
        tk.Button(bottom, text="\u2796", command=self.zoom_out, **hover_style).pack(side=tk.RIGHT, padx=2, pady=4)
        self.zoom_var = tk.StringVar(value="100%")
        tk.Label(bottom, textvariable=self.zoom_var, bg=PANEL_COLOR, fg=TEXT_SECONDARY,
                 font=("Microsoft YaHei UI", 9)).pack(side=tk.RIGHT, padx=(2, 6))

        ttk.Separator(bottom, orient=tk.VERTICAL).pack(side=tk.RIGHT, fill=tk.Y, pady=6)

        tk.Button(bottom, text="\uf096", command=self.toggle_fullscreen, **hover_style).pack(side=tk.RIGHT, padx=2, pady=4)
        tk.Button(bottom, text="\uf085", command=lambda: self.show_settings(), **hover_style).pack(side=tk.RIGHT, padx=2, pady=4)

        # 欢迎页或恢复状态
        if self.image_list:
            if 0 <= self.current_index < len(self.image_list):
                self.show_image(self.current_index)
            else:
                self._show_welcome()
        else:
            self._show_welcome()
        self._update_status()

    # ── 欢迎页（CFKViewer 风格）──
    def _show_welcome(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width() or 800
        h = self.canvas.winfo_height() or 600
        cx, cy = w // 2, h // 2

        # 绘制图标（SVG 风格的图片占位符）
        icon_size = 64
        ix, iy = cx - icon_size // 2, cy - 80
        self.canvas.create_rectangle(ix, iy, ix + icon_size, iy + icon_size,
                                     outline="#BBBBBB", width=2)
        self.canvas.create_line(ix + 16, iy + 36, ix + 32, iy + 18, fill="#BBBBBB", width=2)
        self.canvas.create_line(ix + 32, iy + 18, ix + 48, iy + 48, fill="#BBBBBB", width=2)
        self.canvas.create_oval(ix + 38, iy + 22, ix + 48, iy + 32, outline="#BBBBBB", width=2)

        self.canvas.create_text(cx, cy + 15,
                                text=self.t("welcome_drag"),
                                font=("Microsoft YaHei UI", 14),
                                fill=TEXT_PRIMARY)
        self.canvas.create_text(cx, cy + 45,
                                text=self.t("welcome_formats"),
                                font=("Microsoft YaHei UI", 11),
                                fill=TEXT_SECONDARY)

        # 打开图片按钮
        bw, bh = 96, 32
        bx, by = cx - bw // 2, cy + 70
        self.welcome_btn = self.canvas.create_rectangle(
            bx, by, bx + bw, by + bh,
            outline=BTN_BORDER, fill=BG_COLOR, width=1)
        self.canvas.create_text(cx, by + bh // 2,
                                text=self.t("welcome_open_btn"),
                                font=("Microsoft YaHei UI", 10),
                                fill=TEXT_PRIMARY, tags="welcome_btn_text")
        self.canvas.tag_bind(self.welcome_btn, "<Button-1>", lambda e: self.open_file())
        self.canvas.tag_bind(self.welcome_btn, "<Enter>",
                             lambda e: [self.canvas.itemconfig(self.welcome_btn, fill=BTN_HOVER_BG)])
        self.canvas.tag_bind(self.welcome_btn, "<Leave>",
                             lambda e: [self.canvas.itemconfig(self.welcome_btn, fill=BG_COLOR)])

    # ── 右键上下文菜单 ──
    def _show_context_menu(self, event):
        menu = Menu(self.root, tearoff=0, bg=MENU_BG, fg=TEXT_PRIMARY,
                    activebackground=ACCENT_COLOR, activeforeground="#FFFFFF",
                    font=("Microsoft YaHei UI", 10), borderwidth=1,
                    relief=tk.SOLID)

        # 复制图片
        menu.add_command(label=self.t("ctx_copy_image"),
                         accelerator="Ctrl+C",
                         command=self.copy_image_to_clipboard)

        # 复制文件
        menu.add_command(label=self.t("ctx_copy_file"),
                         accelerator="Ctrl+Shift+C",
                         command=self.copy_file_to_clipboard)

        # 复制更多 → 子菜单
        copy_more = Menu(menu, tearoff=0, bg=MENU_BG, fg=TEXT_PRIMARY,
                         activebackground=ACCENT_COLOR, activeforeground="#FFFFFF",
                         font=("Microsoft YaHei UI", 10))
        copy_more.add_command(label=self.t("sub_copy_path"), command=self.copy_path)
        copy_more.add_command(label=self.t("sub_copy_filename"), command=self.copy_filename)
        copy_more.add_command(label=self.t("sub_copy_size"), command=self.copy_dimensions)
        menu.add_cascade(label=self.t("ctx_copy_more"), menu=copy_more)

        menu.add_separator()

        # 另存为 / 打印
        menu.add_command(label=self.t("ctx_save_as"),
                         accelerator="Ctrl+S", command=self.save_as)
        menu.add_command(label=self.t("ctx_print"),
                         accelerator="Ctrl+P", command=self.print_image)

        menu.add_separator()

        # 打开位置 / 信息
        menu.add_command(label=self.t("ctx_open_location"),
                         command=self.open_in_explorer)
        menu.add_command(label=self.t("ctx_info"),
                         command=self.show_info)

        # 设置
        menu.add_command(label=self.t("ctx_settings"),
                         command=self.show_settings)

        # 删除
        menu.add_command(label=self.t("ctx_delete"),
                         accelerator="Delete", command=self.delete_image)

        menu.add_separator()

        # 窗口置顶
        top_label = ("✔ " + self.t("ctx_always_on_top")) if self.always_on_top else self.t("ctx_always_on_top")
        menu.add_command(label=top_label, command=self.toggle_always_on_top)

        # 无边框
        border_label = ("✔ " + self.t("ctx_borderless")) if self.borderless_mode else self.t("ctx_borderless")
        menu.add_command(label=border_label, command=self.toggle_borderless)

        # 全屏
        menu.add_command(label=self.t("ctx_fullscreen"),
                         accelerator="F11", command=self.toggle_fullscreen)

        # 打开方式 →
        open_with = Menu(menu, tearoff=0, bg=MENU_BG, fg=TEXT_PRIMARY,
                         activebackground=ACCENT_COLOR, activeforeground="#FFFFFF",
                         font=("Microsoft YaHei UI", 10))
        open_with.add_command(label="系统默认程序", command=self.open_with_default)
        open_with.add_command(label="画图 (Paint)", command=self.open_with_paint)
        menu.add_cascade(label=self.t("ctx_open_with"), menu=open_with)

        # 更多 →
        more = Menu(menu, tearoff=0, bg=MENU_BG, fg=TEXT_PRIMARY,
                    activebackground=ACCENT_COLOR, activeforeground="#FFFFFF",
                    font=("Microsoft YaHei UI", 10))
        more.add_command(label=self.t("rotate_left") if hasattr(self, 't') else "↺ 左转",
                         command=self.rotate_left)
        more.add_command(label=self.t("rotate_right") if hasattr(self, 't') else "↻ 右转",
                         command=self.rotate_right)
        more.add_command(label="适应窗口" if self.i18n.lang == "zh_CN" else "Fit Window",
                         command=self.fit_window)
        more.add_command(label="原始大小 (1:1)" if self.i18n.lang == "zh_CN" else "Actual Size (1:1)",
                         command=self.zoom_100)
        more.add_separator()
        ss_label = self.t("slideshow_stop") if self.slideshow_running else self.t("slideshow_start")
        more.add_command(label=ss_label, command=self.toggle_slideshow)
        more.add_separator()
        lang_menu = Menu(more, tearoff=0, bg=MENU_BG, fg=TEXT_PRIMARY,
                         activebackground=ACCENT_COLOR, activeforeground="#FFFFFF",
                         font=("Microsoft YaHei UI", 10))
        for code, name in I18n.LANGUAGES.items():
            mark = "✓" if code == self.i18n.lang else ""
            lang_menu.add_radiobutton(label=f"{mark} {name}", command=lambda c=code: self.change_language(c))
        more.add_cascade(label=self.t("language"), menu=lang_menu)
        menu.add_cascade(label=self.t("ctx_more"), menu=more)

        menu.add_separator()
        menu.add_command(label=self.t("ctx_exit"),
                         accelerator="Esc", command=self.on_exit)

        menu.tk_popup(event.x_root, event.y_root)

    # ═══════════════════ 语言切换 ═══════════════════

    def change_language(self, lang: str):
        if lang == self.i18n.lang:
            return
        if self.slideshow_running:
            self.slideshow_running = False
            if self._slideshow_job:
                self.root.after_cancel(self._slideshow_job)
                self._slideshow_job = None
        self.i18n.lang = lang
        self.config["language"] = lang
        save_config(self.config)
        self._build_ui()

    # ═══════════════════ 键盘绑定 ═══════════════════

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
        self.root.bind("<Control-c>", lambda e: self.copy_image_to_clipboard())
        self.root.bind("<Control-Shift-C>", lambda e: self.copy_file_to_clipboard())
        self.root.bind("<Control-s>", lambda e: self.save_as())

    # ═══════════════════ 文件操作 ═══════════════════

    def open_file(self):
        filetypes = [
            (self.t("ftype_images"), " ".join(f"*{e}" for e in SUPPORTED_EXTS)),
            (self.t("ftype_all"), "*.*")
        ]
        path = filedialog.askopenfilename(title=self.t("dlg_open_image"), filetypes=filetypes)
        if path:
            p = Path(path)
            self._load_folder(p.parent)
            idx = next((i for i, x in enumerate(self.image_list) if x == p), 0)
            self.show_image(idx)

    def open_folder(self):
        folder = filedialog.askdirectory(title=self.t("dlg_open_folder"))
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
        self.last_folder = str(folder)

    def _on_drop(self, event):
        raw = event.data
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

    # ═══════════════════ 图片显示 ═══════════════════

    def show_image(self, index: int):
        if not self.image_list:
            return
        index = index % len(self.image_list)
        self.current_index = index
        path = self.image_list[index]

        try:
            img = Image.open(path)
            img = self._fix_exif_rotation(img)
            img = img.convert("RGBA") if img.mode in ("P", "LA") else img
            self.original_image = img
        except Exception as e:
            messagebox.showerror(self.t("err_open_title"),
                                 self.t("err_open_msg", error=e))
            return

        self.rotation = 0
        if self.fit_mode:
            self.zoom_factor = self._calc_fit_zoom()
        self._canvas_offset = [0, 0]
        self._render()
        self._update_status()

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
        return min(zx, zy, 1.0)

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
        self.canvas.create_image(x, y, image=self.photo_image, anchor="center")
        self.zoom_var.set(f"{int(self.zoom_factor * 100)}%")

    def _on_canvas_resize(self, event):
        if self.fit_mode and self.original_image:
            self.zoom_factor = self._calc_fit_zoom()
            self._canvas_offset = [0, 0]
            self._render()

    # ═══════════════════ 导航 ═══════════════════

    def prev_image(self):
        if self.image_list:
            self.show_image(self.current_index - 1)

    def next_image(self):
        if self.image_list:
            self.show_image(self.current_index + 1)

    # ═══════════════════ 缩放 ═══════════════════

    def zoom_in(self):
        self.fit_mode = False
        self.zoom_factor = min(self.zoom_factor * 1.25, 20.0)
        self._render()

    def zoom_out(self):
        self.fit_mode = False
        self.zoom_factor = max(self.zoom_factor / 1.25, 0.05)
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
        self.zoom_factor = max(0.05, min(self.zoom_factor * factor, 20.0))
        self._render()

    # ═══════════════════ 旋转 ═══════════════════

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

    # ═══════════════════ 拖拽 ═══════════════════

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

    # ═══════════════════ 全屏 / 置顶 / 无边框 ═══════════════════

    def toggle_fullscreen(self):
        state = self.root.attributes("-fullscreen")
        self.root.attributes("-fullscreen", not state)

    def toggle_always_on_top(self):
        self.always_on_top = not self.always_on_top
        self.root.attributes("-topmost", self.always_on_top)

    def toggle_borderless(self):
        self.borderless_mode = not self.borderless_mode
        self.root.overrideredirect(self.borderless_mode)
        # 让无边框窗口可以拖动移动
        if self.borderless_mode:
            self.root.bind("<ButtonPress-1>", self._borderless_drag_start, add="+")
            self.root.bind("<B1-Motion>", self._borderless_drag_move, add="+")

    def _borderless_drag_start(self, event):
        self._borderless_drag = (event.x, event.y)

    def _borderless_drag_move(self, event):
        if hasattr(self, "_borderless_drag") and self._borderless_drag:
            dx = event.x - self._borderless_drag[0]
            dy = event.y - self._borderless_drag[1]
            x = self.root.winfo_x() + dx
            y = self.root.winfo_y() + dy
            self.root.geometry(f"+{x}+{y}")

    def _on_escape(self, event):
        if self.root.attributes("-fullscreen"):
            self.root.attributes("-fullscreen", False)
        elif self.borderless_mode:
            self.toggle_borderless()

    # ═══════════════════ 幻灯片 ═══════════════════

    def toggle_slideshow(self):
        if not self.image_list:
            return
        self.slideshow_running = not self.slideshow_running
        if self.slideshow_running:
            self._advance_slideshow()
        else:
            if self._slideshow_job:
                self.root.after_cancel(self._slideshow_job)

    def _advance_slideshow(self):
        if not self.slideshow_running:
            return
        self.next_image()
        self._slideshow_job = self.root.after(self.slideshow_delay, self._advance_slideshow)

    # ═══════════════════ 右键菜单功能 ═══════════════════

    def copy_image_to_clipboard(self):
        """复制图片到剪贴板"""
        if not self.original_image or self.current_index < 0:
            return
        try:
            import win32clipboard
            import io

            img = self.original_image.copy()
            if self.rotation:
                img = img.rotate(-self.rotation, expand=True)
            if img.mode == "RGBA":
                bg = Image.new("RGB", img.size, (255, 255, 255))
                bg.paste(img, mask=img.split()[3])
                img = bg
            else:
                img = img.convert("RGB")

            buf = io.BytesIO()
            img.save(buf, format="BMP")
            data = buf.getvalue()[14:]  # skip BMP header

            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
            win32clipboard.CloseClipboard()
            self._show_hint(self.t("hint_copied_img"))
        except ImportError:
            try:
                # fallback: copy file to clipboard
                self.copy_file_to_clipboard()
            except Exception:
                pass
        except Exception as e:
            print(f"Copy error: {e}")

    def copy_file_to_clipboard(self):
        """复制文件到剪贴板"""
        if self.current_index < 0 or not self.image_list:
            return
        try:
            import ctypes
            from ctypes import wintypes

            path_str = str(self.image_list[self.current_index])

            class DROPFILES(ctypes.Structure):
                _fields_ = [
                    ("pFiles", wintypes.DWORD),
                    ("pt", wintypes.POINT),
                    ("fNC", wintypes.BOOL),
                    ("fWide", wintypes.BOOL),
                ]

            # Encode paths as wide string
            encoded = (path_str + "\0").encode("utf-16-le")[2:]

            size = ctypes.sizeof(DROPFILES) + len(encoded)
            mem = ctypes.windll.kernel32.GlobalAlloc(0x0042, size)  # GMEM_MOVEABLE | GHND
            ptr = ctypes.windll.kernel32.GlobalLock(mem)

            df = DROPFILES()
            df.pFiles = ctypes.sizeof(DROPFILES)
            df.pt = wintypes.POINT(0, 0)
            df.fNC = False
            df.fWide = True
            ctypes.memmove(ptr, ctypes.byref(df), ctypes.sizeof(DROPFILES))
            ctypes.memmove(ptr + ctypes.sizeof(DROPFILES), encoded, len(encoded))

            ctypes.windll.kernel32.GlobalUnlock(mem)
            ctypes.windll.user32.OpenClipboard(0)
            ctypes.windll.user32.EmptyClipboard()
            ctypes.windll.user32.SetClipboardData(15, mem)  # CF_HDROP = 15
            ctypes.windll.user32.CloseClipboard()
            self._show_hint(self.t("hint_copied_file"))
        except Exception as e:
            print(f"Copy file error: {e}")

    def copy_path(self):
        if self.current_index < 0 or not self.image_list:
            return
        path_str = str(self.image_list[self.current_index])
        self.root.clipboard_clear()
        self.root.clipboard_append(path_str)
        self._show_hint(self.t("hint_copied_path"))

    def copy_filename(self):
        if self.current_index < 0 or not self.image_list:
            return
        name = self.image_list[self.current_index].name
        self.root.clipboard_clear()
        self.root.clipboard_append(name)
        self._show_hint(self.t("hint_copied_path"))

    def copy_dimensions(self):
        if not self.original_image:
            return
        w, h = self.original_image.size
        dim = f"{w} x {h}"
        self.root.clipboard_clear()
        self.root.clipboard_append(dim)
        self._show_hint(self.t("hint_copied_path"))

    def save_as(self):
        if not self.original_image or self.current_index < 0:
            return
        src = self.image_list[self.current_index]
        default_name = src.stem + "_copy" + src.suffix
        path = filedialog.asksaveasfilename(
            title=self.t("dlg_save_as"),
            initialfile=default_name,
            defaultextension=src.suffix,
            filetypes=[(self.t("ftype_images"), "*" + src.suffix)]
        )
        if path:
            try:
                img = self.original_image.copy()
                if self.rotation:
                    img = img.rotate(-self.rotation, expand=True)
                img.save(path)
                self._show_hint(self.t("hint_saved_as", path=path))
            except Exception as e:
                messagebox.showerror(self.t("err_save_title"), str(e))

    def print_image(self):
        if not self.original_image or self.current_index < 0:
            return
        try:
            import tempfile
            img = self.original_image.copy()
            if self.rotation:
                img = img.rotate(-self.rotation, expand=True)

            tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            img.convert("RGB").save(tmp.name)
            tmp.close()

            os.startfile(tmp.name, "print")
        except Exception as e:
            messagebox.showerror(self.t("err_print_title"), str(e))

    def open_in_explorer(self):
        if self.current_index < 0 or not self.image_list:
            return
        path = self.image_list[self.current_index]
        subprocess.Popen(["explorer", "/select,", str(path)])

    def open_with_default(self):
        if self.current_index < 0 or not self.image_list:
            return
        os.startfile(str(self.image_list[self.current_index]))

    def open_with_paint(self):
        if self.current_index < 0 or not self.image_list:
            return
        subprocess.Popen(["mspaint", str(self.image_list[self.current_index])])

    # ═══════════════════ 设置 ═══════════════════

    def show_settings(self):
        top = tk.Toplevel(self.root)
        top.title(self.t("dlg_title_settings"))
        top.geometry("400x280")
        top.configure(bg=BG_COLOR)
        top.transient(self.root)
        top.grab_set()
        top.resizable(False, False)

        # 居中
        top.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - 400) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - 280) // 2
        top.geometry(f"+{x}+{y}")

        frame = tk.Frame(top, bg=BG_COLOR, padx=24, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # 语言选择
        tk.Label(frame, text=self.t("set_language"), bg=BG_COLOR, fg=TEXT_PRIMARY,
                 font=("Microsoft YaHei UI", 11)).grid(row=0, column=0, sticky="w", pady=(0, 4))
        lang_var = tk.StringVar(value=self.i18n.lang)
        lang_combo = ttk.Combobox(frame, textvariable=lang_var,
                                   values=list(I18n.LANGUAGES.values()), state="readonly", width=20)
        lang_combo.grid(row=1, column=0, sticky="w", pady=(0, 16))

        # 幻灯片速度
        tk.Label(frame, text=self.t("set_slideshow_speed"), bg=BG_COLOR, fg=TEXT_PRIMARY,
                 font=("Microsoft YaHei UI", 11)).grid(row=2, column=0, sticky="w", pady=(0, 4))
        speed_var = tk.IntVar(value=self.slideshow_delay // 1000)
        speed_spin = tk.Spinbox(frame, from_=1, to=30, textvariable=speed_var, width=10,
                                font=("Microsoft YaHei UI", 10))
        speed_spin.grid(row=3, column=0, sticky="w", pady=(0, 16))

        # 启动时打开上次文件夹
        reopen_var = tk.BooleanVar(value=self.config.get("reopen_last_folder", True))
        cb = tk.Checkbutton(frame, text=self.t("set_startup_folder"), variable=reopen_var,
                            bg=BG_COLOR, fg=TEXT_PRIMARY, selectcolor=BG_COLOR,
                            activebackground=BG_COLOR, font=("Microsoft YaHei UI", 10))
        cb.grid(row=4, column=0, sticky="w", pady=(0, 20))

        # 按钮
        btn_frame = tk.Frame(frame, bg=BG_COLOR)
        btn_frame.grid(row=5, column=0, sticky="e")
        tk.Button(btn_frame, text=self.t("set_close"), command=top.destroy,
                  bg=PANEL_COLOR, fg=TEXT_PRIMARY, relief=tk.FLAT,
                  font=("Microsoft YaHei UI", 10), padx=16, pady=6).pack(side=tk.RIGHT, padx=(8, 0))
        tk.Button(btn_frame, text=self.t("set_ok"),
                  command=lambda: self._apply_settings(top, lang_var.get(), speed_var.get(), reopen_var.get()),
                  bg=ACCENT_COLOR, fg="#FFFFFF", relief=tk.FLAT,
                  font=("Microsoft YaHei UI", 10), padx=16, pady=6).pack(side=tk.RIGHT)

    def _apply_settings(self, dialog, lang_display: str, speed: int, reopen: bool):
        # 反查语言代码
        code_map = {v: k for k, v in I18n.LANGUAGES.items()}
        lang_code = code_map.get(lang_display, self.i18n.lang)

        self.slideshow_delay = speed * 1000
        self.config["slideshow_speed"] = speed
        self.config["reopen_last_folder"] = reopen
        save_config(self.config)

        dialog.destroy()
        if lang_code != self.i18n.lang:
            self.change_language(lang_code)

    # ═══════════════════ 信息 & 删除 ═══════════════════

    def show_info(self):
        if not self.original_image or self.current_index < 0:
            messagebox.showinfo(self.t("info_title"), self.t("info_open_first"))
            return
        path = self.image_list[self.current_index]
        stat = path.stat()
        w, h = self.original_image.size
        size_kb = stat.st_size / 1024
        sep = self._sep
        import datetime
        mtime = datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        info = (
            f"{self.t('label_filename')}{sep}{path.name}\n"
            f"{self.t('label_path')}{sep}{path.parent}\n"
            f"{self.t('label_resolution')}{sep}{w} \u00d7 {h} px\n"
            f"{self.t('label_filesize')}{sep}{size_kb:.1f} KB\n"
            f"{self.t('label_format')}{sep}{self.original_image.format or self.t('label_unknown')}\n"
            f"{self.t('label_colormode')}{sep}{self.original_image.mode}\n"
            f"{self.t('label_modified')}{sep}{mtime}"
        )
        messagebox.showinfo(self.t("info_title"), info)

    def delete_image(self):
        if not self.image_list or self.current_index < 0:
            return
        path = self.image_list[self.current_index]
        if not messagebox.askyesno(
                self.t("confirm_del"),
                self.t("confirm_del_msg", name=path.name)):
            return
        try:
            os.remove(path)
        except Exception as e:
            messagebox.showerror(self.t("err_del_title"), str(e))
            return
        self.image_list.pop(self.current_index)
        if not self.image_list:
            self.current_index = -1
            self.original_image = None
            self._show_welcome()
            self._update_status()
        else:
            idx = min(self.current_index, len(self.image_list) - 1)
            self.show_image(idx)
        self._show_hint(self.t("hint_deleted", name=path.name))

    # ═══════════════════ 状态栏 & 提示 ═══════════════════

    def _update_status(self):
        if not self.image_list or self.current_index < 0:
            self.status_var.set(self.t("status_ready"))
            return
        path = self.image_list[self.current_index]
        total = len(self.image_list)
        self.status_var.set(
            f"{self.current_index + 1} / {total}   \u00b7   {path.name}"
        )

    def _show_hint(self, msg: str):
        """底部状态栏短暂显示提示信息"""
        old = self.status_var.get()
        self.status_var.set(msg)
        self.root.after(2500, lambda: self._update_status())

    # ═══════════════════ 退出 ═══════════════════

    def on_exit(self):
        if self.slideshow_running:
            self.slideshow_running = False
            if self._slideshow_job:
                self.root.after_cancel(self._slideshow_job)
        self.root.quit()


# ──────────────────────────── 入口 ────────────────────────────

def main():
    root = tk.Tk()

    # 图标
    icon_path = Path(__file__).parent / "icon.ico"
    if icon_path.exists():
        try:
            root.iconbitmap(str(icon_path))
        except Exception:
            pass

    app = CFKViewer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
