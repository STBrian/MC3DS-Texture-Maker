@ECHO OFF
if exist build\ (
    del /S /Q build\\*
    rmdir /S /Q build
)
if exist dist\ (
    del /S /Q dist\\*
    rmdir /S /Q dist
)
pyinstaller --onefile --hide-console minimize-late --icon icon.ico --add-data assets:assets --add-data icon.ico:. --add-data icon.png:. --add-data icon2.png:. --hidden-import PIL --hidden-import PIL._imagingtk --hidden-import PIL._tkinter_finder mc3ds-tm-gui.py
del mc3ds-tm-gui.spec