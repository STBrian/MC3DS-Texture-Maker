import os
from PIL import Image

from . import tex3dst

def getItemsFromIndexFile(filename):
    items = []
    with open(filename, "r") as f:
        content = f.read()
        items = content.split("\n")
    
    return items

def deleteMatches(list1: list, list2: list):
    matches = []
    for i in range(0, len(list1)):
        if not (list1[i] in list2):
            matches.append(list1[i])

    return matches

def checkForMatch(value, list1: list):
    position = -1
    for i in range(0, len(list1)):
        if value == list1[i]:
            position = i

    return position

def checkForMatches(list1: list, list2: list):
    matches = []
    for i in range(0, len(list1)):
        if list1[i] in list2:
            matches.append(list1[i])

    return matches

def calculateGrid(value: int, grid_width: int, grid_height: int, cube_lenght: int):
    x_grid = value - ((value // grid_width) * grid_width)
    y_grid = value // grid_width
    if y_grid > grid_height:
        return -1
    x = x_grid * cube_lenght
    y = y_grid * cube_lenght

    return (x, y)

def isImage16x16(texture_path):
    img = Image.open(texture_path)
    if img.size[0] == 16 and img.size[1] == 16:
        img.close()
        return True
    else:
        img.close()
        return False

def createOutputDirectory(directoryName):
    if not os.path.exists(directoryName):
        os.makedirs(directoryName)

def addElementToFile(value, filePath: str):
    if os.path.exists(filePath):
        with open(filePath, "a") as f:
            f.write(f"{value}\n")
        return
    else:
        file = open(filePath, "w")
        file.write(f"{value}\n")

def addToItemAtlas(pixelPosition, textureImgPath, sourceFolder, output_folder):
    # Carga los archivos necesarios a la memoria
    if os.path.exists(f"{output_folder}/atlas/atlas.items.meta_79954554_0.3dst"):
        print("Opening modified atlas...")
        itemAtlas = tex3dst.load(f"{output_folder}/atlas/atlas.items.meta_79954554_0.3dst")
        # El archivo previamente debe estar de cabeza entonces hay que voltearlo para usarlo normal
        itemAtlas.flipX()
    else:
        print("Creating new atlas file...")
        itemAtlas = tex3dst.new(512, 256, 1)
        print("Opening atlas from assets...")
        itemAtlasSource = Image.open(f"{sourceFolder}/atlas/atlas.items.vanilla.png").convert("RGBA")
        x = 0
        y = 0
        for i in range(0, itemAtlasSource.size[1]):
            for j in range(0, itemAtlasSource.size[0]):
                r, g, b, a = itemAtlasSource.getpixel((x, y))
                itemAtlas.setPixelRGBA(x, y, r, g, b, a)
                x += 1
            x = 0
            y += 1

        itemAtlasSource.close()

    print("Opening new texture...")
    textureImg = Image.open(textureImgPath).convert("RGBA")
        
    # Define las variables de posición
    x_atlas = pixelPosition[0]
    y_atlas = pixelPosition[1]

    # Reemplazar la textura original por la nueva
    print("Replacing new texture...")
    x = 0
    y = 0
    for i in range(0, 16):
        for i in range(0, 16):
            r, g, b, a = textureImg.getpixel((x, y))
            itemAtlas.setPixelRGBA(x_atlas, y_atlas, r, g, b, a)
            x += 1
            x_atlas += 1
        x = 0
        x_atlas -= 16
        y += 1
        y_atlas += 1

    # Crea el directorio de salida si no existe
    if not os.path.exists(f"{output_folder}/atlas"):
        createOutputDirectory(f"{output_folder}/atlas")

    # Invierte el atlas en el eje x y convierte los datos del atlas antes de exportarlos
    print("Inverting x-axis atlas...")
    itemAtlas.flipX()
    print("Converting data...")
    itemAtlas.convertData()

    # Guarda el atlas modificado
    print("Saving changes...")
    itemAtlas.export(f"{output_folder}/atlas/atlas.items.meta_79954554_0.3dst")

    return True

def addToBlockAtlas(pixelPosition, textureImgPath, sourceFolder, output_folder):
    # Carga los archivos necesarios a la memoria
    print("Starting...")
    if os.path.exists(f"{output_folder}/atlas/atlas.terrain.meta_79954554_0.3dst"):
        print("Opening modified atlas...")
        blockAtlas = tex3dst.load(f"{output_folder}/atlas/atlas.terrain.meta_79954554_0.3dst")
        # El archivo previamente debe estar de cabeza entonces hay que voltearlo para usarlo normal
        blockAtlas.flipX()
    else:
        print("Creating new texture file...")
        blockAtlas = tex3dst.new(512, 512, 3)
        print("Opening atlas from assets...")
        blockAtlasSource = Image.open(f"{sourceFolder}/atlas/atlas.terrain.vanilla.png").convert("RGBA")
        x = 0
        y = 0
        for i in range(0, blockAtlasSource.size[1]):
            for j in range(0, blockAtlasSource.size[0]):
                r, g, b, a = blockAtlasSource.getpixel((x, y))
                blockAtlas.setPixelRGBA(x, y, r, g, b, a)
                x += 1
            x = 0
            y += 1

        blockAtlasSource.close()

    print("Opening new texture...")
    textureImg = Image.open(textureImgPath).convert("RGBA")
        
    # Define las variables de posición
    x_atlas = pixelPosition[0]
    y_atlas = pixelPosition[1]

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
            r, g, b, a = textureImg.getpixel((x2, y2))
            blockAtlas.setPixelRGBA(x_atlas, y_atlas, r, g, b, a)
            x += 1
            x_atlas += 1
        x = -2
        x_atlas -= 20
        y += 1
        y_atlas += 1

    # Crea el directorio de salida si no existe
    if not os.path.exists(f"{output_folder}/atlas"):
        createOutputDirectory(f"{output_folder}/atlas")

    # Invierte el atlas en el eje x y convierte los datos del atlas antes de exportarlos
    print("Inverting x-axis atlas...")
    blockAtlas.flipX()
    print("Converting data...")
    blockAtlas.convertData()

    # Guarda el atlas modificado
    print("Saving changes...")
    blockAtlas.export(f"{output_folder}/atlas/atlas.terrain.meta_79954554_0.3dst")

    return True