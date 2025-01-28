import os, sys
import difflib, threading, time
import configparser
import customtkinter, CTkMenuBar

from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw
from functools import partial
from pathlib import Path
from tkinter import messagebox
from AutoImport import *
from modules import *
from modules.MyCTkTopLevel import *
from py3dst import Texture3dst

VERSION = "3.0-dev"

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

def clearTreeview(tree: ttk.Treeview):
    for item in tree.get_children():
        tree.delete(item)

class SearchOptionsFrame(customtkinter.CTkFrame):
    def __init__(self, master, globalVars: dict, **kwargs):
        super().__init__(master, **kwargs)

        self.globalVars = globalVars

        # Variables
        self.searchText = customtkinter.StringVar(value="")
        self.lastSearchText = ""
        self.showModifiedVar = customtkinter.StringVar(value="off")
        self.lastModifiedVar = "off"
        self.showUnmodifiedVar = customtkinter.StringVar(value="on")
        self.lastUnmodifiedVar = "on"
        self.actualOpt = customtkinter.StringVar(value="Items")
        self.lastOpt = "Items"
        self.globalVars["searchDataLoc"] = ["", "off", "on", "Items"]

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

        self.showMenu = customtkinter.CTkComboBox(self.entryTextFrame, values=["Items", "Blocks"], variable=self.actualOpt, state="readonly")
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
            self.globalVars["searchDataLoc"][0] = self.lastSearchText
            self.globalVars["searchDataLoc"][1] = self.lastModifiedVar
            self.globalVars["searchDataLoc"][2] = self.lastUnmodifiedVar
            self.globalVars["searchDataLoc"][3] = self.lastOpt

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

        self.buttonReplace = customtkinter.CTkButton(self, text="Replace", command=self.changeTextureCall, state="disabled", width=100)
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

    def changeTextureCall(self):
        changeTexture = partial(self.changeTextureFunc, self.selected.get())
        self.buttonReplace.configure(state="disabled")
        threading.Thread(target=changeTexture).start()

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

                    mainApp.saved = False
                    mainApp.updateTreeIcons()
        self.buttonReplace.configure(state="normal")

