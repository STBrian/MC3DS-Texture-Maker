#!/bin/bash

if [ -d ./build ]
then
rm -r ./build
fi

if [ -d ./dist ]
then
rm -r ./dist
fi

python3.12 -m PyInstaller --onefile --hide-console hide-early --add-data assets:assets --add-data icon.ico:. --add-data icon.png:. --add-data icon2.png:. --hidden-import PIL --hidden-import PIL._imagingtk --hidden-import PIL._tkinter_finder mc3dstm.py
python3.12 -m PyInstaller --onefile --windowed --icon icon.ico --hidden-import PIL --hidden-import PIL._imagingtk --hidden-import PIL._tkinter_finder py3dstViewer.py
rm mc3ds-tm.spec
rm 3dstViewer.spec