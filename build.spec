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
os.remove("./release_type.txt")
# End custom code

main_datas = [
    ("assets", "assets"),
    ("icon_viewer.ico", "."),
    ("icon_viewer.png", ".")
]
main_hiddenimports = ["PIL", "PIL._imagingtk", "PIL._tkinter_finder", "pkg_resources.extern"]

main_a = Analysis( # type: ignore
    ['src/main.py'],
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
main_pyz = PYZ(main_a.pure) # type: ignore
main_exe = EXE( # type: ignore
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
    icon='./assets/icon.ico'
)

py3dst_hiddenimports = ["PIL", "PIL._imagingtk", "PIL._tkinter_finder", "pkg_resources.extern"]

py3dst_a = Analysis( # type: ignore
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
py3dst_pyz = PYZ(py3dst_a.pure) # type: ignore
py3dst_exe = EXE( # type: ignore
    py3dst_pyz,
    py3dst_a.scripts,
    [],
    exclude_binaries=True,
    name='3DSTViewer',
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
    icon='./icon_viewer.ico'
)

coll = COLLECT( # type: ignore
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
