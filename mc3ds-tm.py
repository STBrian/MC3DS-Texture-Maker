import os
import math
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

def addToItemAtlas(item, data):
    # Elige el atlas original si aún no existe uno modificado
    if os.path.exists("3dsTexture/atlas/atlas.items.meta_79954554_0.3dst"):
        with open("3dsTexture/atlas/atlas.items.meta_79954554_0.3dst", "rb") as f:
            atlasRead = f.read()
    else:
        with open("assets/atlas/atlas.items.meta_79954554_0.3dst", "rb") as f:
            atlasRead = f.read()

    # Obtiene la lista de bytes del atlas seleccionado
    atlasContent = []
    for b in atlasRead:
        atlasContent.append(b)

    # Establece la variable de la posición del item en el atlas
    position = int(item)
    print(position)

    # Calcula el offset hasta el item seleccionado
    y_offset = math.floor(position / 32)
    print(y_offset)
    x_offset = position - (y_offset * 32)
    print(x_offset)

    atlasIndex = 32 + ((((16 * 4) * 32) * 16) * y_offset) + (((16 * 4) * 8) * x_offset)
    index = 32

    # Reemplaza la información del item original
    for i in range(0, (128 * 4)):
        atlasContent[atlasIndex] = data[index]
        atlasIndex +=1
        index += 1

    atlasIndex += ((16 * 4) * 8) * 31

    for i in range(0, (128 * 4)):
        atlasContent[atlasIndex] = data[index]
        atlasIndex += 1
        index += 1

    # Crea la carpeta de atlas si no existe aún
    createOutputDirectory(f"{outputFolder}/atlas")

    # Guarda el archivo editado
    byte_arr = bytearray(atlasContent)

    with open(f"{outputFolder}/atlas/atlas.items.meta_79954554_0.3dst", "wb") as f:
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
                items = getItemsFromIndexFile("assets/itemslist.txt")
                clear()

                # Imprime todos los items de la lista
                for i in range(len(items)):
                    itemName = items[i].split(".")
                    print(f"{i+1}: {itemName[0]}")
                
                selection = input("Enter the texture id to change: ")

                try: 
                    selection = int(selection)
                    if selection < 0 or selection > (len(items)):
                        selection = None
                except:
                    selection = None

                if selection != None:
                    clear()
                    itemName = items[selection-1].split(".")
                    print(f"Selection: {itemName[0]}")

                    print("Enter the image file path: ")
                    filePath = filedialog.askopenfilename(filetypes = [("Image files", ".png .jpg")])
                    if filePath != '':
                        print(f"Path selected: {filePath}")
                        clear()
                        print("Converting Image...")
                        createOutputDirectory(outputFolder)
                        outputData, bytes_list = convertImageTo3dst(filePath)
                        if outputData != None and bytes_list != None:
                            createOutputDirectory(f"{outputFolder}/items")
                            with open(f"{outputFolder}/items/{itemName[0]}.3dst", "wb") as outputFile:
                                outputFile.write(outputData)

                            print(itemName)
                            addToItemAtlas(itemName[1], bytes_list)
                            clear()
                            print("Success")
                            print(f"File created at: {outputFolder}/items/{itemName[0]}.3dst")
                        else:
                            clear()
                            print("Error: Image must be 16x16 pixels")
                    else:
                        clear()
                        print("Error: No file selected")
                else:
                    clear()
                    print("Error: Invalid selection")

            case 2:
                clear()
                blocks = getItemsFromIndexFile("assets/blockslist.txt")

            case 3:
                clear()
                print("Exit")
                break

            case _:
                clear()
                print("Error: Invalid option")