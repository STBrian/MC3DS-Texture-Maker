from PIL import Image

def separar2(texto: str):
    partes = [texto[i:i+2] for i in range(0, len(texto), 2)]
    return partes

colors = ["79c05a", "8ab689", "bfb755", "59c93c", "55c93f", "88bb66", "86b87f", "64c73f", "86b783", "83b593", "80b497", "91bd59", "90814d", "8eb971", "6a7039", "507a32"]

for color in colors:
    r, g, b = separar2(color)
    r = int.from_bytes(bytes.fromhex(r))
    g = int.from_bytes(bytes.fromhex(g))
    b = int.from_bytes(bytes.fromhex(b))

    dirt_texture = Image.open("dirt.png").convert("RGBA")
    overlay_texture = Image.open("grass_block_side_overlay.png").convert("LA")
    w, h = overlay_texture.size
    pixels = overlay_texture.load()
    dirtPixels = dirt_texture.load()
    for i in range(h):
        for j in range(w):
            gray, a = pixels[j, i]
            if a != 0:
                r2 = int((gray / 255)*r)
                g2 = int((gray / 255)*g)
                b2 = int((gray / 255)*b)
                dirtPixels[j, i] = (r2, g2, b2, a)
                print(dirtPixels[j, i])

    dirt_texture.save(f"grass_block_side_{color}.png")