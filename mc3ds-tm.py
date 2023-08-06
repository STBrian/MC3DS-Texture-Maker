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

def convertImageTo3dst(item_data, texture_path, output_folder):
    img = Image.open(texture_path).convert('RGBA')
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

        if not os.path.exists(f"{output_folder}"):
            os.makedirs(f"{output_folder}")

        with open(f"{output_folder}/{item_data[0]}.3dst", "wb") as f:
            f.write(byte_arr)

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
    
def addToBlockAtlas(blockData, textureImgPath, output_folder):
    # Establece variables necesarias para el proceso
    x_offset = int(blockData[2])
    y_offset = int(blockData[1])
    
    # Carga los archivos necesarios
    print("Loading files")
    if not os.path.exists(f"{output_folder}/atlas/atlas.terrain.meta_79954554_0.png"):
        blockAtlas = Image.open("assets/atlas/atlas.terrain.meta_79954554_0.png")
    else:
        blockAtlas = Image.open(f"{output_folder}/atlas/atlas.terrain.meta_79954554_0.png")
    textureImg = Image.open(textureImgPath).convert("RGBA")
    
    # Continua solo si la imagen es 16x16
    if textureImg.size[0] == 16 and textureImg.size[1] == 16:
        # Voltea verticalmente la textura
        textureImgFlip = textureImg.transpose(Image.FLIP_TOP_BOTTOM)

        # Establece la lista de salida
        modifiedBlockAtlas = [51, 68, 83, 84, 3, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 3, 0, 0, 0]

        # Calcula los offsets
        x_atlas = (20 * x_offset)
        y_atlas = 72 + (20 * y_offset)

        # Carga el atlas a la memoria
        blockAtlasPixels = blockAtlas.load()

        # Reemplaza la textura original por la nueva
        ## Esquinas
        for i in range(0, 2):
            for i in range(0, 2):
                blockAtlasPixels[x_atlas, y_atlas] = textureImgFlip.getpixel((0, 0))
                x_atlas += 1
            x_atlas -= 2
            y_atlas += 1

        x_atlas = (20 * x_offset) + 18
        y_atlas = 72 + (20 * y_offset)

        for i in range(0, 2):
            for i in range(0, 2):
                blockAtlasPixels[x_atlas, y_atlas] = textureImgFlip.getpixel((15, 0))
                x_atlas += 1
            x_atlas -= 2
            y_atlas += 1

        x_atlas = (20 * x_offset)
        y_atlas = 72 + (20 * y_offset) + 18

        for i in range(0, 2):
            for i in range(0, 2):
                blockAtlasPixels[x_atlas, y_atlas] = textureImgFlip.getpixel((0, 15))
                x_atlas += 1
            x_atlas -= 2
            y_atlas += 1

        x_atlas = (20 * x_offset) + 18
        y_atlas = 72 + (20 * y_offset) + 18

        for i in range(0, 2):
            for i in range(0, 2):
                blockAtlasPixels[x_atlas, y_atlas] = textureImgFlip.getpixel((15, 15))
                x_atlas += 1
            x_atlas -= 2
            y_atlas += 1

        ## Laterales
        x_atlas = (20 * x_offset) + 2
        y_atlas = 72 + (20 * y_offset)

        x = 0
        y = 0
        for i in range(0, 2):
            for i in range(0, 16):
                blockAtlasPixels[x_atlas, y_atlas] = textureImgFlip.getpixel((x, y))
                x += 1
                x_atlas += 1
            x -= 16
            x_atlas -= 16
            y_atlas += 1

        x_atlas = (20 * x_offset) + 2
        y_atlas = 72 + (20 * y_offset) + 18

        x = 0
        y = 15
        for i in range(0, 2):
            for i in range(0, 16):
                blockAtlasPixels[x_atlas, y_atlas] = textureImgFlip.getpixel((x, y))
                x += 1
                x_atlas += 1
            x -= 16
            x_atlas -= 16
            y_atlas += 1

        x_atlas = (20 * x_offset)
        y_atlas = 72 + (20 * y_offset) + 2

        x = 0
        y = 0
        for i in range(0, 2):
            for i in range(0, 16):
                blockAtlasPixels[x_atlas, y_atlas] = textureImgFlip.getpixel((x, y))
                y += 1
                y_atlas += 1
            y -= 16
            y_atlas -= 16
            x_atlas += 1

        x_atlas = (20 * x_offset) + 18
        y_atlas = 72 + (20 * y_offset) + 2

        x = 15
        y = 0
        for i in range(0, 2):
            for i in range(0, 16):
                blockAtlasPixels[x_atlas, y_atlas] = textureImgFlip.getpixel((x, y))
                y += 1
                y_atlas += 1
            y -= 16
            y_atlas -= 16
            x_atlas += 1

        ## Centro
        x_atlas = (20 * x_offset) + 2
        y_atlas = 72 + (20 * y_offset) + 2

        x = 0
        y = 0
        for i in range(0, 16):
            for i in range(0, 16):
                blockAtlasPixels[x_atlas, y_atlas] = textureImgFlip.getpixel((x, y))
                x += 1
                x_atlas += 1
            x = 0
            y += 1
            x_atlas -= 16
            y_atlas += 1

        # Crea la version completa del atlas
        print("Making full version atlas...")
        x = 0
        y = 0
        for i in range(0, 64):
            for i in range(0, 64):
                for i in range(0, 2):
                    for i in range(0, 2):
                        for i in range(0, 2):
                            for i in range(0, 2):
                                for i in range(0, 2):
                                    for i in range(0, 2):
                                        r, g, b, a = blockAtlasPixels[x, y]
                                        modifiedBlockAtlas.append(a)
                                        modifiedBlockAtlas.append(b)
                                        modifiedBlockAtlas.append(g)
                                        modifiedBlockAtlas.append(r)
                                        x += 1
                                    x -= 2
                                    y += 1
                                x += 2
                                y -= 2
                            x -= 4
                            y += 2
                        x += 4
                        y -= 4
                    x -= 8
                    y += 4
                x += 8
                y -= 8
            x = 0
            y += 8

        # Reduce a la mitad la resolucion del atlas
        basewidth = 256
        wpercent = (basewidth/float(blockAtlas.size[0]))
        hsize = int((float(blockAtlas.size[1])*float(wpercent)))
        blockAtlas = blockAtlas.resize((basewidth,hsize), Image.Resampling.LANCZOS)

        # Carga el atlas a la memoria
        blockAtlasPixels = blockAtlas.load()

        # Crea la version con la resolucion a la mitad respecto a la resolucion original
        print("Making half resolution atlas...")
        x = 0
        y = 0
        for i in range(0, 32):
            for i in range(0, 32):
                for i in range(0, 2):
                    for i in range(0, 2):
                        for i in range(0, 2):
                            for i in range(0, 2):
                                for i in range(0, 2):
                                    for i in range(0, 2):
                                        r, g, b, a = blockAtlasPixels[x, y]
                                        modifiedBlockAtlas.append(a)
                                        modifiedBlockAtlas.append(b)
                                        modifiedBlockAtlas.append(g)
                                        modifiedBlockAtlas.append(r)
                                        x += 1
                                    x -= 2
                                    y += 1
                                x += 2
                                y -= 2
                            x -= 4
                            y += 2
                        x += 4
                        y -= 4
                    x -= 8
                    y += 4
                x += 8
                y -= 8
            x = 0
            y += 8

        # Reduce a un cuarto la resolucion del atlas referente a la resolución inicial
        basewidth = 128
        wpercent = (basewidth/float(blockAtlas.size[0]))
        hsize = int((float(blockAtlas.size[1])*float(wpercent)))
        blockAtlas = blockAtlas.resize((basewidth,hsize), Image.Resampling.LANCZOS)

        # Carga el atlas a la memoria
        blockAtlasPixels = blockAtlas.load()

        # Crea la version en resolucion de un cuarto respecto a la resolucion original del atlas
        print("Making 1/4 resolution atlas...")
        x = 0
        y = 0
        for i in range(0, 16):
            for i in range(0, 16):
                for i in range(0, 2):
                    for i in range(0, 2):
                        for i in range(0, 2):
                            for i in range(0, 2):
                                for i in range(0, 2):
                                    for i in range(0, 2):
                                        r, g, b, a = blockAtlasPixels[x, y]
                                        modifiedBlockAtlas.append(a)
                                        modifiedBlockAtlas.append(b)
                                        modifiedBlockAtlas.append(g)
                                        modifiedBlockAtlas.append(r)
                                        x += 1
                                    x -= 2
                                    y += 1
                                x += 2
                                y -= 2
                            x -= 4
                            y += 2
                        x += 4
                        y -= 4
                    x -= 8
                    y += 4
                x += 8
                y -= 8
            x = 0
            y += 8

        # Convierte los bytes en un bytearray
        byte_arr = bytearray(modifiedBlockAtlas)

        # Crea el directorio de salida si no existe
        if not os.path.exists(f"{output_folder}"):
            os.mkdir(f"{output_folder}")
        if not os.path.exists(f"{output_folder}/atlas"):
            os.mkdir(f"{output_folder}/atlas")

        # Guarda el archivo modificado
        print("Saving changes...")
        with open(f"{output_folder}/atlas/atlas.terrain.meta_79954554_0.3dst", "wb") as f:
            f.write(byte_arr)

        # Retorna la lista de bytes
        return byte_arr

    else:
        return None

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
                    if os.path.exists(f"{outputFolder}/changedItems.txt"):
                        addedItems = getItemsFromIndexFile(f"{outputFolder}/changedItems.txt")

                    noAddedItems = []
                    for element in items:
                        if element not in addedItems:
                            if len(element.split(".")) > 2:
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
                                convertImageTo3dst(itemName, filePath, f"{outputFolder}/items")
                                outputData = addToItemAtlas(itemName, filePath, outputFolder)
                                if outputData != None:
                                    clear()
                                    print("Success")
                                    print(f"Atlas created at: {outputFolder}/atlas/atlas.items.meta_79954554_0.3dst")
                                    if not os.path.exists(f"{outputFolder}/addedItems.txt"):
                                        with open(f"{outputFolder}/changedItems.txt", "w") as f:
                                            f.write("")
                                    with open(f"{outputFolder}/changedItems.txt", "a") as f:
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
                # Cambiar la textura de un bloque
                if os.path.exists("assets/atlas/atlas.terrain.meta_79954554_0.3dst") or os.path.exists(f"{outputFolder}/atlas/atlas.terrain.meta_79954554_0.3dst"):
                    clear()
                    blocks = getItemsFromIndexFile("assets/blockslist.txt")
                    addedBlocks = []
                    if os.path.exists(f"{outputFolder}/changedBlocks.txt"):
                        addedBlocks = getItemsFromIndexFile(f"{outputFolder}/changedBlocks.txt")
                    
                    noAddedBlocks = []
                    for element in blocks:                    
                        if element not in addedBlocks:
                            if len(element.split(".")) > 2:
                                noAddedBlocks.append(element)

                    for i in range(len(noAddedBlocks)):
                        blockName = noAddedBlocks[i].split(".")
                        print(f"{i+1}: {blockName[0]}")

                    selection = input("Enter the texture id to change: ")

                    try: 
                        selection = int(selection)
                        if selection < 1 or selection > (len(noAddedBlocks)):
                            selection = None
                    except:
                        selection = None

                    if selection != None:
                        clear()
                        blockName = noAddedBlocks[selection-1].split(".")
                        if len(blockName) > 2:
                            print(f"Selection: {blockName[0]}")

                            print("Enter the image file path: ")
                            filePath = filedialog.askopenfilename(filetypes = [("Image files", ".png .jpg")])
                            if filePath != '':
                                print(f"Path selected: {filePath}")
                                clear()
                                print("Converting image...")
                                print(blockName)
                                convertImageTo3dst(blockName, filePath, f"{outputFolder}/blocks")
                                outputData = addToBlockAtlas(blockName, filePath, outputFolder)
                                if outputData != None:
                                    clear()
                                    print("Success")
                                    print(f"Atlas created at: {outputFolder}/atlas/atlas.terrain.meta_79954554_0.3dst")
                                    if not os.path.exists(f"{outputFolder}/changedBlocks.txt"):
                                        with open(f"{outputFolder}/changedBlocks.txt", "w") as f:
                                            f.write("")
                                    with open(f"{outputFolder}/changedBlocks.txt", "a") as f:
                                        f.write(f"{blockName[0]}.{blockName[1]}.{blockName[2]}\n")
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