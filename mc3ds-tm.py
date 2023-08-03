import os
from PIL import Image
from tkinter import Tk
from tkinter import filedialog

def clear():
    os.system('cls')

def createOutputDirectory(directoryName):
    if not os.path.exists(directoryName):
        os.mkdir(directoryName)

def getItemsFromIndexFile(filename):
    items = []
    with open(filename, "r") as f:
        content = f.read()
        items = content.split("\n")
    
    return items

def printMenu():
    print("Choose an option:")
    print("\t1: Change an item texture")
    print("\t2: Change a block texture")
    print("\t3: Exit")

def convertImageTo3dst(path):
    img = Image.open(path).convert('RGBA')
    width, height = img.size
    if width == 16 and height == 16:
        flip_img = img.transpose(Image.FLIP_TOP_BOTTOM)

        outputData = [51, 68, 83, 84, 3, 0, 0, 0, 0, 0, 0, 0, 16, 0, 0, 0, 16, 0, 0, 0, 16, 0, 0, 0, 16, 0, 0, 0, 1, 0, 0, 0]

        x = 0
        y = 0
        for i in range(0, 2):
            for i in range(0, 2):
                for i in range(0, 2):
                    for i in range(0, 2):
                        for i in range(0, 2):
                            for i in range(0, 2):
                                for i in range(0, 2):
                                    for i in range(0, 2):
                                        r, g, b, a = flip_img.getpixel((x, y))
                                        print(r, g, b, a)

                                        outputData.append(a)
                                        if a != 0:
                                            outputData.append(b)
                                            outputData.append(g)
                                            outputData.append(r)
                                        else:
                                            for i in range(0, 3):
                                                outputData.append(0)

                                        x += 1
                                    y += 1
                                    x -= 2
                                y -= 2
                                x += 2
                            y += 2
                            x -= 4
                        y -= 4
                        x += 4
                    y += 4
                    x -= 8
                y -= 8
                x += 8
            y += 8
            x -= 16

        byte_arr = bytearray(outputData)

        return byte_arr, outputData
    else:
        return None, None

def addToItemAtlas(itemData, itemImgPath, output_folder):
    # Establece variables necesarias para la conversión
    x_offset = int(itemData[2])
    y_offset = int(itemData[1])

    # Carga los archivos necesarios a la memoria
    if os.path.exists(f"{output_folder}/atlas/atlas.items.meta_79954554_0.3dst"):
        with open(f"{output_folder}/atlas/atlas.items.meta_79954554_0.3dst", "rb") as f:
            itemAtlas = f.read()
    else:
        with open(f"assets/atlas/atlas.items.meta_79954554_0.3dst", "rb") as f:
            itemAtlas = f.read()
    itemImg = Image.open(itemImgPath).convert("RGBA")

    # Continua solo si la imagen es 16x16
    width, height = itemImg.size
    if width == 16 and height == 16:
        # Voltea verticalmente la imagen del item
        itemImgFlip = itemImg.transpose(Image.FLIP_TOP_BOTTOM)

        # Obtiene los bytes en una lista del atlas
        itemAtlasBytes = []
        for b in itemAtlas:
            itemAtlasBytes.append(b)

        # Carga los pixeles de la imagen
        itemImgFlipPixels = itemImgFlip.load()

        # Convierte la imagen a 3dst
        img3dst = []
        x = 0
        y = 0
        for i in range(0, 2):
            for i in range(0, 2):
                for i in range(0, 2):
                    for i in range(0, 2):
                        for i in range(0, 2):
                            for i in range(0, 2):
                                for i in range(0, 2):
                                    for i in range(0, 2):
                                        r, g, b, a = itemImgFlipPixels[x, y]
                                        print(r, g, b, a)

                                        img3dst.append(a)
                                        if a != 0:
                                            img3dst.append(b)
                                            img3dst.append(g)
                                            img3dst.append(r)
                                        else:
                                            for i in range(0, 3):
                                                img3dst.append(0)
                                        x += 1
                                    y += 1
                                    x -= 2
                                y -= 2
                                x += 2
                            y += 2
                            x -= 4
                        y -= 4
                        x += 4
                    y += 4
                    x -= 8
                y -= 8
                x += 8
            y += 8
            x -= 16
        
        # Establece variables de indexado
        atlas_i = 32 + (((((16 * 4) * 8) * 2) * 32) * (y_offset + 3)) + (((16 * 4) * 8) * x_offset)
        img3dstIndex = 0

        # Reemplazar infromacion del atlas
        for i in range(0, (128 * 4)):
            itemAtlasBytes[atlas_i] = img3dst[img3dstIndex]
            atlas_i += 1
            img3dstIndex += 1

        # (Necesario ya que cada item en el archivo se divide en 2 partes)
        atlas_i += (((16 * 4) * 8) * 31)

        for i in range(0, (128 * 4)):
            itemAtlasBytes[atlas_i] = img3dst[img3dstIndex]
            atlas_i += 1
            img3dstIndex += 1

        # Crea el directorio de salida si no existe
        if not os.path.exists(f"{output_folder}"):
            os.mkdir(f"{output_folder}")
        if not os.path.exists(f"{output_folder}/atlas"):
            os.mkdir(f"{output_folder}/atlas")

        # Convierte la lista de bytes en bytesarray
        byte_arr = bytearray(itemAtlasBytes)

        # Guarda el atlas modificado
        if not os.path.exists(f"{output_folder}/atlas/atlas.items.meta_79954554_0.3dst"):
            print("No atlas file found in output folder. Created a new one")
        with open(f"{output_folder}/atlas/atlas.items.meta_79954554_0.3dst", "wb") as f:
            f.write(byte_arr)

        # Retorna la lista de bytes
        return itemAtlasBytes
    else:
        return None

