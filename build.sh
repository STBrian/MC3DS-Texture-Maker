#!/bin/bash

if [ -d ./build ]
then
rm -r ./build
fi

if [ -d ./dist ]
then
rm -r ./dist
fi

python3.11 -m PyInstaller --onefile --add-data assets:assets --add-data modules:modules --add-data icon.ico:. --add-data icon.png:. --hidden-import PIL --hidden-import PIL._imagingtk --hidden-import PIL._tkinter_finder mc3ds-tm.py
python3.11 -m PyInstaller --onefile --hide-console hide-early --add-data assets:assets --add-data modules:modules --add-data icon.ico:. --add-data icon.png:. --hidden-import PIL --hidden-import PIL._imagingtk --hidden-import PIL._tkinter_finder mc3ds-tm-gui.py

rm mc3ds-tm.spec
rm mc3ds-tm-gui.spec