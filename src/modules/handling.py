import os
from pathlib import Path
from PIL import Image

try:
    from py3dst.py3dst_exp import Texture3dst
except:
    from py3dst import Texture3dst

class atlasTexture3dst():
    def __init__(self):
        pass

    def open(self, path: str | Path, tile_padding: int):
        if type(path) == str:
            path = Path(path)
        if not isinstance(path, Path):
            raise TypeError("Expected str or Path type for path.")
        if not isinstance(tile_padding, int):
            raise ValueError("Expected int type for tile_padding.")

        print("Opening atlas...")
        atlas = Texture3dst.open(str(path))

        self.atlas = atlas
        self.tile_padding = tile_padding
        return self
    
    def cropToImage(self, x1, y1, x2, y2):
        return self.atlas.crop(x1, y1, x2, y2).toImage()

    def addElement(self, position: tuple | list, new_texture: Image.Image):
        new_texture = new_texture.convert("RGBA")

        x1_pos = position[0]
        y1_pos = position[1]
        x2_pos = position[2]
        y2_pos = position[3]
        width = x2_pos - x1_pos
        height = y2_pos - y1_pos

        print("Replacing texture...")
        x_atlas = x1_pos - self.tile_padding
        y_atlas = y1_pos - self.tile_padding
        x2_atlas = x_atlas
        y2_atlas = y_atlas
        x = -self.tile_padding
        y = -self.tile_padding
        x2 = 0
        y2 = 0
        for i in range(0, height + self.tile_padding*2):
            for j in range(0, width + self.tile_padding*2):
                if x < 0:
                    x2 = 0
                elif x >= width:
                    x2 = width - 1
                else:
                    x2 = x

                if y < 0:
                    y2 = 0
                elif y >= height:
                    y2 = height - 1
                else:
                    y2 = y
                    
                if x_atlas < 0:
                    x2_atlas = 0
                elif x_atlas >= self.atlas.size[0]:
                    x2_atlas = self.atlas.size[0] - 1
                else:
                    x2_atlas = x_atlas
                
                if y_atlas < 0:
                    y2_atlas = 0
                elif y_atlas >= self.atlas.size[1]:
                    y2_atlas = self.atlas.size[1] - 1
                else:
                    y2_atlas = y_atlas

                self.atlas.setPixel(x2_atlas, y2_atlas, new_texture.getpixel((x2, y2)))
                x += 1
                x_atlas += 1
            x = -self.tile_padding
            x_atlas -= width + self.tile_padding*2
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