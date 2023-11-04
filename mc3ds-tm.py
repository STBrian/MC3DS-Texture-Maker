import os
import sys
from PIL import Image
from tkinter import Tk
from tkinter import filedialog

import tex3dst

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
    print("\t3: Change texture pack icon")
    print("\t0: Exit")

def isImage16x16(texture_path):
    img = Image.open(texture_path)
    if img.size[0] == 16 and img.size[1] == 16:
        img.close()
        return True
    else:
        img.close()
        return False

def convertImageTo3dst(output_filename, texture_path, output_folder):
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

        with open(f"{output_folder}/{output_filename}.3dst", "wb") as f:
            f.write(byte_arr)

        return byte_arr, outputData
    else:
        return None, None

def addToItemAtlas(itemData, textureImgPath, output_folder):
    # Establece variables necesarias para la conversión
    x_offset = int(itemData[2])
    y_offset = int(itemData[1])

    # Carga los archivos necesarios a la memoria
    if os.path.exists(f"{output_folder}/atlas.items.meta_79954554_0.png"):
        itemAtlas = Image.open(f"{output_folder}/atlas.items.meta_79954554_0.png")
    else:
        itemAtlas = Image.open(f"{sourceFolder}/atlas/atlas.items.meta_79954554_0.png")
    textureImg = Image.open(textureImgPath).convert("RGBA")

    # Continua solo si la imagen es 16x16
    if textureImg.size[0] == 16 and textureImg.size[1] == 16:
        # Voltea verticalmente la imagen del item
        textureImgFlip = textureImg.transpose(Image.FLIP_TOP_BOTTOM)

        # Establece la lista de salida
        modifiedItemAtlas = [51, 68, 83, 84, 3, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 1, 0, 0, 0, 2, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0]
        
        # Calcula los offsets
        x_atlas = (16 * x_offset)
        y_atlas = 48 + (y_offset * 16)

        # Carga el atlas a la memoria
        itemAtlasPixels = itemAtlas.load()

        # Reemplazar la textura original por la nueva
        x = 0
        y = 0
        for i in range(0, 16):
            for i in range(0, 16):
                itemAtlasPixels[x_atlas, y_atlas] = textureImgFlip.getpixel((x, y))
                x += 1
                x_atlas += 1
            x = 0
            x_atlas -= 16
            y += 1
            y_atlas += 1

        # Crea el directorio de salida si no existe
        if not os.path.exists(f"{output_folder}/atlas"):
            os.makedirs(f"{output_folder}/atlas")

        # Guarda los cambios hechos en la imagen
        print("Saving changes...")
        itemAtlas.save(f"{output_folder}/atlas.items.meta_79954554_0.png")

        # Crea la version completa del atlas
        print("Making full version atlas...")
        x = 0
        y = 0
        for i in range(0, 32):
            for i in range(0, 64):
                for i in range(0, 2):
                    for i in range(0, 2):
                        for i in range(0, 2):
                            for i in range(0, 2):
                                for i in range(0, 2):
                                    for i in range(0, 2):
                                        r, g, b, a = itemAtlasPixels[x, y]
                                        modifiedItemAtlas.append(a)
                                        modifiedItemAtlas.append(b)
                                        modifiedItemAtlas.append(g)
                                        modifiedItemAtlas.append(r)
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

        # Convierte la lista de bytes en bytesarray
        byte_arr = bytearray(modifiedItemAtlas)

        # Guarda el atlas modificado
        print("Saving changes...")
        with open(f"{output_folder}/atlas/atlas.items.meta_79954554_0.3dst", "wb") as f:
            f.write(byte_arr)

        # Retorna la lista de bytes
        return byte_arr
    else:
        return None
    
