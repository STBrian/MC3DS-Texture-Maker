import os
import sys
import difflib
from PIL import Image
from tkinter import Tk
from tkinter import filedialog

from src.tex3dst import *

def clear():
    os.system('cls')

def printList(list1: list):
    for i in range(0, len(list1)):
        print(f"{i + 1}: {list1[i]}")

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

def deleteMatches(list1: list, list2: list):
    matches = []
    for i in range(0, len(list1)):
        if not (list1[i] in list2):
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

def addElementToFile(value, filePath: str):
    if os.path.exists(filePath):
        with open(filePath, "a") as f:
            f.write(f"{value}\n")
        return
    else:
        file = open(filePath, "w")
        file.write(f"{value}\n")

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

def addToItemAtlas(pixelPosition, textureImgPath, output_folder):
    # Carga los archivos necesarios a la memoria
    if os.path.exists(f"{output_folder}/atlas/atlas.items.meta_79954554_0.3dst"):
        itemAtlas = Texture3dst().open(f"{output_folder}/atlas/atlas.items.meta_79954554_0.3dst")
    else:
        itemAtlas = Texture3dst().new(512, 256, 1)
        itemAtlasSource = Image.open(f"{sourceFolder}/atlas/atlas.items.vanilla.png").convert("RGBA")
        itemAtlasSrcPixels = itemAtlasSource.load()
        x = 0
        y = 0
        for i in range(0, itemAtlasSource.size[1]):
            for j in range(0, itemAtlasSource.size[0]):
                r, g, b, a = itemAtlasSrcPixels[x, y]
                itemAtlas.setPixelRGBA(x, y, r, g, b, a)
                x += 1
            x = 0
            y += 1

        itemAtlasSource.close()
        itemAtlasSrcPixels = None

    textureImg = Image.open(textureImgPath).convert("RGBA")
        
    # Define las variables de posición
    x_atlas = pixelPosition[0]
    y_atlas = pixelPosition[1]

    # Reemplazar la textura original por la nueva
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
        os.makedirs(f"{output_folder}/atlas")

    # Invierte el atlas en el eje x y convierte los datos del atlas antes de exportarlos
    itemAtlas.flipX()
    itemAtlas.convertData()

    # Guarda el atlas modificado
    print("Saving changes...")
    itemAtlas.export(f"{output_folder}/atlas/atlas.items.meta_79954554_0.3dst")

    return
    
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

        blockAtlas.save("out2.png")

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
        clear()
        printMenu()
        
        option = input("Enter an option: ")
        clear()

        match option:
            case "1":
                while True:
                    # Cambiar la textura de un item
                    clear()
                    print("Choose an option:")
                    print("\t1: Search unmodified item by text")
                    print("\t2: Search modified item by text")
                    print("\t3: Show unmodified items")
                    print("\t4: Show modified items")
                    print("\t0: Back")
                    option2 = input("Enter an option: ")

                    if option2.isdigit():
                        option2 = int(option2)
                        if option2 >= 1 and option2 <= 4:
                            escapemenu3 = False
                            update = True
                            items = getItemsFromIndexFile(f"{sourceFolder}/newitemslist.txt")

                            while escapemenu3 == False:
                                if update == True:
                                    clear()
                                    addedItems = []
                                    match option2:
                                        case 1:
                                            search = input("Enter the search text: ")
                                            matches = difflib.get_close_matches(search, items, n=len(items), cutoff=0.5)
                                            if os.path.exists(f"{outputFolder}/items.txt"):
                                                addedItems = getItemsFromIndexFile(f"{outputFolder}/items.txt")
                                                itemsList = deleteMatches(matches, addedItems)
                                            else:
                                                itemsList = matches
                                        case 2:
                                            search = input("Enter the search text: ")
                                            matches = difflib.get_close_matches(search, items, n=len(items), cutoff=0.5)
                                            if os.path.exists(f"{outputFolder}/items.txt"):
                                                addedItems = getItemsFromIndexFile(f"{outputFolder}/items.txt")
                                                itemsList = checkForMatches(matches, addedItems)
                                            else:
                                                itemsList = []
                                        case 3:
                                            if os.path.exists(f"{outputFolder}/items.txt"):
                                                addedItems = getItemsFromIndexFile(f"{outputFolder}/items.txt")
                                                itemsList = deleteMatches(items, addedItems)
                                            else:
                                                itemsList = items

                                        case 4:
                                            if os.path.exists(f"{outputFolder}/items.txt"):
                                                addedItems = getItemsFromIndexFile(f"{outputFolder}/items.txt")
                                                itemsList = checkForMatches(items, addedItems)
                                            else:
                                                itemsList = []
                                    
                                    printList(itemsList)
                                    print("0: Back")
                                    update = False
                                
                                id = input("Enter an ID: ")
                                if id.isdigit():
                                    id = int(id)
                                    if id == 0:
                                        escapemenu3 = True
                                    else:
                                        if not (id < 0 and id >= len(itemsList)):
                                            id -= 1
                                            matchwith = checkForMatch(itemsList[id], items)
                                            if matchwith != False:
                                                position = calculateGrid(matchwith, 32, 13, 16)
                                                if position != False:
                                                    print(f"Selection: {items[matchwith]}")
                                                    filePath = filedialog.askopenfilename(filetypes = [("Image files", ".png .jpg")])
                                                    if filePath != '':
                                                        if isImage16x16(filePath):
                                                            addToItemAtlas(position, filePath, outputFolder)
                                                            duplicated = checkForMatch(items[matchwith], addedItems)
                                                            if duplicated == -1:
                                                                print(duplicated)
                                                                addElementToFile(items[matchwith], f"{outputFolder}/items.txt")
                                                            print("Finished")
                                                            update = True
                                                        else:
                                                            print("Texture must be 16x16")
                                                    else:
                                                        print("No file selected")
                                                else:
                                                    print("Error calculating the grid position")
                                            else:
                                                print("Unexpected error")
                                        else:
                                            print("Invalid ID (Out of range)")
                                else:
                                    print("Invalid ID (Not a digit)")
                        else:
                            if option2 == 0:
                                break
                            else:
                                print("Invalid option (Out of range)")
                    else:
                        print("Invalid option (Not a digit)")

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