from src.tex3dst import *
from PIL import Image

image = Image.open("atlas.png").convert("RGBA")
texture = NewTexture3dst(512, 256, 1)
x = 0
y = 0
for i in range(0, 256):
    for j in range(0, 512):
        r, g, b, a = image.getpixel((x, y))
        texture.setPixelRGBA(x, y, r, g, b, a)
        x += 1
    x = 0
    y += 1
print(len(texture.data))
print(texture.getPixelData(0, 0))
texture.convertData()
texture.export("out.3dst")