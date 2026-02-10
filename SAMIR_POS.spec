# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['E:\\xamp\\htdocs\\samir\\ni1\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('E:\\xamp\\htdocs\\samir\\ni1\\views', 'views/'), ('E:\\xamp\\htdocs\\samir\\ni1\\utils', 'utils/'), ('E:\\xamp\\htdocs\\samir\\ni1\\ui', 'ui/'), ('E:\\xamp\\htdocs\\samir\\ni1\\database', 'database/'), ('E:\\xamp\\htdocs\\samir\\ni1\\controllers', 'controllers/'), ('E:\\xamp\\htdocs\\samir\\ni1\\back\\data.py', '.'), ('E:\\xamp\\htdocs\\samir\\mr\\assets', 'assets/'), ('E:\\xamp\\htdocs\\samir\\mr\\models', 'models/')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='SAMIR_POS',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['E:\\xamp\\htdocs\\samir\\mr\\icon.ico'],
    contents_directory='POS_SYSTEM',
)
