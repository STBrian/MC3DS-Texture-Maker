import os, sys
import difflib, threading, time
import configparser
import customtkinter, CTkMenuBar
from PIL import Image
from PIL import ImageTk
import platform
from functools import partial
from pathlib import Path
from tkinter import messagebox
from AutoImport import *
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

        self.buttonChange = customtkinter.CTkButton(self, text="Change", command=self.changeTextureCall, state="disabled", width=100)
        self.buttonChange.grid(row=3, column=0, padx=5, pady=5, sticky="wes")

        self.buttonExport = customtkinter.CTkButton(self, text="Export", state="disabled", command=self.saveAs, width=100)
        self.buttonExport.grid(row=3, column=1, padx=(0, 5), pady=5, sticky="wes")

    def saveAs(self):
        file = customtkinter.filedialog.asksaveasfile(mode="wb", defaultextension=".png", filetypes=(("PNG File", ".png"), ("3DST File", ".3dst")))
        if file:
            extension = Path(file.name).suffix
            value = self.selected.get()
            mainApp = self.master.master
            if value != "":
                selected = value
                actualOpt = mainApp.searchData[3]

                # Calculate positions
                if actualOpt == "Items":
                    matchwith = checkForMatch(selected, mainApp.items.getItems())
                    position = calculateGrid(matchwith, 32, 13, 16)
                elif actualOpt == "Blocks":
                    matchwith = checkForMatch(selected, mainApp.blocks.getItems())
                    position = calculateGrid(matchwith, 25, 22, 20)
                    position = (position[0] + 2, position[1] + 2)

                # Get atlas
                if actualOpt == "Items":
                    atlas = mainApp.itemsAtlas
                elif actualOpt == "Blocks":
                    atlas = mainApp.blocksAtlas

                # Copy region and export
                export = atlas.atlas.copy(position[0], position[1], position[0] + 16, position[1] + 16)          
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
        self.buttonChange.configure(state="disabled")
        threading.Thread(target=changeTexture).start()

    def changeTextureFunc(self, value):
        mainApp = self.master.master
        mainFrame = self.master
        outputDir = mainApp.outputFolder

        actualOpt = mainApp.searchData[3]
        items = mainApp.items.getItems()
        blocks = mainApp.blocks.getItems()
        itemsAtlas = mainApp.itemsAtlas
        blocksAtlas = mainApp.blocksAtlas
        addedItems = mainApp.addedItems
        addedBlocks = mainApp.addedBlocks

        # Load indexes
        if actualOpt == "Items":
            added = addedItems
        elif actualOpt == "Blocks":
            added = addedBlocks

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
                    textureToReplace = Image.open(filePath)
                    itemsAtlas.addElement(position, textureToReplace)
                    duplicated = checkForMatch(items[matchwith], added.getItems())

                    if not os.path.exists(f"{outputDir}/textures/items"):
                        os.makedirs(f"{outputDir}/textures/items")

                    newTexture = Texture3dst().new(textureToReplace.size[0], textureToReplace.size[1], 1)
                    newTexture.paste(textureToReplace, 0, 0)
                    newTexture.flipX()
                    newTexture.convertData()
                    newTexture.export(f"{outputDir}/textures/items/{items[matchwith]}.3dst")

                    if duplicated == -1:
                        added.addItem(items[matchwith])
                elif actualOpt == "Blocks":
                    blocksAtlas.addElement(position, Image.open(filePath))
                    duplicated = checkForMatch(blocks[matchwith], added.getItems())

                    if not os.path.exists(f"{outputDir}/textures/blocks"):
                        os.makedirs(f"{outputDir}/textures/blocks")

                    newTexture = Texture3dst().new(textureToReplace.size[0], textureToReplace.size[1], 1)
                    newTexture.paste(textureToReplace, 0, 0)
                    newTexture.flipX()
                    newTexture.convertData()

                    newTexture.export(f"{outputDir}/textures/blocks/{blocks[matchwith]}.3dst")
                    if duplicated == -1:
                        added.addItem(blocks[matchwith])
                mainFrame.listElementCall(value)
                mainApp.saved = False
        self.buttonChange.configure(state="normal")

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
        if self.infoDispFrame.buttonChange.cget("state") == "disabled":
            self.infoDispFrame.buttonChange.configure(state="normal")
        if self.infoDispFrame.buttonExport.cget("state") == "disabled":
            self.infoDispFrame.buttonExport.configure(state="normal")
        self.infoDispFrame.selected.set(value)

        selected = value
        actualOpt = self.master.searchData[3]
        mainApp = self.master

        # Calculate positions
        if actualOpt == "Items":
            matchwith = checkForMatch(selected, mainApp.items.getItems())
            position = calculateGrid(matchwith, 32, 13, 16)
        elif actualOpt == "Blocks":
            matchwith = checkForMatch(selected, mainApp.blocks.getItems())
            position = calculateGrid(matchwith, 25, 22, 20)
            position = (position[0] + 2, position[1] + 2)

        # Load atlas
        if actualOpt == "Items":
            atlas = mainApp.itemsAtlas
        elif actualOpt == "Blocks":
            atlas = mainApp.blocksAtlas

        # Copy region and update display
        if matchwith != -1:
            print(selected)
            portview = atlas.atlas.copy(position[0], position[1], position[0] + 16, position[1] + 16)
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
        self.saved = True
        self.atlas = []

        # --------------------------------------------

        if getattr(sys, 'frozen', False):
            self.running = "exe"
            self.app_path = sys._MEIPASS
            self.runningDir = os.path.dirname(sys.executable)
        elif __file__:
            self.running = "src"
            self.app_path = os.path.dirname(__file__)
            self.runningDir = os.path.dirname(__file__)
        
        # Ini file
        if os.path.exists(os.path.join(self.runningDir, "mc3ds-tm.ini")):
            self.config = configparser.ConfigParser()
            self.config.read(os.path.join(self.runningDir, "mc3ds-tm.ini"))
        else:
            self.config = configparser.ConfigParser()
            self.config["Preferences"] = {"theme": "dark"}
            self.config["Path"] = {"lastdir": os.path.join(self.runningDir, "MC3DS")}
        self.outputFolder = self.config["Path"]["lastdir"]
        self.theme = self.config["Preferences"]["theme"]
        if not self.theme in ["dark", "light"]:
            self.theme = "dark"
            self.config["Preferences"]["theme"] = "dark"
        customtkinter.set_appearance_mode(self.theme)
        self.saveChangesForIniFile()

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
        fileMenu.add_option("Toggle theme", command=self.changeTheme)
        fileMenu.add_separator()
        fileMenu.add_option("Save", command=self.saveChanges)
        fileMenu.add_separator()
        fileMenu.add_option("Exit", command=self.closeApp)

        toolsMenu = CTkMenuBar.CustomDropdownMenu(widget=menu_bar.add_cascade("Tools"))
        toolsMenu.add_option("Auto Import", command=self.openAutoImport)
        toolsMenu.add_option("Update Application", command=self.updateApp)

        helpMenu = CTkMenuBar.CustomDropdownMenu(widget=menu_bar.add_cascade("Help"))
        helpMenu.add_option("About", command=self.about_popup)

        # --------------------------------------------

        # Main frame
        self.mainFrame = MainFrame(self, fg_color="transparent")
        self.mainFrame.pack(side='left', expand=True, fill='both')

        # --------------------------------------------

        # Initial loading
        if self.theme == "dark":
            self.mainFrame.elementsFrame.text_color = "white"
        else:
            self.mainFrame.elementsFrame.text_color = "black"

        # Load indexes of blocks and items from source
        self.items = IndexFile().open(os.path.join(self.app_path, f"{self.sourceFolder}/indexes/newItemsIndex.txt"))
        self.blocks = IndexFile().open(os.path.join(self.app_path, f"{self.sourceFolder}/indexes/newBlocksIndex.txt"))

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
        with open(os.path.join(self.runningDir, "mc3ds-tm.ini"), "w") as configfile:
            self.config.write(configfile)

    def openFolder(self):
        if self.askForChanges():
            input = customtkinter.filedialog.askdirectory()
            if self.outputFolder != input and input != '':
                self.outputFolder = input
                self.config["Path"]["lastdir"] = self.outputFolder
                self.saveChangesForIniFile()
                self.loadResources()
                self.saved = True
                self.updateList = True

    def changeTheme(self):
        if self.theme == "dark":
            customtkinter.set_appearance_mode("light")
            self.mainFrame.elementsFrame.text_color = "black"
            self.updateList = True
            self.theme = "light"
        else:
            customtkinter.set_appearance_mode("dark")
            self.mainFrame.elementsFrame.text_color = "white"
            self.updateList = True
            self.theme = "dark"
        self.config["Preferences"]["theme"] = self.theme
        self.saveChangesForIniFile()

    def about_popup(self):
        about_text = "MC3DS Texture Maker\nVersion 2.0\n\nAuthor: STBrian\nE-mail: brichap100@gmail.com"
        messagebox.showinfo("About", about_text)

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
                mainFrame = self.mainFrame
                searchData = self.searchData
                actualOpt = searchData[3]
                items = self.items
                blocks = self.blocks
                addedItems = self.addedItems
                addedBlocks = self.addedBlocks

                # mainFrame.elementsFrame.delete("all")
                end = len(mainFrame.elementsFrame.buttons)
                for i in range(end):
                    end -= 1
                    mainFrame.elementsFrame.buttons[end].grid_remove()
                    mainFrame.elementsFrame.buttons[end].destroy()
                mainFrame.elementsFrame.buttons = {}
                mainFrame.elementsFrame.end_num = 0

                if actualOpt == "Items":
                    elements = items
                    added = addedItems
                elif actualOpt == "Blocks":
                    elements = blocks
                    added = addedBlocks

                elements = elements.getItems()

                if (not searchData[0] == ""):
                    elements = difflib.get_close_matches(searchData[0], elements, n = len(elements), cutoff=0.4)
                
                if searchData[1] == "off":
                    elements = deleteMatches(elements, added.getItems())

                if searchData[2] == "off":
                    elements = checkForMatches(elements, added.getItems())

                for i in range(0, len(elements)):
                    mainFrame.elementsFrame.insert(i, elements[i])
                    if self.updateList == True:
                        break
            time.sleep(0.5)

    def loadResources(self):
        # Load atlas either from source folder or output if exists
        if os.path.exists(os.path.normpath(f"{self.outputFolder}/atlas/atlas.items.meta_79954554_0.3dst")):
            self.itemsAtlas = atlasTexture3dst().open(os.path.normpath(f"{self.outputFolder}/atlas/atlas.items.meta_79954554_0.3dst"), "Items")
        else:
            self.itemsAtlas = atlasTexture3dst().open(os.path.join((self.app_path), f"{self.sourceFolder}/atlas/atlas.items.vanilla.png"), "Items")
        if os.path.exists(os.path.normpath(f"{self.outputFolder}/atlas/atlas.terrain.meta_79954554_0.3dst")):
            self.blocksAtlas = atlasTexture3dst().open(os.path.normpath(f"{self.outputFolder}/atlas/atlas.terrain.meta_79954554_0.3dst"), "Blocks")
        else:
            self.blocksAtlas = atlasTexture3dst().open(os.path.join((self.app_path), f"{self.sourceFolder}/atlas/atlas.terrain.vanilla.png"), "Blocks")

        # Load index of added blocks and items if exists
        if os.path.exists(os.path.normpath(f"{self.outputFolder}/items.txt")):
            self.addedItems = IndexFile().open(os.path.normpath(f"{self.outputFolder}/items.txt"))
        else:
            self.addedItems = IndexFile().new()
        if os.path.exists(os.path.normpath(f"{self.outputFolder}/blocks.txt")):
            self.addedBlocks = IndexFile().open(os.path.normpath(f"{self.outputFolder}/blocks.txt"))
        else:
            self.addedBlocks = IndexFile().new()
        return
    
    def saveChanges(self):
        out = os.path.join(self.outputFolder, "atlas")
        if not os.path.exists(out):
            os.makedirs(out)
        self.itemsAtlas.save(os.path.normpath(f"{self.outputFolder}/atlas/atlas.items.meta_79954554_0.3dst"))
        self.blocksAtlas.save(os.path.normpath(f"{self.outputFolder}/atlas/atlas.terrain.meta_79954554_0.3dst"))
        self.addedItems.save(os.path.normpath(f"{self.outputFolder}/items.txt"))
        self.addedBlocks.save(os.path.normpath(f"{self.outputFolder}/blocks.txt"))
        self.saved = True

    def openAutoImport(self):
        autoImport = AutoImport(self)

    def closeApp(self, val=None):
        if self.saved:
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
    
    def updateApp(self):
        if '.exe' in os.path.basename(__file__) and os.path.exists('.\\updater.exe'):
            os.system(f'start .\\updater.exe')
        else:
            error = messagebox.showerror("Error", "The Updater Executable isn't in the Current Install Directory.\nCannot Update, Download the latest Release manually.")
        

    def askForChanges(self):
        if self.saved:
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

if __name__ == "__main__":
    customtkinter.set_default_color_theme("blue")

    print("Loading app...")
    app = App()

    app.bind('<Alt-F4>', app.closeApp)
    app.protocol("WM_DELETE_WINDOW", app.closeApp)

    app.mainloop()
