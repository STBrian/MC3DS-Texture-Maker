from src.tex3dst import *
from PIL import Image

image = Image.open("src/atlas/atlas.terrain.meta_79954554_0.png").convert("RGBA")
texture = Texture3dst().new(512, 512, 3)

x = 0
y = 0
for i in range(0, 512):
    for j in range(0, 512):
        r, g, b, a = image.getpixel((x, y))
        texture.setPixelRGBA(x, y, r, g, b, a)
        x += 1
    x = 0
    y += 1
texture.convertData()
texture.export("atlas.terrain.meta_79954554_0.3dst")

tex = Texture3dst().open("atlas.terrain.meta_79954554_0.3dst")
tex.convertData()
tex.export("apple2.3dst")
