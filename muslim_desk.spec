# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for Muslim Desk

import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# Bundle timezonefinder boundary data + tzdata zone files
_extra_datas = collect_data_files('timezonefinder')
_extra_datas += collect_data_files('tzdata')

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        ('src', 'src'),
    ] + _extra_datas,
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.QtSvg',
        'PyQt6.sip',
        'requests',
        'requests.adapters',
        'requests.packages',
        'urllib3',
        'certifi',
        'charset_normalizer',
        'idna',
        'hijri_converter',
        'timezonefinder',
        'zoneinfo',
        'tzdata',
        'winsound',
        'winreg',
        'json',
        'dataclasses',
        'threading',
        'math',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'unittest',
        'test',
        'setuptools',
        'pip',
        'numpy',
        'pandas',
        'matplotlib',
        'scipy',
        'PIL',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MuslimDesk',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,          # no console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico',
    version=None,
    uac_admin=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MuslimDesk',
)
