import os
import customtkinter
from PIL import Image, ImageDraw
from pathlib import Path
from py3dst import Texture3dst
from tkinter import messagebox
from modules import atlasTexture3dst, canOpenImage, isImageSize, checkForMatch

def _generateChessboardPattern(width, height, tileSize = 10):
    chessboard = Image.new("RGBA", (width, height), (146, 146, 146, 255))
    draw = ImageDraw.Draw(chessboard)

    for y in range(0, height, tileSize):
        for x in range(0, width, tileSize):
            if (x // tileSize + y // tileSize) % 2 == 0:
                draw.rectangle(
                    [(x, y), (x + tileSize - 1, y + tileSize - 1)], 
                    fill=(86, 86, 86, 255)
                )
    
    return chessboard

class InfoDisplayFrame(customtkinter.CTkFrame):
    def __init__(self, master, globalVars: dict, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure((0, 1, 2, 3), weight=1)

        self.globalVars = globalVars

        # Variables
        self.selected = customtkinter.StringVar(value="No element selected")
        self.portview = customtkinter.CTkImage(dark_image=Image.new("RGBA", (16, 16)), size=(128, 128))
        self.changeTexture = False

        # Widgets

        self.portviewFrameCanvas = customtkinter.CTkCanvas(self, width=128, height=128)
        self.portviewFrameCanvas.grid(row=1, column=0, padx=5, pady=5, columnspan=2)

        self.portviewFrame = customtkinter.CTkLabel(self.portviewFrameCanvas, image=self.portview, text="", compound="top", bg_color="black")
        self.portviewFrame.grid(row=1, column=0, padx=2, pady=2)

        self.selectionLabel = customtkinter.CTkLabel(self, textvariable=self.selected)
        self.selectionLabel.grid(row=2, column=0, padx=5, pady=5, columnspan=2)

        self.buttonReplace = customtkinter.CTkButton(self, text="Replace", command=self.changeTextureCallback, state="disabled", width=100)
        self.buttonReplace.grid(row=3, column=0, padx=5, pady=5, sticky="wes")

        self.buttonExport = customtkinter.CTkButton(self, text="Export", state="disabled", command=self.saveAs, width=100)
        self.buttonExport.grid(row=3, column=1, padx=(0, 5), pady=5, sticky="wes")

        self.lastActualOption = None

    def saveAs(self):
        file = customtkinter.filedialog.asksaveasfile(mode="wb", defaultextension=".png", filetypes=(("PNG File", ".png"), ("3DST File", ".3dst")))
        if file:
            extension = Path(file.name).suffix
            value = self.selected.get()
            mainApp = self.master.master
            if value != "":
                selected = value
                atlasType = self.lastActualOption

                # Define variables by atlas type
                if atlasType == "Items":
                    element = self.globalVars["items"][selected]
                    atlas = self.globalVars["itemsAtlas"]
                elif atlasType == "Blocks":
                    element = self.globalVars["blocks"][selected]
                    atlas = self.globalVars["blocksAtlas"]
                position = element["uv"]

                # Copy region and export
                export = atlas.atlas.copy(position[0], position[1], position[0] + element["tileSize"], position[1] + element["tileSize"])
                if extension == ".png":
                    export.save(file)
                elif extension == ".3dst":
                    export3dst = Texture3dst().fromImage(export)
                    export3dst.export(file.name)
        file.close()

    def changeTextureCallback(self):
        self.changeTextureFunc(self.selected.get())

    def changeTextureFunc(self, value):
        mainApp = self.master.master
        mainFrame = self.master
        outputDir = self.globalVars["outputFolder"]
        allowResize = True if self.globalVars["allowResize"] == "true" else False

        atlasType = self.lastActualOption
        items = self.globalVars["items"]
        blocks = self.globalVars["blocks"]
        itemsAtlas = self.globalVars["itemsAtlas"]
        blocksAtlas = self.globalVars["blocksAtlas"]
        addedItems = self.globalVars["addedItems"]
        addedBlocks = self.globalVars["addedBlocks"]       

        # Define variables by atlas type
        if atlasType == "Items":
            added = addedItems
            atlas: atlasTexture3dst = itemsAtlas
            element = items[value]
        elif atlasType == "Blocks":
            added = addedBlocks
            atlas: atlasTexture3dst = blocksAtlas
            element = blocks[value]
        position = element["uv"]

        exts = Image.registered_extensions()
        supported_extensions = {ex for ex, f in exts.items() if f in Image.OPEN}
        exts_str = ""
        for idx, extension in enumerate(supported_extensions):
            exts_str += extension
            if idx < len(supported_extensions)-1:
                exts_str += " "
        filePath = customtkinter.filedialog.askopenfilename(filetypes=[("Image files", ".jpeg .jpg .gif .png .webp .tiff .tif .bmp .psd .ico"), ("All image files", exts_str)])
        if filePath != '':
            if not canOpenImage(filePath):
                messagebox.showerror("Failed to open image", "Unable to open the selected image")
            else:
                textureToReplace = Image.open(filePath)
                isSized = isImageSize(textureToReplace, element["tileSize"], element["tileSize"])
                if not isSized and not allowResize:
                    messagebox.showerror("Invalid texture", f"Texture selected is not {element['tileSize']}x{element['tileSize']}")
                else:
                    if not isSized:
                        textureToReplace = textureToReplace.resize((element['tileSize'], element['tileSize']), Image.Resampling.LANCZOS)
                    atlas.addElement(position, textureToReplace)
                    if atlasType == "Items":
                        duplicated = checkForMatch(value, added.getItems())

                        if not os.path.exists(f"{outputDir}/textures/items"):
                            os.makedirs(f"{outputDir}/textures/items")

                        newTexture = Texture3dst().fromImage(textureToReplace)
                        newTexture.export(f"{outputDir}/textures/items/{value}.3dst")

                        if duplicated == -1:
                            added.addItem(value)
                    elif atlasType == "Blocks":
                        duplicated = checkForMatch(value, added.getItems())

                        if not os.path.exists(f"{outputDir}/textures/blocks"):
                            os.makedirs(f"{outputDir}/textures/blocks")

                        newTexture = Texture3dst().fromImage(textureToReplace)
                        newTexture.export(f"{outputDir}/textures/blocks/{value}.3dst")

                        if duplicated == -1:
                            added.addItem(value)
                    
                    # Updates portview
                    mainFrame.listElementFun(value, self.lastActualOption)

                    self.globalVars["saved"] = False
                    self.globalVars["updateTreeIcons"]()
        self.buttonReplace.configure(state="normal")

    def showItemInfo(self, value = None, cat_opt = None):
        if value == None:
            item = self.globalVars["treeElementSelected"]
            values = item['values']
            name = values[1]
        else:
            name = value

        if self.buttonReplace.cget("state") == "disabled":
            self.buttonReplace.configure(state="normal")
        if self.buttonExport.cget("state") == "disabled":
            self.buttonExport.configure(state="normal")

        selected = name
        if selected != "No element selected" and selected != self.selected.get():
            self.selected.set(selected)
            if cat_opt == None:
                actualOpt = self.globalVars["searchData"][3]
            else:
                actualOpt = cat_opt
            self.lastActualOption = actualOpt

            # Set variables by atlas type
            if actualOpt == "Items":
                element = self.globalVars["items"][selected]
                atlas: atlasTexture3dst = self.globalVars["itemsAtlas"]
            elif actualOpt == "Blocks":
                element = self.globalVars["blocks"][selected]
                atlas: atlasTexture3dst = self.globalVars["blocksAtlas"]
            position = element["uv"]

            # Copy region and update display
            print(selected)
            portview = atlas.atlas.copy(position[0], position[1], position[0] + element["tileSize"], position[1] + element["tileSize"])
            portviewRes = portview.resize((256, 256), Image.Resampling.NEAREST)
            
            if self.globalVars["showPreviewBg"] == "true":
                backgound = _generateChessboardPattern(256, 256, tileSize=20)
                portviewRes = Image.alpha_composite(backgound, portviewRes)

            self.portview.configure(dark_image=portviewRes)