def addToBlockAtlas(itemData, itemImgPath):
    # Establece variables necesarias para la conversión
    x_offset = int(itemData[2])
    y_offset = int(itemData[1])

    # Carga las imagenes necesarias a la memoria
    if os.path.exists(f"{outputFolder}/atlas/atlas.terrain.meta_79954554_0.png"):
        atlasImg = Image.open(f"{outputFolder}/atlas/atlas.terrain.meta_79954554_0.png").convert("RGBA")
    else:
        atlasImg = Image.open("assets/atlas/atlas.terrain.meta_79954554_0.png").convert("RGBA")
    itemImg = Image.open(itemImgPath).convert("RGBA")
    itemImgFlip = itemImg.transpose(Image.FLIP_TOP_BOTTOM)

    # Carga los pixeles de cada imagen
    atlasImgPixels = atlasImg.load()
    itemImgFlipPixels = itemImgFlip.load()

    # Posiciona las variables x & y según los offsets
    atlas_x = (20 * x_offset) + 2
    atlas_y = 72 + (20 * y_offset) + 2

    # Reemplaza la textura en el archivo .png
    for y in range(0, 16):
        for x in range(0, 16):
            atlasImgPixels[atlas_x, atlas_y] = itemImgFlipPixels[x, y]
            atlas_x += 1
        atlas_x -= 16
        atlas_y += 1
    
    # Preparaciones para iniciar la conversión de .png a .3dst
    data = [51, 68, 83, 84, 3, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 3, 0, 0, 0]
    atlas_x = 0
    atlas_y = 0

    # Crea los datos para el archivo .3dst del item atlas
    for i in range(0, 64):
        for i in range(0, 64):
            for i in range(0, 2):
                for i in range(0, 2):
                    for i in range(0, 2):
                        for i in range(0, 2):
                            for i in range(0, 2):
                                for i in range(0, 2):
                                    r, g, b, a = atlasImgPixels[atlas_x, atlas_y]
                                    data.append(a)
                                    if a != 0:
                                        data.append(b)
                                        data.append(g)
                                        data.append(r)
                                    else:
                                        for i in range(0, 3):
                                            data.append(0)
                                    atlas_x += 1
                                atlas_x -= 2
                                atlas_y += 1
                            atlas_x += 2
                            atlas_y -= 2
                        atlas_x -= 4
                        atlas_y += 2
                    atlas_x += 4
                    atlas_y -= 4
                atlas_x -= 8
                atlas_y += 4
            atlas_x += 8
            atlas_y -= 8
        atlas_x -= 512
        atlas_y += 8

    # Crea la carpeta de atlas si aun no existe
    if not os.path.exists(f"{outputFolder}/atlas"):
        os.mkdir(f"{outputFolder}/atlas")

    # Convierte la lista a binario
    byte_arr = bytearray(data)

    # Guarda las modificaciones al archivo .png
    atlasImg.save(f"{outputFolder}/atlas/atlas.terrain.meta_79954554_0.png")

    # Guarda el archivo .3dst
    with open(f"{outputFolder}/atlas/atlas.terrain.meta_79954554_0.3dst", "wb") as f:
        f.write(byte_arr)

