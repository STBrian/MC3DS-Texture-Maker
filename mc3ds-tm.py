import os
import sys
import difflib
from PIL import Image
from tkinter import Tk
from tkinter import filedialog

from modules.tex3dst import *

def clear():
    os_type = os.name
    if os_type == "posix":
        os.system("clear")
    elif os_type == "nt":
        os.system("cls")
    else:
        print("Unsupported OS")

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
        os.makedirs(directoryName)

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
    # print("\t3: Change texture pack icon")
    print("\t0: Exit")

def isImage16x16(texture_path):
    img = Image.open(texture_path)
    if img.size[0] == 16 and img.size[1] == 16:
        img.close()
        return True
    else:
        img.close()
        return False

def addToItemAtlas(pixelPosition, textureImgPath, output_folder):
    # Carga los archivos necesarios a la memoria
    if os.path.exists(f"{output_folder}/atlas/atlas.items.meta_79954554_0.3dst"):
        print("Opening modified atlas...")
        itemAtlas = Texture3dst().open(f"{output_folder}/atlas/atlas.items.meta_79954554_0.3dst")
        # El archivo previamente debe estar de cabeza entonces hay que voltearlo para usarlo normal
        itemAtlas.flipX()
    else:
        print("Creating new atlas file...")
        itemAtlas = Texture3dst().new(512, 256, 1)
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
    
def addToBlockAtlas(pixelPosition, textureImgPath, output_folder):
    # Carga los archivos necesarios a la memoria
    print("Starting...")
    if os.path.exists(f"{output_folder}/atlas/atlas.terrain.meta_79954554_0.3dst"):
        print("Opening modified atlas...")
        blockAtlas = Texture3dst().open(f"{output_folder}/atlas/atlas.terrain.meta_79954554_0.3dst")
        # El archivo previamente debe estar de cabeza entonces hay que voltearlo para usarlo normal
        blockAtlas.flipX()
    else:
        print("Creating new texture file...")
        blockAtlas = Texture3dst().new(512, 512, 3)
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

if __name__ == "__main__":
    Tk().withdraw()
    
    items = []
    blocks = []

    sourceFolder = "assets"
    if getattr(sys, 'frozen', False):
        print("Running from executable file")
        os.chdir(sys._MEIPASS)
        outputFolder = os.path.join(os.path.dirname(sys.executable), input("Enter the output folder: "))
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
                escapemenu2 = False
                while escapemenu2 == False:
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
                            items = getItemsFromIndexFile(f"{sourceFolder}/indexes/newitemslist.txt")

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
                                        if not (id < 0 or id > len(itemsList)):
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
                                escapemenu2 = True
                            else:
                                print("Invalid option (Out of range)")
                    else:
                        print("Invalid option (Not a digit)")

            case "2":
                escapemenu2 = False

                while escapemenu2 == False:
                    # Cambiar la textura de un bloque
                    clear()
                    print("Choose an option:")
                    print("\t1: Search unmodified block by text")
                    print("\t2: Search modified block by text")
                    print("\t3: Show unmodified blocks")
                    print("\t4: Show modified blocks")
                    print("\t0: Back")
                    option2 = input("Enter an option: ")

                    if option2.isdigit():
                        option2 = int(option2)
                        if option2 >= 1 and option2 <= 4:
                            escapemenu3 = False
                            update = True
                            items = getItemsFromIndexFile(f"{sourceFolder}/indexes/newblockslist.txt")

                            while escapemenu3 == False:
                                if update == True:
                                    clear()
                                    addedItems = []
                                    match option2:
                                        case 1:
                                            search = input("Enter the search text: ")
                                            matches = difflib.get_close_matches(search, items, n=len(items), cutoff=0.5)
                                            if os.path.exists(f"{outputFolder}/blocks.txt"):
                                                addedItems = getItemsFromIndexFile(f"{outputFolder}/blocks.txt")
                                                itemsList = deleteMatches(matches, addedItems)
                                            else:
                                                itemsList = matches
                                        case 2:
                                            search = input("Enter the search text: ")
                                            matches = difflib.get_close_matches(search, items, n=len(items), cutoff=0.5)
                                            if os.path.exists(f"{outputFolder}/blocks.txt"):
                                                addedItems = getItemsFromIndexFile(f"{outputFolder}/blocks.txt")
                                                itemsList = checkForMatches(matches, addedItems)
                                            else:
                                                itemsList = []
                                        case 3:
                                            if os.path.exists(f"{outputFolder}/blocks.txt"):
                                                addedItems = getItemsFromIndexFile(f"{outputFolder}/blocks.txt")
                                                itemsList = deleteMatches(items, addedItems)
                                            else:
                                                itemsList = items
                                        case 4:
                                            if os.path.exists(f"{outputFolder}/blocks.txt"):
                                                addedItems = getItemsFromIndexFile(f"{outputFolder}/blocks.txt")
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
                                        if not (id < 0 or id > len(itemsList)):
                                            id -= 1
                                            matchwith = checkForMatch(itemsList[id], items)
                                            if matchwith != False:
                                                position = calculateGrid(matchwith, 25, 22, 20)
                                                if position != False:
                                                    print(f"Selection: {items[matchwith]}")
                                                    filePath = filedialog.askopenfilename(filetypes = [("Image files", ".png .jpg")])
                                                    if filePath != '':
                                                        if isImage16x16(filePath):
                                                            addToBlockAtlas(position, filePath, outputFolder)
                                                            duplicated = checkForMatch(items[matchwith], addedItems)
                                                            if duplicated == -1:
                                                                addElementToFile(items[matchwith], f"{outputFolder}/blocks.txt")
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
                                escapemenu2 = True
                            else:
                                print("Invalid option (Out of range)")
                    else:
                        print("Invalid option (Not a digit)")
            case "3":
                # Unused option
                if True == False:
                    clear()
                    # Cambiar icono del paquete
                    print("Choose an image: ")
                    filePath = filedialog.askopenfilename(filetypes = [("Image files", ".png .jpg")])
                    if filePath != '':
                        texture = Image.open(filePath).convert("RGBA")
                        if texture.size[0] == texture.size[1]:
                            resizedwidth = 64
                            width = texture.size[0]
                            height = texture.size[1]
                            wpercent = (resizedwidth/float(width))
                            hsize = int((float(height)*float(wpercent)))
                            texture = texture.resize((resizedwidth, hsize), Image.Resampling.LANCZOS)

                            icon_texture = Texture3dst().new(64, 64, 1)

                            x = 0
                            y = 0
                            for i in range(0, 64):
                                for j in range(0, 64):
                                    r, g, b, a = texture.getpixel((x, y))
                                    icon_texture.setPixelRGBA(x, y, r, g, b, a)
                                    x += 1
                                x = 0
                                y += 1

                            texture.close()

                            icon_texture.flipX()
                            icon_texture.convertData()

                            if not os.path.exists(f"{outputFolder}"):
                                createOutputDirectory(f"{outputFolder}")
                            
                            print("Saving icon...")
                            icon_texture.export(f"{outputFolder}/icon_pack.3dst")
                            print("Success!")

                        else:
                            print("Image texture must be 1:1")
                    else:
                        print("No file selected")
                else:
                    clear()
                    print("Invalid option")

            case "0":
                clear()
                print("Exit")
                close = True

            case _:
                clear()
                print("Invalid option")