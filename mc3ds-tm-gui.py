import os
import sys
import difflib
import customtkinter
import CTkMenuBar
import threading
import time
import numpy
from PIL import Image
from PIL import ImageTk
from functools import partial
from pathlib import Path

import tools
from modules import *

class SearchOptionsFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        # Variables
        self.searchText = customtkinter.StringVar(value="")
        self.lastSearchText = ""
        self.showModifiedVar = customtkinter.StringVar(value="off")
        self.lastModifiedVar = "off"
        self.showUnmodifiedVar = customtkinter.StringVar(value="on")
        self.lastUnmodifiedVar = "on"
        self.actualOpt = customtkinter.StringVar(value="Items")
        self.lastOpt = "Items"
        self.searchDataLoc = ["", "off", "on", "Items"]

        self.grid_columnconfigure(0, weight=1)

        self.searchOptionsLabel = customtkinter.CTkLabel(self, text="Search options:")
        self.searchOptionsLabel.grid(row=0, column=0, padx=5, sticky="wn")

        self.showUnmodifiedSwitch = customtkinter.CTkSwitch(self, text="Show unmodified elements", onvalue="on", offvalue="off", variable=self.showUnmodifiedVar)
        self.showUnmodifiedSwitch.grid(row=1, column=0, padx=5, pady=0, sticky="wn")

        self.showModifiedSwitch = customtkinter.CTkSwitch(self, text="Show modified elements", onvalue="on", offvalue="off", variable=self.showModifiedVar)
        self.showModifiedSwitch.grid(row=2, column=0, padx=5, pady=5, sticky="wn")

        self.entryTextFrame = customtkinter.CTkFrame(self)
        self.entryTextFrame.grid(row=3, column=0, padx=5, pady=5, sticky="wen")
        self.entryTextFrame.grid_columnconfigure(1, weight=1)

        self.showMenu = customtkinter.CTkComboBox(self.entryTextFrame, values=["Items", "Blocks"], variable=self.actualOpt)
        self.showMenu.grid(row=0, column=0, padx=5, pady=0, sticky="w")

        self.entryText = customtkinter.CTkEntry(self.entryTextFrame, textvariable=self.searchText, placeholder_text="Search")
        self.entryText.grid(row=0, column=1, padx=0, pady=5, sticky="wen")

        self.button = customtkinter.CTkButton(self.entryTextFrame, text="Search", width=80, command=self.saveSearch)
        self.button.grid(row=0, column=2, padx=5, pady=5, sticky="wn")
        
    def saveSearch(self):
        if self.lastSearchText != self.searchText.get() or self.lastModifiedVar != self.showModifiedVar.get() or self.lastUnmodifiedVar != self.showUnmodifiedVar.get() or self.lastOpt != self.actualOpt.get():
            self.lastSearchText = self.searchText.get()
            self.lastModifiedVar = self.showModifiedVar.get()
            self.lastUnmodifiedVar = self.showUnmodifiedVar.get()
            self.lastOpt = self.actualOpt.get()
            self.searchDataLoc[0] = self.lastSearchText
            self.searchDataLoc[1] = self.lastModifiedVar
            self.searchDataLoc[2] = self.lastUnmodifiedVar
            self.searchDataLoc[3] = self.lastOpt

class InfoDisplayFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure((0, 1, 2, 3), weight=1)

        # Variables
        self.selected = customtkinter.StringVar(value="")
        self.portview = customtkinter.CTkImage(dark_image=Image.new("RGBA", (16, 16)), size=(128, 128))
        self.changeTexture = False

        # Widgets
        self.noSelectedText = customtkinter.CTkLabel(self, text="No element selected")
        self.noSelectedText.grid(row=0, column=0, padx=5, pady=5, columnspan=2)

        self.portviewFrame = customtkinter.CTkLabel(self, image=self.portview, text="", compound="top")
        self.portviewFrame.grid(row=1, column=0, padx=5, pady=5, columnspan=2)

        self.selectionLabel = customtkinter.CTkLabel(self, textvariable=self.selected)
        self.selectionLabel.grid(row=2, column=0, padx=5, pady=5, columnspan=2)

        self.buttonChange = customtkinter.CTkButton(self, text="Change", command=self.changeTextureCall, state="disabled", width=100)
        self.buttonChange.grid(row=3, column=0, padx=5, pady=5, sticky="wes")

        self.buttonExport = customtkinter.CTkButton(self, text="Export", state="disabled", command=self.saveAs, width=100)
        self.buttonExport.grid(row=3, column=1, padx=(0, 5), pady=5, sticky="wes")

    def saveAs(self):
        file = customtkinter.filedialog.asksaveasfile(mode="wb", defaultextension=".png", filetypes=(("PNG File", ".png"), ("3DST File", ".3dst")))
        if file:
            extension = Path(file.name).suffix
            value = self.selected.get()
            root = self.master.master
            if value != "":
                selected = value
                actualOpt = root.searchData[3]

                # Calculate positions
                if actualOpt == "Items":
                    matchwith = checkForMatch(selected, root.items)
                    position = calculateGrid(matchwith, 32, 13, 16)
                elif actualOpt == "Blocks":
                    matchwith = checkForMatch(selected, root.blocks)
                    position = calculateGrid(matchwith, 25, 22, 20)
                    position = (position[0] + 2, position[1] + 2)

                # Load atlas
                if actualOpt == "Items":
                    atlas = root.atlas[1]
                    idx = 0
                elif actualOpt == "Blocks":
                    atlas = root.atlas[3]
                    idx = 2

                # Copy region and export
                if root.atlas[idx] == 1:
                    box = (position[0], position[1], position[0] + 16, position[1] + 16)
                    region = atlas.crop(box)
                    export = Image.new("RGBA", (16, 16))
                    export.paste(region, (0, 0))
                else:
                    region = atlas.copy(position[0], position[1], position[0] + 16, position[1] + 16)
                    buffer = numpy.asarray(region, dtype=numpy.uint8)
                    export = Image.fromarray(buffer)

                if extension == ".png":
                    export.save(file)
                elif extension == ".3dst":
                    export3dst = Texture3dst().new(16, 16, 1)
                    export3dst.paste(export, 0, 0)
                    export3dst.convertData()
                    export3dst.export(file.name)
        file.close()

    def changeTextureCall(self):
        changeTexture = partial(self.changeTextureFunc, self.selected.get())
        threading.Thread(target=changeTexture).start()

    def changeTextureFunc(self, value):
        root = self.master.master
        mainFrame = self.master

        actualOpt = root.searchData[3]
        outputFolder = root.outputFolder
        items = root.items
        blocks = root.blocks
        app_path = root.app_path
        sourceFolder = root.sourceFolder

        # Load indexes
        added = []
        if actualOpt == "Items":
            if os.path.exists(os.path.join(outputFolder, "items.txt")):
                added = getItemsFromIndexFile(os.path.join(outputFolder, "items.txt"))
        elif actualOpt == "Blocks":
            if os.path.exists(os.path.join(outputFolder, "blocks.txt")):
                added = getItemsFromIndexFile(os.path.join(outputFolder, "blocks.txt"))

        # Calculate positions
        if actualOpt == "Items":
            matchwith = checkForMatch(value, items)
            position = calculateGrid(matchwith, 32, 13, 16)
        elif actualOpt == "Blocks":
            matchwith = checkForMatch(value, blocks)
            position = calculateGrid(matchwith, 25, 22, 20)

        filePath = customtkinter.filedialog.askopenfilename(filetypes=[("Image files", ".png .jpg")])
        if filePath != '':
            if isImage16x16(filePath):
                if actualOpt == "Items":
                    addToItemAtlas(position, filePath, os.path.join(app_path, sourceFolder), outputFolder)
                    duplicated = checkForMatch(items[matchwith], added)
                    if duplicated == -1:
                        addElementToFile(items[matchwith], os.path.join(outputFolder, "items.txt"))
                elif actualOpt == "Blocks":
                    addToBlockAtlas(position, filePath, os.path.join(app_path, sourceFolder), outputFolder)
                    duplicated = checkForMatch(blocks[matchwith], added)
                    if duplicated == -1:
                        addElementToFile(blocks[matchwith], os.path.join(outputFolder, "blocks.txt"))
                root.reloadAtlas()
                mainFrame.listElementCall(value)

class MainFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_columnconfigure(0, weight=5)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.searchOptionsFrame = SearchOptionsFrame(self)
        self.searchOptionsFrame.grid(row=0, column=0, padx=5, pady=5, sticky="wen", columnspan=2)

        self.elementsFrame = MyCTkListbox(self, command=self.listElementCall)
        self.elementsFrame.grid(row=1, column=0, padx=5, pady=(0, 5), sticky="wens")

        self.infoDispFrame = InfoDisplayFrame(self)
        self.infoDispFrame.grid(row=1, column=1, padx=(0, 5), pady=(0, 5), sticky="nswe")

    def listElementCall(self, value):
        listElement = partial(self.listElementFun, value)
        threading.Thread(target=listElement).start()

    def listElementFun(self, value):
        if value != "":
            self.updateElement = False
            self.infoDispFrame.noSelectedText.grid_remove()
            if self.infoDispFrame.buttonChange.cget("state") == "disabled":
                self.infoDispFrame.buttonChange.configure(state="normal")
            if self.infoDispFrame.buttonExport.cget("state") == "disabled":
                self.infoDispFrame.buttonExport.configure(state="normal")
            self.infoDispFrame.selected.set(value)

            selected = value
            actualOpt = self.master.searchData[3]
            master = self.master

            # Calculate positions
            if actualOpt == "Items":
                matchwith = checkForMatch(selected, master.items)
                position = calculateGrid(matchwith, 32, 13, 16)
            elif actualOpt == "Blocks":
                matchwith = checkForMatch(selected, master.blocks)
                position = calculateGrid(matchwith, 25, 22, 20)
                position = (position[0] + 2, position[1] + 2)

            # Load atlas
            if actualOpt == "Items":
                atlas = master.atlas[1]
                idx = 0
            elif actualOpt == "Blocks":
                atlas = master.atlas[3]
                idx = 2

            # Copy region and update display
            if master.atlas[idx] == 1:
                box = (position[0], position[1], position[0] + 16, position[1] + 16)
                region = atlas.crop(box)
                portview = Image.new("RGBA", (16, 16))
                portview.paste(region, (0, 0))
            else:
                region = atlas.copy(position[0], position[1], position[0] + 16, position[1] + 16)
                buffer = numpy.asarray(region, dtype=numpy.uint8)
                portview = Image.fromarray(buffer)
            portviewRes = portview.resize((256, 256), Image.Resampling.NEAREST)
            self.infoDispFrame.portview.configure(dark_image=portviewRes)

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # --------------------------------------------

        # Variables declaration
        self.searchData = ["", "off", "on", "Items"]
        self.sourceFolder = "assets"
        self.selected = ""
        self.elementsList = []
        self.updateList = True
        self.atlas = []

        # --------------------------------------------

        if getattr(sys, 'frozen', False):
            self.running = "exe"
            self.app_path = sys._MEIPASS
            self.runningDir = os.path.dirname(sys.executable)
            self.outputFolder = os.path.join(self.runningDir, "MC3DS")
        elif __file__:
            self.running = "src"
            self.app_path = os.path.dirname(__file__)
            self.runningDir = os.path.dirname(__file__)
            self.outputFolder = os.path.join(self.runningDir, "MC3DS")

        self.title("MC3DS Texture Maker")
        os_name = os.name
        if os_name == "nt":
            self.iconbitmap(default=os.path.join(self.app_path, "icon.ico"))
        elif os_name == "posix":
            iconpath = ImageTk.PhotoImage(file=os.path.join(self.app_path, "icon.png"))
            self.wm_iconbitmap()
            self.iconphoto(False, iconpath)

        self.geometry("580x420")
        self.minsize(580, 420)
        self.resizable(True, True)

        # --------------------------------------------

        # Menu bar
        menu_bar = CTkMenuBar.CTkMenuBar(master=self, height=15)

        fileMenu = CTkMenuBar.CustomDropdownMenu(widget=menu_bar.add_cascade("File"))
        fileMenu.add_option("Open folder", command=self.openFolder)
        fileMenu.add_option("Preferences")
        fileMenu.add_separator()
        fileMenu.add_option("Exit", command=sys.exit)

        toolsMenu = CTkMenuBar.CustomDropdownMenu(widget=menu_bar.add_cascade("Tools"))
        toolsMenu.add_option("Auto importer", command=self.openAutoImporter)

        helpMenu = CTkMenuBar.CustomDropdownMenu(widget=menu_bar.add_cascade("Help"))
        helpMenu.add_option("About")

        # --------------------------------------------

        # Main frame
        self.mainFrame = MainFrame(self, fg_color="transparent")
        self.mainFrame.pack(side='left', expand=True, fill='both')

        # --------------------------------------------

        # Initial loading
        self.items = getItemsFromIndexFile(os.path.join(self.app_path, f"{self.sourceFolder}/indexes/items.txt"))
        self.blocks = getItemsFromIndexFile(os.path.join(self.app_path, f"{self.sourceFolder}/indexes/blocks.txt"))
        self.reloadAtlas()

        # Start daemon threads
        threadParams = threading.Thread(target=self.updateParamsThread)
        threadParams.daemon = True
        threadParams.start()

        listUpdateThread = threading.Thread(target=self.updateListThread)
        listUpdateThread.daemon = True
        listUpdateThread.start()

    def openFolder(self):
        input = customtkinter.filedialog.askdirectory()
        if self.outputFolder != input and input != '':
            self.outputFolder = input
            self.reloadAtlas()
            self.updateList = True

    def updateParamsThread(self):
        while True:
            if self.searchData != self.mainFrame.searchOptionsFrame.searchDataLoc:
                self.searchData = self.mainFrame.searchOptionsFrame.searchDataLoc[0:4]
                self.updateList = True

            if f"{self.searchData[3]}:" != self.mainFrame.elementsFrame.cget("label_text"):
                self.mainFrame.elementsFrame.configure(label_text=f"{self.searchData[3]}:")
            time.sleep(0.5)

    def updateListThread(self):
        while True:
            if self.updateList == True:
                self.updateList = False
                root = self
                mainFrame = self.mainFrame
                searchData = self.searchData
                actualOpt = searchData[3]
                items = root.items
                blocks = root.blocks
                outputFolder = root.outputFolder

                mainFrame.elementsFrame.delete("all")

                elements = []
                added = []
                if actualOpt == "Items":
                    elements = items
                    if os.path.exists(os.path.join(outputFolder, "items.txt")):
                        added = getItemsFromIndexFile(os.path.join(outputFolder, "items.txt"))
                elif actualOpt == "Blocks":
                    elements = blocks
                    if os.path.exists(os.path.join(outputFolder, "blocks.txt")):
                        added = getItemsFromIndexFile(os.path.join(outputFolder, "blocks.txt"))

                if (not searchData[0] == ""):
                    elements = difflib.get_close_matches(searchData[0], elements, cutoff=0.4)
                
                if searchData[1] == "off":
                    elements = deleteMatches(elements, added)

                if searchData[2] == "off":
                    elements = checkForMatches(elements, added)

                for i in range(0, len(elements)):
                    mainFrame.elementsFrame.insert(i, elements[i])
                    if self.updateList == True:
                        break
            time.sleep(0.5)

    def reloadAtlas(self):
        self.atlas = []
        if os.path.exists(os.path.normpath(f"{self.outputFolder}/atlas/atlas.items.meta_79954554_0.3dst")):
            atlas = Texture3dst().open(os.path.normpath(f"{self.outputFolder}/atlas/atlas.items.meta_79954554_0.3dst"))
            atlas.flipX()
            self.atlas.append(2)
        else:
            atlas = Image.open(os.path.join((self.app_path), f"{self.sourceFolder}/atlas/atlas.items.vanilla.png"))
            self.atlas.append(1)
        self.atlas.append(atlas)
        if os.path.exists(os.path.normpath(f"{self.outputFolder}/atlas/atlas.terrain.meta_79954554_0.3dst")):
            atlas = Texture3dst().open(os.path.normpath(f"{self.outputFolder}/atlas/atlas.terrain.meta_79954554_0.3dst"))
            atlas.flipX()
            self.atlas.append(2)
        else:
            atlas = Image.open(os.path.join((self.app_path), f"{self.sourceFolder}/atlas/atlas.terrain.vanilla.png"))
            self.atlas.append(1)
        self.atlas.append(atlas)
        return

    def openAutoImporter(self):
        autoImporter = tools.AutoImporter(self)

def closeApp(val=None):
    sys.exit()

customtkinter.set_default_color_theme("blue")
customtkinter.set_appearance_mode("dark")

app = App()

app.bind('<Alt-F4>', closeApp)
app.protocol("WM_DELETE_WINDOW", closeApp)

app.mainloop()
