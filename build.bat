@ECHO OFF
if exist build\ (
    del /S /Q build\\*
    rmdir /S /Q build
)
if exist dist\ (
    del /S /Q dist\\*
    rmdir /S /Q dist
)
pyinstaller --name=MC3DS-Texture-Maker --onefile --hide-console hide-early --icon icon.ico --add-data assets:assets --add-data icon.ico:. --add-data icon.png:. --add-data icon2.png:. --hidden-import PIL --hidden-import PIL._imagingtk --hidden-import PIL._tkinter_finder --hidden-import pkg_resources.extern main.py
pyinstaller --name=3DST-Viewer --onefile --windowed --icon icon.ico --hidden-import PIL --hidden-import PIL._imagingtk --hidden-import PIL._tkinter_finder --hidden-import pkg_resources.extern py3dstViewer.py
del MC3DS-Texture-Maker.spec
del 3DST-Viewer.spec