def addToBlockAtlas(blockData, textureImgPath, output_folder):
    # Establece variables necesarias para el proceso
    x_offset = int(blockData[2])
    y_offset = int(blockData[1])
    
    # Carga los archivos necesarios
    print("Loading files")
    if not os.path.exists(f"{output_folder}/atlas.terrain.meta_79954554_0.png"):
        blockAtlas = Image.open(f"{sourceFolder}/atlas/atlas.terrain.meta_79954554_0.png")
    else:
        blockAtlas = Image.open(f"{output_folder}/atlas.terrain.meta_79954554_0.png")
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

        
        # Crea el directorio de salida si no existe
        if not os.path.exists(f"{output_folder}/atlas"):
            os.makedirs(f"{output_folder}/atlas")

        # Guarda los cambios hecho en la imagen
        print("Saving changes...")
        blockAtlas.save(f"{output_folder}/atlas.terrain.meta_79954554_0.png")

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

    sourceFolder = "src"
    if getattr(sys, 'frozen', False):
        print("Running from executable file")
        os.chdir(sys._MEIPASS)
        outFolder = input("Enter the output folder: ")
        outputFolder = os.path.join(os.path.dirname(sys.executable), outFolder)
    elif __file__:
        print("Running from source file")
        outputFolder = "MC3DS"

    clear()
    close = False

    # Main loop
    while close != True:
        printMenu()
        
        option = input("Enter an option: ")
        clear()

        match option:
            case "1":
                while True:
                    # Cambiar la textura de un item
                    print("Choose an option:")
                    print("\t1: Search unmodified item by text")
                    print("\t2: Search modified item by text")
                    print("\t3: Show unmodified items")
                    print("\t4: Show modified items")
                    print("\t0: Exit")
                    option2 = input("Enter an option: ")
                    match option2:
                        case "3":
                            # Mostrar items no modificados
                            clear()
                            items = getItemsFromIndexFile(f"{sourceFolder}/itemslist.txt")
                            updateItems = True
                            while True:
                                # Imprime todos los items de la lista
                                if updateItems == True:
                                    addedItems = []
                                    if os.path.exists(f"{outputFolder}/changedItems.txt"):
                                        addedItems = getItemsFromIndexFile(f"{outputFolder}/changedItems.txt")

                                    noAddedItems = []
                                    for element in items:
                                        if element not in addedItems:
                                            # Si el item no está agregado aún, no se mostrará
                                            if len(element.split(".")) > 2:
                                                noAddedItems.append(element)

                                    for i in range(len(noAddedItems)):
                                        itemName = noAddedItems[i].split(".")
                                        print(f"{i+1}: {itemName[0]}")
                                    print("0: Exit")
                                    updateItems = False

                                selection = input("Enter the texture id to change: ")

                                try: 
                                    selection = int(selection)
                                    if selection < 0 or selection > (len(noAddedItems)):
                                        selection = None
                                except:
                                    selection = None

                                if selection != None:
                                    if selection != 0:
                                        itemName = noAddedItems[selection-1].split(".")
                                        # Si el elemento contiene más de 2 valores (es decir: nombre, y position, x position)
                                        if len(itemName) > 2:
                                            print(f"Selection: {itemName[0]}")
                                            print("Enter the image file path: ")
                                            filePath = filedialog.askopenfilename(filetypes = [("Image files", ".png .jpg")])
                                            if filePath != '':
                                                print(f"Path selected: {filePath}")
                                                if isImage16x16(filePath):
                                                    print("Converting Image...")
                                                    print(itemName)
                                                    convertImageTo3dst(itemName[0], filePath, f"{outputFolder}/items")
                                                    outputData = addToItemAtlas(itemName, filePath, outputFolder)
                                                    if outputData != None:
                                                        if not os.path.exists(f"{outputFolder}/changedItems.txt"):
                                                            with open(f"{outputFolder}/changedItems.txt", "w") as f:
                                                                f.write("")
                                                        with open(f"{outputFolder}/changedItems.txt", "a") as f:
                                                                f.write(f"{itemName[0]}.{itemName[1]}.{itemName[2]}\n")
                                                        clear()
                                                        print("Success")
                                                        print(f"Atlas created at: {outputFolder}/atlas/atlas.items.meta_79954554_0.3dst")
                                                        updateItems = True
                                                    else:
                                                        clear()
                                                        print("Error: Unknown error")
                                                        updateItems = True
                                                else:
                                                    print("Error: The image must be 16x16")
                                            else:
                                                print("Error: No file selected")
                                        else:
                                            print("Error: Item not supported yet")
                                    else:
                                        print("Exit")
                                        clear()
                                        break
                                else:
                                    print("Error: Invalid selection")

                        case "4":
                            # Mostrar items modificados
                            clear()
                            items = getItemsFromIndexFile(f"{sourceFolder}/itemslist.txt")

                            addedItems = []
                            if os.path.exists(f"{outputFolder}/changedItems.txt"):
                                addedItems = getItemsFromIndexFile(f"{outputFolder}/changedItems.txt")

                            listItems = []
                            for element in addedItems:
                                if element in items:
                                    # Si el item no está agregado aún, no se mostrará
                                    if len(element.split(".")) > 2:
                                        listItems.append(element)

                            updateItems = True

                            while True:
                                # Imprime todos los items de la lista
                                if updateItems == True:
                                    for i in range(len(listItems)):
                                        itemName = listItems[i].split(".")
                                        print(f"{i+1}: {itemName[0]}")
                                    print("0: Exit")
                                    updateItems = False

                                selection = input("Enter the texture id to change: ")

                                try: 
                                    selection = int(selection)
                                    if selection < 0 or selection > (len(listItems)):
                                        selection = None
                                except:
                                    selection = None

                                if selection != None:
                                    if selection != 0:
                                        itemName = listItems[selection-1].split(".")
                                        # Si el elemento contiene más de 2 valores (es decir: nombre, y position, x position)
                                        if len(itemName) > 2:
                                            print(f"Selection: {itemName[0]}")
                                            print("Enter the image file path: ")
                                            filePath = filedialog.askopenfilename(filetypes = [("Image files", ".png .jpg")])
                                            if filePath != '':
                                                print(f"Path selected: {filePath}")
                                                if isImage16x16(filePath):
                                                    print("Converting Image...")
                                                    print(itemName)
                                                    convertImageTo3dst(itemName[0], filePath, f"{outputFolder}/items")
                                                    outputData = addToItemAtlas(itemName, filePath, outputFolder)
                                                    if outputData != None:
                                                        if not os.path.exists(f"{outputFolder}/changedItems.txt"):
                                                            with open(f"{outputFolder}/changedItems.txt", "w") as f:
                                                                f.write("")
                                                        with open(f"{outputFolder}/changedItems.txt", "a") as f:
                                                                f.write(f"{itemName[0]}.{itemName[1]}.{itemName[2]}\n")
                                                        clear()
                                                        print("Success")
                                                        print(f"Atlas created at: {outputFolder}/atlas/atlas.items.meta_79954554_0.3dst")
                                                        updateItems = True
                                                    else:
                                                        clear()
                                                        print("Error: Unknown error")
                                                        updateItems = True
                                                else:
                                                    print("Error: The image must be 16x16")
                                            else:
                                                print("Error: No file selected")
                                        else:
                                            print("Error: Item not supported yet")
                                    else:
                                        print("Exit")
                                        clear()
                                        break
                                else:
                                    print("Error: Invalid selection")

                        case "0":
                            print("Exit")
                            clear()
                            break

                        case _:
                            clear()
                            print("Error: Invalid option")

            case "2":
                # Cambiar la textura de un bloque
                clear()
                blocks = getItemsFromIndexFile(f"{sourceFolder}/blockslist.txt")
                addedBlocks = []
                if os.path.exists(f"{outputFolder}/changedBlocks.txt"):
                    addedBlocks = getItemsFromIndexFile(f"{outputFolder}/changedBlocks.txt")
                    
                noAddedBlocks = []
                for element in blocks:                    
                    if element not in addedBlocks:
                        # Si el bloque no está agregado aún, no se mostrará
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
                    # Si el elemento contiene más de 2 valores (es decir: nombre, y position, x position)
                    if len(blockName) > 2:
                        print(f"Selection: {blockName[0]}")
                        print("Enter the image file path: ")
                        filePath = filedialog.askopenfilename(filetypes = [("Image files", ".png .jpg")])
                        if filePath != '':
                            print(f"Path selected: {filePath}")
                            if isImage16x16(filePath):
                                print("Converting image...")
                                print(blockName)
                                convertImageTo3dst(blockName[0], filePath, f"{outputFolder}/blocks")
                                outputData = addToBlockAtlas(blockName, filePath, outputFolder)
                                if outputData != None:
                                    if not os.path.exists(f"{outputFolder}/changedBlocks.txt"):
                                        with open(f"{outputFolder}/changedBlocks.txt", "w") as f:
                                            f.write("")
                                    with open(f"{outputFolder}/changedBlocks.txt", "a") as f:
                                        f.write(f"{blockName[0]}.{blockName[1]}.{blockName[2]}\n")
                                    clear()
                                    print("Success")
                                    print(f"Atlas created at: {outputFolder}/atlas/atlas.terrain.meta_79954554_0.3dst")
                                else:
                                    clear()
                                    print("Error: Unknown error")
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

            case "3":
                # Agrega o cambia el icono del paquete
                clear()
                print("Enter the image file path: ")
                filePath = filedialog.askopenfilename(filetypes = [("Image files", ".png .jpg")])
                if filePath != '':
                    print(f"Path selected: {filePath}")
                    if isImage16x16(filePath):
                        print("Converting image...")
                        outputData = convertImageTo3dst("pack", filePath, outputFolder)
                        if outputData != None:
                            clear()
                            print("Success")
                            print(f"Pack icon created at: {outputFolder}/pack.3dst")
                        else:
                            clear()
                            print("Error: Unknown error")
                    else:
                        clear()
                        print("Error: Image must be 16x16 pixels")
                else:
                    clear()
                    print("Error: No file selected")
            case "0":
                clear()
                print("Exit")
                break

            case _:
                clear()
                print("Error: Invalid option")