# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config.py', '.'),
        ('requirements.txt', '.'),
        ('README.md', '.'),
        ('controllers', 'controllers'),
        ('database', 'database'),
        ('ui', 'ui'),
        ('utils', 'utils'),
        ('views', 'views'),
    ],
    hiddenimports=[
        'customtkinter',
        'PIL',
        'PIL._tkinter_finder',
        'tkinter',
        'sqlite3',
        'hashlib',
        'datetime',
        'json',
        're',
        'calendar',
        'threading',
        'webbrowser',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='SamirPOS',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # إخفاء نافذة الكونسول
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.png',
)
