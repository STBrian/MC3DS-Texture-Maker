import os
import customtkinter
from PIL import Image, ImageDraw
from pathlib import Path
from py3dst import Texture3dst
from tkinter import messagebox
from modules import atlasTexture3dst, canOpenImage, isImageSize, checkForMatch
from appGlobalVars import appGlobalVars

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
    def __init__(self, master, globalVars: appGlobalVars, **kwargs):
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
            if value != "":
                selected = value

                element = self.globalVars.items[selected]
                atlas = self.globalVars.atlasHandler
                position = element["uv"]

                # Copy region and export
                export = atlas.atlas.cropToImage(position[0], position[1], position[2], position[3])
                if extension == ".png":
                    export.save(file)
                elif extension == ".3dst":
                    export3dst = Texture3dst().fromImage(export)
                    export3dst.export(file.name)
            file.close()

    def changeTextureCallback(self):
        self.changeTextureFunc(self.selected.get())

    def changeTextureFunc(self, value):
        outputDir = self.globalVars.outputFolder
        allowResize = self.globalVars.allowResize

        added = self.globalVars.addedItems
        atlas: atlasTexture3dst = self.globalVars.atlasHandler
        element = self.globalVars.items[value]
        position = element["uv"]

        exts = Image.registered_extensions()
        supported_extensions = {ex for ex, f in exts.items() if f in Image.OPEN}
        exts_str = ""
        for idx, extension in enumerate(supported_extensions):
            exts_str += extension
            if idx < len(supported_extensions)-1:
                exts_str += " "
        filePath = customtkinter.filedialog.askopenfilename(filetypes=[("Image files", ".jpeg .jpg .gif .png .webp .tiff .tif .bmp .psd .ico"), ("All image files", exts_str)])
        if filePath != '' and isinstance(filePath, str):
            if not canOpenImage(filePath):
                messagebox.showerror("Failed to open image", "Unable to open the selected image")
            else:
                textureToReplace = Image.open(filePath)
                isSized = isImageSize(textureToReplace, position[2] - position[0], position[3] - position[1])
                if not isSized and not allowResize:
                    messagebox.showerror("Invalid texture", f"Texture selected is not {position[2] - position[0]}x{position[3] - position[1]}")
                else:
                    if not isSized:
                        resampling = Image.Resampling.LANCZOS
                        if self.globalVars.resamplingType == "Bilinear":
                            resampling = Image.Resampling.BILINEAR
                        elif self.globalVars.resamplingType == "Nearest":
                            resampling = Image.Resampling.NEAREST
                        textureToReplace = textureToReplace.resize((position[2] - position[0], position[3] - position[1]), resampling)
                    atlas.addElement(position, textureToReplace)
                    duplicated = checkForMatch(value, added.getItems())

                    if not os.path.exists(f"{outputDir}/textures"):
                        os.makedirs(f"{outputDir}/textures")

                    newTexture = Texture3dst().fromImage(textureToReplace)
                    newTexture.export(f"{outputDir}/textures/{value}.3dst")

                    if duplicated == -1:
                        added.addItem(value)
                    
                    # Updates portview
                    self.showItemInfo(value)

                    self.globalVars.saved = False
                    self.globalVars.updateList()
        self.buttonReplace.configure(state="normal")

    def showItemInfo(self, value = None):
        if value == None:
            item = self.globalVars.treeElementSelected
            if not "values" in item:
                return
            print(item)
            values = item['values']
            if values == '':
                return
            name = values[1]
        else:
            name = value

        if self.buttonReplace.cget("state") == "disabled":
            self.buttonReplace.configure(state="normal")
        if self.buttonExport.cget("state") == "disabled":
            self.buttonExport.configure(state="normal")

        selected = name
        if selected != "No element selected":
            self.selected.set(selected)

            element = self.globalVars.items[selected]
            atlas: atlasTexture3dst = self.globalVars.atlasHandler
            position = element["uv"]

            # Copy region and update display
            print(selected)
            portview = atlas.cropToImage(position[0], position[1], position[2], position[3])
            portviewRes = portview.resize((256, 256), Image.Resampling.NEAREST)
            
            if self.globalVars.showPreviewBg:
                backgound = _generateChessboardPattern(256, 256, tileSize=20)
                portviewRes = Image.alpha_composite(backgound, portviewRes)

            self.portview.configure(dark_image=portviewRes)