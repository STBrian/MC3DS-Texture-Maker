@ECHO OFF
if exist build\ (
    del /S /Q build\\*
    rmdir /S /Q build
)
if exist dist\ (
    del /S /Q dist\\*
    rmdir /S /Q dist
)
pyinstaller mc3ds-tm.spec
pyinstaller mc3ds-tm-gui.spec
pause