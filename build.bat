@ECHO OFF
if exist build\ (
    del /S /Q build\\*
    rmdir /S /Q build
)
if exist dist\ (
    del /S /Q dist\\*
    rmdir /S /Q dist
)
pyinstaller --onefile --icon icon.ico --add-data assets:assets --add-data modules:modules --add-data icon.ico:. --add-data icon.png:. --hidden-import PIL --hidden-import PIL._imagingtk --hidden-import PIL._tkinter_finder mc3ds-tm.py
pyinstaller --onefile --hide-console hide-early --icon icon.ico --add-data assets:assets --add-data modules:modules --add-data icon.ico:. --add-data icon.png:. --hidden-import PIL --hidden-import PIL._imagingtk --hidden-import PIL._tkinter_finder mc3ds-tm-gui.py
del mc3ds-tm.spec
del mc3ds-tm-gui.spec