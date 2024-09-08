import os
from pathlib import Path
from PIL import Image

from py3dst import Texture3dst

class atlasTexture3dst():
    def __init__(self):
        pass

    def open(self, path: str | Path, atlas_type: str):
        if type(path) == str:
            path = Path(path)
        if not isinstance(path, Path):
            raise TypeError("Expected str or Path type for path.")
        if not atlas_type in ["Items", "Blocks"]:
            raise ValueError("Expected 'Items' or 'Blocks' type for atlas_type.")

        print("Opening atlas...")
        atlas = None
        if path.suffix == ".png":
            atlas = Texture3dst().fromImage(Image.open(path))
            if atlas_type == "Blocks":
                atlas.miplevel = 3
        elif path.suffix == ".3dst":
            atlas = Texture3dst().open(path)

        self.atlas = atlas
        self.atlas_type = atlas_type

        return self

    def addElement(self, position: tuple | list, new_texture: Image.Image):
        new_texture = new_texture.convert("RGBA")

        # Define las variables de posición
        x_atlas = position[0]
        y_atlas = position[1]

        if self.atlas_type == "Items":
            # Reemplazar la textura original por la nueva
            print("Replacing texture...")
            x = 0
            y = 0
            for y in range(0, 16):
                for x in range(0, 16):
                    r, g, b, a = new_texture.getpixel((x, y))
                    self.atlas.setPixelRGBA(x_atlas, y_atlas, (r, g, b, a))
                    x_atlas += 1
                x_atlas -= 16
                y_atlas += 1
        elif self.atlas_type == "Blocks":
            # Reemplazar la textura original por la nueva
            print("Replacing texture...")
            x = -2
            y = -2
            x2 = 0
            y2 = 0
            for i in range(0, 20):
                for i in range(0, 20):
                    if x < 0:
                        x2 = 0
                    if x > 15:
                        x2 = 15
                    if y < 0:
                        y2 = 0
                    if y > 15:
                        y2 = 15
                    if x >= 0 and x <= 15:
                        x2 = x
                    if y >= 0 and y <= 15:
                        y2 = y
                    r, g, b, a = new_texture.getpixel((x2, y2))
                    self.atlas.setPixelRGBA(x_atlas, y_atlas, (r, g, b, a))
                    x += 1
                    x_atlas += 1
                x = -2
                x_atlas -= 20
                y += 1
                y_atlas += 1
        print("Texture replaced")

    def save(self, path: str | Path):
        if type(path) == str:
            path = Path(path)
        if not isinstance(path, Path):
            raise TypeError("Expected str or Path type for path.")
        
        if not os.path.exists(path.parent):
            os.makedirs(path.parent)

        print("Saving atlas...")
        self.atlas.export(path)
        print("Success")

class IndexFile():
    def __init__(self):
        pass
    
    def new(self):
        self.items = []
        return self

    def open(self, fp: str | Path):
        if type(fp) == str:
            fp = Path(fp)
        if not isinstance(fp, Path):
            raise TypeError("Expected str or Path type for fp.")
        
        with open(fp, "r") as f:
            content = f.read()
            self.items = content.split("\n")

        return self
    
    def getItems(self) -> list:
        return self.items
    
    def addItem(self, value: str):
        value = str(value)
        self.items.append(value)

    def save(self, path: str | Path):
        if type(path) == str:
            path = Path(path)
        if not isinstance(path, Path):
            raise TypeError("Expected str or Path type for path.")
        
        if not os.path.exists(path.parent):
            os.makedirs(path.parent)

        outstr = ""
        for element in self.items:
            if len(element) != 0:
                outstr += str(element) + "\n"

        with open(path, "w") as f:
            f.write(outstr)

def calculateGrid(value: int, grid_width: int, grid_height: int, cube_lenght: int):
    x_grid = value - ((value // grid_width) * grid_width)
    y_grid = value // grid_width
    if y_grid > grid_height:
        return -1
    x = x_grid * cube_lenght
    y = y_grid * cube_lenght

    return (x, y)