if __name__ == "__main__":
    Tk().withdraw()
    
    items = []
    blocks = []
    outputFolder = "3dsTexture"

    clear()
    close = False

    # Main loop
    while close != True:
        printMenu()
        
        option = input("Enter an option: ")

        try:
            option = int(option)
        except:
            option = None

        match option:
            # Cambiar la textura de un item
            case 1:
                if os.path.exists("assets/atlas/atlas.items.meta_79954554_0.3dst") or os.path.exists(f"{outputFolder}/atlas/atlas.items.meta_79954554_0.3dst"):
                    clear()
                    items = getItemsFromIndexFile("assets/itemslist.txt")
                    addedItems = []
                    if os.path.exists(f"{outputFolder}/addedItems.txt"):
                        addedItems = getItemsFromIndexFile(f"{outputFolder}/addedItems.txt")

                    print(addedItems)

                    noAddedItems = []
                    for element in items:
                        if element not in addedItems:
                            noAddedItems.append(element)

                    # Imprime todos los items de la lista
                    for i in range(len(noAddedItems)):
                        itemName = noAddedItems[i].split(".")
                        print(f"{i+1}: {itemName[0]}")
                    
                    selection = input("Enter the texture id to change: ")

                    try: 
                        selection = int(selection)
                        if selection < 1 or selection > (len(noAddedItems)):
                            selection = None
                    except:
                        selection = None

                    if selection != None:
                        clear()
                        itemName = noAddedItems[selection-1].split(".")
                        if len(itemName) > 2:
                            print(f"Selection: {itemName[0]}")

                            print("Enter the image file path: ")
                            filePath = filedialog.askopenfilename(filetypes = [("Image files", ".png .jpg")])
                            if filePath != '':
                                print(f"Path selected: {filePath}")
                                clear()
                                print("Converting Image...")
                                print(itemName)
                                outputData = addToItemAtlas(itemName, filePath, outputFolder)
                                if outputData != None:
                                    clear()
                                    print("Success")
                                    print(f"File created at: {outputFolder}/items/{itemName[0]}.3dst")
                                    if not os.path.exists(f"{outputFolder}/addedItems.txt"):
                                        with open(f"{outputFolder}/addedItems.txt", "w") as f:
                                            f.write("")
                                    with open(f"{outputFolder}/addedItems.txt", "a") as f:
                                            f.write(f"{itemName[0]}.{itemName[1]}.{itemName[2]}\n")
                                else:
                                    clear()
                                    print("Error: The image must be 16x16")
                            else:
                                clear()
                                print("Error: No file selected")
                        else:
                            clear()
                            print("Error: Item not supported yet")
                    else:
                        clear()
                        print("Error: Invalid selection")
                else:
                    clear()
                    print("Error: No items atlas found in 'assets/atlas'")

            case 2:
                if os.path.exists("assets/atlas/atlas.terrain.meta_79954554_0.3dst") or os.path.exists(f"{outputFolder}/atlas/atlas.terrain.meta_79954554_0.3dst"):
                    clear()
                    blocks = getItemsFromIndexFile("assets/blockslist.txt")

                    for i in range(len(blocks)):
                        blockName = blocks[i].split(".")
                        print(f"{i+1}: {blockName[0]}")

                    selection = input("Enter the texture id to change: ")

                    try: 
                        selection = int(selection)
                        if selection < 1 or selection > (len(blocks)):
                            selection = None
                    except:
                        selection = None

                    if selection != None:
                        clear()
                        blockName = blocks[selection-1].split(".")
                        if len(blockName) > 2:
                            print(f"Selection: {blockName[0]}")

                            print("Enter the image file path: ")
                            filePath = filedialog.askopenfilename(filetypes = [("Image files", ".png .jpg")])
                            if filePath != '':
                                print(f"Path selected: {filePath}")
                                clear()
                                print("Converting image...")
                                createOutputDirectory(outputFolder)
                                outputData, bytes_list = convertImageTo3dst(filePath)
                                if outputData != None and bytes_list != None:
                                    createOutputDirectory(f"{outputFolder}/items")
                                    with open(f"{outputFolder}/items/{blockName[0]}.3dst", "wb") as outputFile:
                                        outputFile.write(outputData)

                                    print(blockName)
                                    addToBlockAtlas(blockName, filePath)
                                    clear()
                                    print("Success")
                                    print(f"File created at: {outputFolder}/items/{blockName[0]}.3dst")
                                else:
                                    clear()
                                    print("Error: Image must be 16x16 pixels")
                            else:
                                clear()
                                print("Error: No file selected")
                        else:
                            clear()
                            print("Error: Block not supported yet")
                    else:
                        clear()
                        print("Error: Invalid selection")
                else:
                    clear()
                    print("Error: No terrain atlas found in 'assets/atlas'")

            case 3:
                clear()
                print("Exit")
                break

            case _:
                clear()
                print("Error: Invalid option")