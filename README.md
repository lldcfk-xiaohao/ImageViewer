# ImageViewer 🖼

> 一款基于 Python + tkinter + Pillow 的轻量看图软件，界面简洁、功能齐全。

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-green.svg)](https://python.org)

---

## 功能特性

| 功能 | 说明 |
|------|------|
| 📂 打开文件 / 文件夹 | 支持单文件或整个文件夹批量加载 |
| ⬅ ➡ 图片导航 | 上一张 / 下一张，键盘左右方向键 |
| 🔍 缩放 | 鼠标滚轮 / 按钮放大缩小，最高 2000% |
| ⬜ 适应窗口 | 自动缩放至适合当前窗口大小 |
| 1:1 原始大小 | 恢复 100% 显示 |
| ↺ ↻ 旋转 | 左转 / 右转各 90° |
| 🖱 拖拽平移 | 鼠标左键拖拽移动图片 |
| ▶ 幻灯片播放 | 每 3 秒自动切换下一张 |
| ⛶ 全屏 | F11 切换全屏，ESC 退出 |
| 🗑 删除 | 一键删除当前图片（需二次确认） |
| ℹ 图片信息 | 显示分辨率、大小、格式、修改时间 |
| 缩略图面板 | 左侧实时缩略图，点击快速跳转 |
| EXIF 自动纠正 | 自动修正手机拍照的旋转方向 |

## 支持格式

`.jpg` `.jpeg` `.png` `.gif` `.bmp` `.webp` `.tiff` `.ico` `.ppm` `.pgm` `.pbm` `.pnm`

## 快速开始

### 安装依赖

```bash
pip install Pillow
```

### 运行

```bash
python viewer.py
```

### （可选）打包为 EXE

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=icon.ico viewer.py
```

打包完成后，`dist/viewer.exe` 即可独立运行，无需安装 Python。

## 键盘快捷键

| 按键 | 功能 |
|------|------|
| `←` / `→` | 上一张 / 下一张 |
| `Space` | 下一张 |
| `↑` / `↓` | 放大 / 缩小 |
| `F11` | 全屏 |
| `ESC` | 退出全屏 |
| `R` | 右转 90° |
| `L` | 左转 90° |
| `F` | 适应窗口 |
| `1` | 原始大小 (1:1) |
| `S` | 开始 / 停止幻灯片 |
| `Delete` | 删除当前图片 |
| `Ctrl+O` | 打开文件 |

## 项目结构

```
image-viewer/
├── viewer.py       # 主程序
├── icon.ico        # 程序图标（可选）
├── LICENSE         # MIT 许可证
└── README.md       # 本文件
```

## 开发环境

- Python 3.9+
- Pillow >= 9.0

## 许可证

本项目使用 [MIT License](LICENSE) 开源，欢迎 Fork、修改和商业使用。

---

Made with ❤️ by [lldcfk-xiaohao](https://github.com/lldcfk-xiaohao)
