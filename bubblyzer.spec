# -*- mode: python ; coding: utf-8 -*-
import sys
import os

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=['src', '.'],
    binaries=[],
    datas=[
        ('models/comic-speech-bubble-detector.onnx', 'models'),
        ('affinity/affinity_bubblyzer.js', 'affinity'),
        ('assets/*', 'assets')
    ],
    hiddenimports=[
        'onnxruntime',
        'pystray',
        'pystray._win32',
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw',
        'cv2',
        'flask',
        'werkzeug',
        'jinja2'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'torch', 'ultralytics', 'torchvision', 'scipy', 'matplotlib', 'pandas', 'sympy', 'networkx'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Bubblyzer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Silent tray execution without black console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/app_icon.ico'
)