class MainFrame(customtkinter.CTkFrame):
    def __init__(self, master, globalVars: dict, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_columnconfigure(0, weight=5)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.globalVars = globalVars

        self.searchOptionsFrame = SearchOptionsFrame(self, globalVars)
        self.searchOptionsFrame.grid(row=0, column=0, padx=5, pady=5, sticky="wen", columnspan=2)

        elementsFrame = customtkinter.CTkFrame(self)
        elementsFrame.grid_columnconfigure(0, weight=1)
        elementsFrame.grid_rowconfigure(0, weight=1)
        elementsFrame.grid(row=1, column=0, padx=5, pady=(0, 5), sticky="wens")

        elementsFrame2 = customtkinter.CTkFrame(elementsFrame)
        elementsFrame2.grid_columnconfigure(0, weight=1)
        elementsFrame2.grid_rowconfigure(0, weight=1)
        elementsFrame2.grid(row=0, column=0, sticky="wens")

        self.globalVars["elementsTreeView"] = ttk.Treeview(elementsFrame2, show="tree", selectmode="browse")
        self.globalVars["elementsTreeView"].bind('<<TreeviewSelect>>', self.listElementCallback)
        self.globalVars["elementsTreeView"].grid(row=0, column=0, padx=(5, 0), pady=5, sticky="wens")
        self.globalVars["elementsTreeView"].icons = []
        self.scrollbar = customtkinter.CTkScrollbar(elementsFrame2, command=self.globalVars["elementsTreeView"].yview)
        self.globalVars["elementsTreeView"].configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.grid(row=0, column=1, padx=0, pady=0, sticky="ns")

        self.infoDispFrame = InfoDisplayFrame(self, globalVars)
        self.infoDispFrame.grid(row=1, column=1, padx=(0, 5), pady=(0, 5), sticky="nswe")

    def listElementCallback(self, *event):
        threading.Thread(target=self.listElementFun).start()

    def listElementFun(self, value = None, cat_opt = None):
        if value == None:
            treeviewSelection = self.globalVars["elementsTreeView"].selection()
            if not treeviewSelection:
                return
            
            item = self.globalVars["elementsTreeView"].item(treeviewSelection)
            values = item['values']
            name = values[1]
            self.infoDispFrame.selected.set(name)
        else:
            name = value

        if self.infoDispFrame.buttonReplace.cget("state") == "disabled":
            self.infoDispFrame.buttonReplace.configure(state="normal")
        if self.infoDispFrame.buttonExport.cget("state") == "disabled":
            self.infoDispFrame.buttonExport.configure(state="normal")

        selected = name
        if selected != "No element selected":
            if cat_opt == None:
                actualOpt = self.globalVars["searchData"][3]
            else:
                actualOpt = cat_opt
            mainApp = self.master
            self.infoDispFrame.lastActualOption = actualOpt

            # Set variables by atlas type
            if actualOpt == "Items":
                element = self.globalVars["items"][selected]
                atlas = self.globalVars["itemsAtlas"]
            elif actualOpt == "Blocks":
                element = self.globalVars["blocks"][selected]
                atlas = self.globalVars["blocksAtlas"]
            position = element["uv"]

            # Copy region and update display
            print(selected)
            portview = atlas.atlas.copy(position[0], position[1], position[0] + element["tileSize"], position[1] + element["tileSize"])
            portviewRes = portview.resize((256, 256), Image.Resampling.NEAREST)
            
            if self.globalVars["showPreviewBg"] == "true":
                backgound = _generateChessboardPattern(256, 256, tileSize=20)
                portviewRes = Image.alpha_composite(backgound, portviewRes)

            self.infoDispFrame.portview.configure(dark_image=portviewRes)

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.version = VERSION

        # --------------------------------------------

        # Variables declaration
        self.globalVars = {}
        self.globalVars["searchData"] = ["", "off", "on", "Items"]
        self.globalVars["sourceFolder"] = "assets"
        self.globalVars["selected"] = ""
        self.globalVars["elementsList"] = []
        self.globalVars["updateList"] = True
        self.globalVars["saved"] = True
        self.globalVars["atlas"] = []
        
        #self.atlas = []
        self.settingsWindow = None

        # --------------------------------------------

        if getattr(sys, 'frozen', False):
            self.globalVars["running"] = "exe"
            self.globalVars["app_path"] = sys._MEIPASS
            self.globalVars["runningDir"] = os.path.dirname(sys.executable)
        elif __file__:
            self.globalVars["running"] = "src"
            self.globalVars["app_path"] = os.path.dirname(__file__)
            self.globalVars["runningDir"] = os.path.dirname(__file__)
        
        # Ini file
        self.config = configparser.ConfigParser()
        if os.path.exists(os.path.join(self.globalVars["runningDir"], "mc3ds-tm.ini")):
            self.config.read(os.path.join(self.globalVars["runningDir"], "mc3ds-tm.ini"))
        
        if not "Path" in self.config:
            self.config["Path"] = {}
        if not "lastdir" in self.config["Path"]:
            self.config["Path"]["lastdir"] = os.path.join(self.globalVars["runningDir"], "MC3DS")

        if not "Preferences" in self.config:
            self.config["Preferences"] = {}
        if not "theme" in self.config["Preferences"]:
            self.config["Preferences"]["theme"] = "dark"    
        if not "showpreviewbg" in self.config["Preferences"]:
            self.config["Preferences"]["showpreviewbg"] = "true"
        if not "allowresize" in self.config["Preferences"]:
            self.config["Preferences"]["allowresize"] = "true"

        if not os.path.exists(self.config["Path"]["lastdir"]):
            self.config["Path"]["lastdir"] = os.path.join(self.globalVars["runningDir"], "MC3DS")

        if not self.config["Preferences"]["theme"] in ["dark", "light"]:
            self.config["Preferences"]["theme"] = "dark"

        if not self.config["Preferences"]["showpreviewbg"] in ["true", "false"]:
            self.config["Preferences"]["showpreviewbg"] = "true"

        if not self.config["Preferences"]["allowresize"] in ["true", "false"]:
            self.config["Preferences"]["allowresize"] = "true"

        self.globalVars["outputFolder"] = self.config["Path"]["lastdir"]
        self.theme = self.config["Preferences"]["theme"]
        self.globalVars["showPreviewBg"] = self.config["Preferences"]["showpreviewbg"]
        self.globalVars["allowResize"] = self.config["Preferences"]["allowresize"]

        self.saveChangesForIniFile()
        self.changeTheme()

        self.title("MC3DS Texture Maker")
        os_name = os.name
        if os_name == "nt":
            self.iconbitmap(default=os.path.join(self.globalVars["app_path"], "icon.ico"))
        elif os_name == "posix":
            iconpath = ImageTk.PhotoImage(file=os.path.join(self.globalVars["app_path"], "icon.png"))
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
        fileMenu.add_separator()
        fileMenu.add_option("Save", command=self.saveChanges)
        fileMenu.add_separator()
        fileMenu.add_option("Settings", command=self.openSettings)
        fileMenu.add_separator()
        fileMenu.add_option("Exit", command=self.closeApp)

        toolsMenu = CTkMenuBar.CustomDropdownMenu(widget=menu_bar.add_cascade("Tools"))
        toolsMenu.add_option("Auto Import", command=self.openAutoImport)

        helpMenu = CTkMenuBar.CustomDropdownMenu(widget=menu_bar.add_cascade("Help"))
        helpMenu.add_option("About", command=self.about_popup)

        # --------------------------------------------

        # Main frame
        self.mainFrame = MainFrame(self, self.globalVars, fg_color="transparent")
        self.mainFrame.pack(side='left', expand=True, fill='both')

        # --------------------------------------------

        # Load indexes of blocks and items from source
        with open("./assets/uvs/atlas.items.vanilla.uvs.json", "r") as f:
            self.globalVars["items"] = json.load(f)
        with open("./assets/uvs/atlas.terrain.vanilla.uvs.json", "r") as f:
            self.globalVars["blocks"] = json.load(f)

        # Load resources
        self.loadResources()

        # Start daemon threads
        threadParams = threading.Thread(target=self.updateParamsThread)
        threadParams.daemon = True
        threadParams.start()

        listUpdateThread = threading.Thread(target=self.updateListThread)
        listUpdateThread.daemon = True
        listUpdateThread.start()

    def saveChangesForIniFile(self):
        with open(os.path.join(self.globalVars["runningDir"], "mc3ds-tm.ini"), "w") as configfile:
            self.config.write(configfile)

    def openFolder(self):
        if self.askForChanges():
            input = customtkinter.filedialog.askdirectory()
            if self.globalVars["outputFolder"] != input and input != '':
                self.globalVars["outputFolder"] = input
                self.config["Path"]["lastdir"] = input
                self.saveChangesForIniFile()
                self.loadResources()
                self.globalVars["saved"] = True
                self.globalVars["updateList"] = True

    def openSettings(self):
        if self.settingsWindow is None or not self.settingsWindow.winfo_exists():
            settingsWindow = MyCTkTopLevel(self)
            settingsWindow.title("Settings")
            settingsWindow.resizable(False, False)

            appearanceLabel = customtkinter.CTkLabel(settingsWindow, text="Appearance", font=(None, 14, "bold"))
            appearanceLabel.grid(column=0, row=0, padx=10, pady=(10, 0), sticky="ws")

            themeLabel = customtkinter.CTkLabel(settingsWindow, text="Theme", font=(None, 12))
            themeLabel.grid(column=0, row=1, padx=10, pady=0, sticky="ws")

            themeValue = customtkinter.StringVar(value=self.theme)
            appThemeCombobox = customtkinter.CTkComboBox(settingsWindow, values=["dark", "light"], variable=themeValue, state="readonly")
            appThemeCombobox.grid(column=0, row=2, padx=10, pady=(0, 10), sticky="w")

            previewBgValue = customtkinter.BooleanVar(value=True if self.globalVars["showPreviewBg"] == "true" else False)
            previewBgCheckbox = customtkinter.CTkCheckBox(settingsWindow, text="Show preview background", variable=previewBgValue, border_width=1, checkbox_width=20, checkbox_height=20)
            previewBgCheckbox.grid(column=0, row=3, padx=10, pady=(0, 2), sticky="w")

            allowResizeValue = customtkinter.BooleanVar(value=True if self.globalVars["allowResize"] == "true" else False)
            allowResizeCheckbox = customtkinter.CTkCheckBox(settingsWindow, text="Allow resize textures", variable=allowResizeValue, border_width=1, checkbox_width=20, checkbox_height=20)
            allowResizeCheckbox.grid(column=0, row=4, padx=10, pady=(0, 10), sticky="w")

            applyChanges = partial(self.applySettings, 
                                   {
                                       "theme": themeValue,
                                       "showpreviewbg": previewBgValue,
                                       "allowresize": allowResizeValue
                                   })
            
            discardChanges = partial(settingsWindow.destroy)

            cancelButton = customtkinter.CTkButton(settingsWindow, text="Cancel", command=discardChanges)
            cancelButton.grid(column=0, row=5, padx=10, pady=10, sticky="e")

            applyButton = customtkinter.CTkButton(settingsWindow, text="Apply", command=applyChanges)
            applyButton.grid(column=1, row=5, padx=(0, 10), pady=10)

            self.settingsWindow = settingsWindow
        else:
            self.settingsWindow.focus()

    def applySettings(self, newSettings: dict):
        self.settingsWindow.destroy()
        self.theme = newSettings["theme"].get()
        self.globalVars["showPreviewBg"] = "true" if newSettings["showpreviewbg"].get() else "false"
        self.globalVars["allowResize"] = "true" if newSettings["allowresize"].get() else "false"

        self.changeTheme()
        self.mainFrame.listElementFun()

        self.config["Preferences"]["theme"] = self.theme
        self.config["Preferences"]["showpreviewbg"] = self.globalVars["showPreviewBg"]
        self.config["Preferences"]["allowresize"] = self.globalVars["allowResize"]
        self.saveChangesForIniFile()

    def changeTheme(self):
        customtkinter.set_appearance_mode(self.theme)
        self.updateTreeviewTheme()

    def about_popup(self):
        about_text = f"MC3DS Texture Maker\nVersion: {self.version}\n\nMade by: STBrian\nGitHub: https://github.com/STBrian"
        messagebox.showinfo("About", about_text)

    def updateParamsThread(self):
        while True:
            if self.globalVars["searchData"] != self.globalVars["searchDataLoc"]:
                self.globalVars["searchData"] = self.globalVars["searchDataLoc"][::]
                self.globalVars["updateList"] = True
            time.sleep(0.5)

    def updateListThread(self):
        while True:
            if self.globalVars["updateList"] == True:
                self.globalVars["updateList"] = False
                mainFrame = self.mainFrame
                searchData = self.globalVars["searchData"]
                actualOpt = searchData[3]
                items = self.globalVars["items"]
                blocks = self.globalVars["blocks"]
                addedItems = self.globalVars["addedItems"]
                addedBlocks = self.globalVars["addedBlocks"]

                clearTreeview(self.globalVars["elementsTreeView"])

                if actualOpt == "Items":
                    elements: dict = items
                    added = addedItems
                elif actualOpt == "Blocks":
                    elements = blocks
                    added = addedBlocks

                elements = list(elements.keys())
                elements.sort()

                if (not searchData[0] == ""):
                    elements = difflib.get_close_matches(searchData[0], elements, n = len(elements), cutoff=0.4)
                
                if searchData[1] == "off":
                    elements = deleteMatches(elements, added.getItems())

                if searchData[2] == "off":
                    elements = checkForMatches(elements, added.getItems())

                self.globalVars["elementsTreeView"].icons = []
                for i in range(0, len(elements)):
                    self.globalVars["elementsTreeView"].insert("", "end", text="  " + elements[i], values=(i, elements[i]))
                    if self.globalVars["updateList"] == True:
                        break
                self.updateTreeIcons()
            time.sleep(0.5)

    def updateTreeIcons(self):
        mainFrame = self.mainFrame
        searchData = self.globalVars["searchData"]
        actualOpt = searchData[3]

        tree = self.globalVars["elementsTreeView"]
        tree.icons.clear()
        children = self.globalVars["elementsTreeView"].get_children("")
        for child in children:
            item = tree.item(child)
            values = item["values"]

            if actualOpt == "Items":
                atlas = self.globalVars["itemsAtlas"]
                element = self.globalVars["items"][values[1]]
                position = element["uv"]
            elif actualOpt == "Blocks":
                atlas = self.globalVars["blocksAtlas"]
                element = self.globalVars["blocks"][values[1]]
                position = element["uv"]

            textureExtract = atlas.atlas.copy(position[0], position[1], position[0] + element["tileSize"], position[1] + element["tileSize"])
            if textureExtract.size != (16, 16):
                textureExtract = textureExtract.resize((16, 16), Image.Resampling.LANCZOS)
            iconTk = ImageTk.PhotoImage(textureExtract)
            tree.icons.append(iconTk)
            tree.item(child, image=iconTk)

    def loadResources(self):
        # Load atlas either from source folder or output if exists
        if os.path.exists(os.path.normpath(f"{self.globalVars["outputFolder"]}/atlas/atlas.items.meta_79954554_0.3dst")):
            self.globalVars["itemsAtlas"] = atlasTexture3dst().open(os.path.normpath(f"{self.globalVars["outputFolder"]}/atlas/atlas.items.meta_79954554_0.3dst"), "Items")
        else:
            self.globalVars["itemsAtlas"] = atlasTexture3dst().open(os.path.join((self.globalVars["app_path"]), f"{self.globalVars["sourceFolder"]}/atlas/atlas.items.vanilla.png"), "Items")
        if os.path.exists(os.path.normpath(f"{self.globalVars["outputFolder"]}/atlas/atlas.terrain.meta_79954554_0.3dst")):
            self.globalVars["blocksAtlas"] = atlasTexture3dst().open(os.path.normpath(f"{self.globalVars["outputFolder"]}/atlas/atlas.terrain.meta_79954554_0.3dst"), "Blocks")
        else:
            self.globalVars["blocksAtlas"] = atlasTexture3dst().open(os.path.join((self.globalVars["app_path"]), f"{self.globalVars["sourceFolder"]}/atlas/atlas.terrain.vanilla.png"), "Blocks")

        # Load index of added blocks and items if exists
        if os.path.exists(os.path.normpath(f"{self.globalVars["outputFolder"]}/items.txt")):
            self.globalVars["addedItems"] = IndexFile().open(os.path.normpath(f"{self.globalVars["outputFolder"]}/items.txt"))
        else:
            self.globalVars["addedItems"] = IndexFile().new()
        if os.path.exists(os.path.normpath(f"{self.globalVars["outputFolder"]}/blocks.txt")):
            self.globalVars["addedBlocks"] = IndexFile().open(os.path.normpath(f"{self.globalVars["outputFolder"]}/blocks.txt"))
        else:
            self.globalVars["addedBlocks"] = IndexFile().new()
        return
    
    def saveChanges(self):
        if not self.saved:
            out = os.path.join(self.globalVars["outputFolder"], "atlas")
            if not os.path.exists(out):
                os.makedirs(out)
            self.globalVars["itemsAtlas"].save(os.path.normpath(f"{self.globalVars["outputFolder"]}/atlas/atlas.items.meta_79954554_0.3dst"))
            self.globalVars["blocksAtlas"].save(os.path.normpath(f"{self.globalVars["outputFolder"]}/atlas/atlas.terrain.meta_79954554_0.3dst"))
            self.globalVars["addedItems"].save(os.path.normpath(f"{self.globalVars["outputFolder"]}/items.txt"))
            self.globalVars["addedBlocks"].save(os.path.normpath(f"{self.globalVars["outputFolder"]}/blocks.txt"))
            self.saved = True

    def openAutoImport(self):
        autoImport = AutoImport(self)

    def closeApp(self, val=None):
        if self.globalVars["saved"]:
            sys.exit()
        else:
            print("Not saved")
            op = messagebox.askyesnocancel(title="Unsaved changes", message="There are unsaved changes. Would you like to save them before exit?")
            if op == True:
                self.saveChanges()
                sys.exit()
            elif op == False:
                sys.exit()
            else:
                pass

    def askForChanges(self):
        if self.globalVars["saved"]:
            return True
        else:
            print("Not saved")
            op = messagebox.askyesnocancel(title="Unsaved changes", message="There are unsaved changes. Would you like to save them?")
            if op == True:
                self.saveChanges()
                return True
            elif op == False:
                return True
            else:
                return False
            
    def updateTreeviewTheme(self):
        bg_color = self._apply_appearance_mode(customtkinter.ThemeManager.theme["CTkFrame"]["fg_color"])
        text_color = self._apply_appearance_mode(customtkinter.ThemeManager.theme["CTkLabel"]["text_color"])
        selected_color = self._apply_appearance_mode(customtkinter.ThemeManager.theme["CTkButton"]["fg_color"])

        treestyle = ttk.Style()
        treestyle.theme_use('default')
        treestyle.configure("Treeview", background=bg_color, foreground=text_color, fieldbackground=bg_color, borderwidth=0, font=(None, 10), rowheight=36)
        treestyle.map('Treeview', background=[('selected', selected_color)], foreground=[('selected', text_color)])

if __name__ == "__main__":
    customtkinter.set_default_color_theme("blue")
    
    print("Loading app...")
    app = App()

    app.updateTreeviewTheme()
    app.bind("<<TreeviewSelect>>", lambda event: app.focus_set())

    app.bind('<Alt-F4>', app.closeApp)
    app.protocol("WM_DELETE_WINDOW", app.closeApp)

    app.mainloop()
