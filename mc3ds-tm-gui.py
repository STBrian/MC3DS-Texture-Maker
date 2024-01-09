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

from modules.stbmodule import *
from modules.tex3dst import *

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

        self.grid(row=0, column=0, padx=5, pady=5, sticky="wen", columnspan=2)
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

class ElementsFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.grid(row=1, column=0, padx=5, pady=(0, 5), sticky="wens")
        self.grid_columnconfigure(0, weight=1)

class InfoDisplayFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid(row=1, column=1, padx=(0, 5), pady=(0, 5), sticky="nswe")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1, 2, 3), weight=1)

        self.selected = customtkinter.StringVar(value="")
        self.portview = customtkinter.CTkImage(dark_image=Image.new("RGBA", (16, 16)), size=(128, 128))
        self.changeTexture = False

        self.noSelectedText = customtkinter.CTkLabel(self, text="No element selected")
        self.noSelectedText.grid(row=0, column=0, padx=5, pady=5)

        self.portviewFrame = customtkinter.CTkLabel(self, image=self.portview, text="", compound="top")
        self.portviewFrame.grid(row=1, column=0, padx=5, pady=5)

        self.selectionLabel = customtkinter.CTkLabel(self, textvariable=self.selected)
        self.selectionLabel.grid(row=2, column=0, padx=5, pady=5)

        self.buttonChange = customtkinter.CTkButton(self, text="Change", command=self.changeTextureFunc, state="disabled")
        self.buttonChange.grid(row=3, column=0, padx=5, pady=5, sticky="wes")

    def changeTextureFunc(self):
        self.changeTexture = True

class MainFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.pack(side='left', expand=True, fill='both')
        self.grid_columnconfigure(0, weight=5)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.searchOptionsFrame = SearchOptionsFrame(self)
        self.elementsFrame = ElementsFrame(self, label_text="Items:")
        self.infoDispFrame = InfoDisplayFrame(self)

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # --------------------------------------------

        # Variables declaration
        self.updateDisplayList = True
        self.searchData = ["", "off", "on", "Items"]
        self.sourceFolder = "assets"
        self.selected = ""
        self.elementsList = []
        self.updateElement = False
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
        toolsMenu.add_option("Dummy 1")
        toolsMenu.add_option("Dummy 2")
        toolsMenu.add_option("Dummy 3")

        helpMenu = CTkMenuBar.CustomDropdownMenu(widget=menu_bar.add_cascade("Help"))
        helpMenu.add_option("About")

        # --------------------------------------------

        # Main frame
        self.mainFrame = MainFrame(self, fg_color="transparent")

        # --------------------------------------------

        # Initial loading
        self.items = getItemsFromIndexFile(os.path.join(self.app_path, f"{self.sourceFolder}/indexes/newitemslist.txt"))
        self.blocks = getItemsFromIndexFile(os.path.join(self.app_path, f"{self.sourceFolder}/indexes/newblockslist.txt"))
        self.reloadAtlas()

        # Start daemon threads
        threadParams = threading.Thread(target=self.updateParamsThread)
        threadParams.daemon = True
        threadParams.start()

        threadDisplayList = threading.Thread(target=self.updateDisplayListThread)
        threadDisplayList.daemon = True
        threadDisplayList.start()

        threadListElement = threading.Thread(target=self.listElementCickedThread)
        threadListElement.daemon = True
        threadListElement.start()

        threadTextureChange = threading.Thread(target=self.changeTextureThread)
        threadTextureChange.daemon = True
        threadTextureChange.start()

    def openFolder(self):
        input = customtkinter.filedialog.askdirectory()
        if self.outputFolder != input and input != '':
            self.outputFolder = input
            self.reloadAtlas()
            self.updateDisplayList = True

    def updateParamsThread(self):
        while True:
            if not (self.searchData == self.mainFrame.searchOptionsFrame.searchDataLoc):
                self.searchData = self.mainFrame.searchOptionsFrame.searchDataLoc[0:4]
                self.updateDisplayList = True

            if f"{self.searchData[3]}:" != self.mainFrame.elementsFrame.cget("label_text"):
                self.mainFrame.elementsFrame.configure(label_text=f"{self.searchData[3]}:")
            time.sleep(0.5)

    def changeTextureThread(self):
        while True:
            if self.mainFrame.infoDispFrame.changeTexture == True and self.mainFrame.infoDispFrame.selected.get() != "":
                self.mainFrame.infoDispFrame.changeTexture = False
                value = self.mainFrame.infoDispFrame.selected.get()
                actualOpt = self.searchData[3]
                outputFolder = self.outputFolder
                items = self.items
                blocks = self.blocks
                app_path = self.app_path
                sourceFolder = self.sourceFolder

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
                        self.reloadAtlas()
                        self.updateElement = True
            time.sleep(0.5)

    def updateDisplayListThread(self):
        while True:
            if self.updateDisplayList == True:
                self.updateDisplayList = False
                actualOpt = self.searchData[3]
                
                for element in self.elementsList:
                    element.grid_remove()

                for element in self.elementsList:
                    element.destroy()

                self.elementsList = []
                elements = []
                added = []
                if actualOpt == "Items":
                    elements = self.items
                    if os.path.exists(os.path.join(self.outputFolder, "items.txt")):
                        added = getItemsFromIndexFile(os.path.join(self.outputFolder, "items.txt"))
                elif actualOpt == "Blocks":
                    elements = self.blocks
                    if os.path.exists(os.path.join(self.outputFolder, "blocks.txt")):
                        added = getItemsFromIndexFile(os.path.join(self.outputFolder, "blocks.txt"))

                if (not self.searchData[0] == ""):
                    elements = difflib.get_close_matches(self.searchData[0], elements, cutoff=0.4)
                
                if self.searchData[1] == "off":
                    elements = deleteMatches(elements, added)

                if self.searchData[2] == "off":
                    elements = checkForMatches(elements, added)

                for i in range(0, len(elements)):
                    self.listElement = customtkinter.CTkButton(self.mainFrame.elementsFrame, text=elements[i], fg_color="transparent", anchor="w", command=lambda v=elements[i]: self.listElementDisplay(v))
                    self.listElement.grid(row=i, column=0, padx=5, pady=(5, 0), sticky="w")
                    self.elementsList.append(self.listElement)
                    if self.updateDisplayList == True:
                        break
            time.sleep(0.5)

    def listElementDisplay(self, value):
            self.mainFrame.infoDispFrame.selected.set(value)

    def listElementCickedThread(self):
        while True:
            if (self.selected != self.mainFrame.infoDispFrame.selected.get() and self.mainFrame.infoDispFrame.selected.get() != "") or self.updateElement == True:
                self.updateElement = False
                self.mainFrame.infoDispFrame.noSelectedText.grid_remove()
                self.mainFrame.infoDispFrame.buttonChange.configure(state="normal")

                self.selected = self.mainFrame.infoDispFrame.selected.get()
                selected = self.selected
                actualOpt = self.searchData[3]

                # Calculate positions
                if actualOpt == "Items":
                    matchwith = checkForMatch(selected, self.items)
                    position = calculateGrid(matchwith, 32, 13, 16)
                elif actualOpt == "Blocks":
                    matchwith = checkForMatch(selected, self.blocks)
                    position = calculateGrid(matchwith, 25, 22, 20)
                    position = (position[0] + 2, position[1] + 2)

                # Load atlas
                if actualOpt == "Items":
                    atlas = self.atlas[1]
                    idx = 0
                elif actualOpt == "Blocks":
                    atlas = self.atlas[3]
                    idx = 2

                # Copy region and update display
                if self.atlas[idx] == 1:
                    box = (position[0], position[1], position[0] + 16, position[1] + 16)
                    region = atlas.crop(box)
                    portview = Image.new("RGBA", (16, 16))
                    portview.paste(region, (0, 0))
                else:
                    region = atlas.copy(position[0], position[1], position[0] + 16, position[1] + 16)
                    buffer = numpy.asarray(region, dtype=numpy.uint8)
                    portview = Image.fromarray(buffer)
                portviewRes = portview.resize((256, 256), Image.Resampling.NEAREST)
                self.mainFrame.infoDispFrame.portview.configure(dark_image=portviewRes)
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

def closeApp(val=None):
    sys.exit()

customtkinter.set_default_color_theme("blue")
customtkinter.set_appearance_mode("dark")

app = App()

app.bind('<Alt-F4>', closeApp)
app.protocol("WM_DELETE_WINDOW", closeApp)

app.mainloop()
