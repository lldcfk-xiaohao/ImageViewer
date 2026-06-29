# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

block_cipher = None

a = Analysis(
    ['viewer.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['PIL', 'PIL.Image', 'PIL.ImageTk', 'PIL.ExifTags', 'tkinter', 'tkinter.ttk', 'tkinter.filedialog', 'tkinter.messagebox'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'scipy', 'pandas'],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

icon_path = str(Path(SPECPATH) / 'icon.ico') if (Path(SPECPATH) / 'icon.ico').exists() else 'NONE'

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='GuoheView',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon=icon_path,
    version=None,
)
