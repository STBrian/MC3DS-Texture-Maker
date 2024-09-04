# -*- mode: python ; coding: utf-8 -*-

# Custom code to detect from extern script if build debug or release
import sys, os

with open("./release_type.txt", "r") as f:
    release_type = f.read().split("\n")[0]

if release_type == "debug":
    CONSOLE = True
elif release_type == "release":
    CONSOLE = False
else:
    print("Unknown release:", release_type)
    sys.exit(1)
# End custom code

main_datas = [
    ("assets", "assets"),
    ("icon.ico", "."),
    ("icon.png", "."),
    ("icon2.png", ".")
]
main_hiddenimports = ["PIL", "PIL._imagingtk", "PIL._tkinter_finder", "pkg_resources.extern"]

main_a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=main_datas,
    hiddenimports=main_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
main_pyz = PYZ(main_a.pure)
main_exe = EXE(
    main_pyz,
    main_a.scripts,
    [],
    exclude_binaries=True,
    name='MC3DS-Texture-Maker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=CONSOLE,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='./icon.ico'
)

py3dst_hiddenimports = ["PIL", "PIL._imagingtk", "PIL._tkinter_finder", "pkg_resources.extern"]

py3dst_a = Analysis(
    ['py3dstViewer.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=py3dst_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
py3dst_pyz = PYZ(py3dst_a.pure)
py3dst_exe = EXE(
    py3dst_pyz,
    py3dst_a.scripts,
    [],
    exclude_binaries=True,
    name='py3dstViewer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=CONSOLE,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='./icon.ico'
)

coll = COLLECT(
    main_exe,
    main_a.binaries,
    main_a.datas,
    py3dst_exe,
    py3dst_a.binaries,
    py3dst_a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MC3DS-Texture-Maker',
)
