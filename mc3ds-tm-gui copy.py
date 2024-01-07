import os
import sys
import difflib
import customtkinter
import threading
import time
from PIL import Image

from modules.stbmodule import *
from modules.tex3dst import *

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # --------------------------------------------

        # Variables declaration
        self.outputFolder = customtkinter.StringVar(value="MC3DS")
        self.lastOutputFolder = "MC3DS"
        self.actualOpt = customtkinter.StringVar(value="Items")
        self.lastSearchText = ""
        self.searchText = customtkinter.StringVar(value="")
        self.sourceFolder = "assets"
        self.showModifiedVar = customtkinter.StringVar(value="off")
        self.lastModifiedVar = "off"
        self.showUnmodifiedVar = customtkinter.StringVar(value="on")
        self.lastUnmodifiedVar = "on"
        self.selected = customtkinter.StringVar(value="")
        self.portview = customtkinter.CTkImage(dark_image=Image.new("RGBA", (16, 16)), size=(128, 128))

        # --------------------------------------------

        if getattr(sys, 'frozen', False):
            self.running = "exe"
            self.app_path = sys._MEIPASS
            self.runningDir = os.path.dirname(sys.executable)
        elif __file__:
            self.running = "src"
            self.app_path = os.path.dirname(__file__)
            self.runningDir = os.path.dirname(__file__)

        self.title("MC3DS Texture Maker")
        if os.name == "nt":
            self.iconbitmap(default=os.path.join(self.app_path, "icon.ico"))
        self.geometry("640x400")
        self.minsize(640, 400)
        self.resizable(True, True)

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --------------------------------------------

        # Secondary Frame
        self.secFrame = customtkinter.CTkFrame(self)
        self.secFrame.grid(row=0, column=0, padx=5, pady=5, sticky="nsw")
        self.secFrame.grid_rowconfigure((0, 1), weight=0)
        self.secFrame.grid_rowconfigure(2, weight=1)

        ## Working Folder Frame
        self.workingFolderFrame = customtkinter.CTkFrame(self.secFrame)
        self.workingFolderFrame.grid(row=0, column=0, padx=5, pady=(5, 0), sticky="wen")

        self.workLabel = customtkinter.CTkLabel(self.workingFolderFrame, text="Output folder:")
        self.workLabel.grid(row=0, column=0, padx=5, pady=0, sticky="wne")

        self.textFolderEntry = customtkinter.CTkEntry(self.workingFolderFrame, textvariable=self.outputFolder)
        self.textFolderEntry.configure(state="disabled")
        self.textFolderEntry.grid(row=1, column=0, padx=5, pady=5, sticky="wne")

        self.modifyTextVar = customtkinter.StringVar(value="Modify")
        self.modifyButton = customtkinter.CTkButton(self.workingFolderFrame, textvariable=self.modifyTextVar, command=self.clickedModify)
        self.modifyButton.grid(row=2, column=0, padx=5, pady=5, sticky="wne")

        self.statusModify = False

        ## Show Menu Frame
        self.showMenuFrame = customtkinter.CTkFrame(self.secFrame)
        self.showMenuFrame.grid(row=1, column=0, padx=5, pady=5)

        self.showMenuLabel = customtkinter.CTkLabel(self.showMenuFrame, text="Show:")
        self.showMenuLabel.grid(row=0, column=0, padx=5, pady=0, sticky="wen")

        self.showMenuComboBox = customtkinter.CTkComboBox(self.showMenuFrame, values=["Items", "Blocks"], command=self.comboBoxShowMenu, variable=self.actualOpt)
        self.showMenuComboBox.set("Items")
        self.showMenuComboBox.grid(row=1, column=0, padx=5, pady=5)

        ## Extra Buttons Frame
        self.extraButtonsFrame = customtkinter.CTkFrame(self.secFrame)
        self.extraButtonsFrame.grid(row=2, column=0, padx=5, pady=(0, 5), sticky="sw")

        self.toolsButton = customtkinter.CTkButton(self.extraButtonsFrame, text="Tools", state="normal", command=self.openTools)
        self.toolsButton.grid(row=0, column=0, padx=5, pady=5, sticky="wne")

        self.optionsButton = customtkinter.CTkButton(self.extraButtonsFrame, text="Options", state="disabled")
        self.optionsButton.grid(row=1, column=0, padx=5, pady=(0, 5), sticky="wne")

        # --------------------------------------------

        # Main Frame
        self.mainFrame = customtkinter.CTkFrame(self)
        self.mainFrame.grid(row=0, column=1, padx=(0, 5), pady=5, sticky="wens")
        self.mainFrame.grid_columnconfigure(0, weight=5)
        self.mainFrame.grid_columnconfigure(1, weight=1)
        self.mainFrame.grid_rowconfigure(1, weight=1)

        ## Search Options Frame
        self.searchOptionsFrame = customtkinter.CTkFrame(self.mainFrame)
        self.searchOptionsFrame.grid(row=0, column=0, padx=5, pady=5, sticky="wen", columnspan=2)
        self.searchOptionsFrame.grid_columnconfigure(0, weight=1)

        self.searchOptionsLabel = customtkinter.CTkLabel(self.searchOptionsFrame, text="Search options:")
        self.searchOptionsLabel.grid(row=0, column=0, padx=5, sticky="wn")

        self.showUnmodifiedSwitch = customtkinter.CTkSwitch(self.searchOptionsFrame, text="Show unmodified elements", onvalue="on", offvalue="off", variable=self.showUnmodifiedVar)
        self.showUnmodifiedSwitch.grid(row=1, column=0, padx=5, pady=0, sticky="wn")

        self.showModifiedSwitch = customtkinter.CTkSwitch(self.searchOptionsFrame, text="Show modified elements", onvalue="on", offvalue="off", variable=self.showModifiedVar)
        self.showModifiedSwitch.grid(row=2, column=0, padx=5, pady=0, sticky="wn")

        self.entryTextFrame = customtkinter.CTkFrame(self.searchOptionsFrame)
        self.entryTextFrame.grid(row=3, column=0, padx=5, pady=5, sticky="wen")
        self.entryTextFrame.grid_columnconfigure(0, weight=1)

        self.entryText = customtkinter.CTkEntry(self.entryTextFrame, textvariable=self.searchText, placeholder_text="Search")
        self.entryText.grid(row=0, column=0, padx=5, pady=5, sticky="wen")

        self.button = customtkinter.CTkButton(self.entryTextFrame, text="Search", width=80, command=self.saveSearch)
        self.button.grid(row=0, column=1, padx=(0, 5), pady=5, sticky="wn")

        ## Elements Frame
        self.elementsFrame = customtkinter.CTkScrollableFrame(self.mainFrame, label_text="Items:")
        self.elementsFrame.grid(row=1, column=0, padx=5, pady=(0, 5), sticky="wens")
        self.elementsFrame.grid_columnconfigure(0, weight=1)

        self.elementsList = []

        ## Info Display Frame
        self.infoDispFrame = customtkinter.CTkFrame(self.mainFrame)
        self.infoDispFrame.grid(row=1, column=1, padx=(0, 5), pady=(0, 5), sticky="nswe")
        self.infoDispFrame.grid_columnconfigure(0, weight=1)
        self.infoDispFrame.grid_rowconfigure(3, weight=1)

        self.noSelectedText = customtkinter.CTkLabel(self.infoDispFrame, text="No element selected")
        self.noSelectedText.grid(row=0, column=0, padx=5, pady=5)

        self.portviewFrame = customtkinter.CTkLabel(self.infoDispFrame, image=self.portview, text="", compound="top")
        self.portviewFrame.grid(row=1, column=0, padx=5, pady=5)

        self.selectionLabel = customtkinter.CTkLabel(self.infoDispFrame, textvariable=self.selected)
        self.selectionLabel.grid(row=2, column=0, padx=5, pady=5)

        self.buttonChange = customtkinter.CTkButton(self.infoDispFrame, text="Change", command=self.threadChangeTexture, state="disabled")
        self.buttonChange.grid(row=3, column=0, padx=5, pady=5, sticky="wes")

        # --------------------------------------------

        # Initial loading
        self.items = getItemsFromIndexFile(os.path.join(self.app_path, f"{self.sourceFolder}/indexes/newitemslist.txt"))
        self.blocks = getItemsFromIndexFile(os.path.join(self.app_path, f"{self.sourceFolder}/indexes/newblockslist.txt"))

        self.updateDisplayList = True
        self.toolsWindow = None

        displayListThread = threading.Thread(target=self.updateDisplayListThread)
        displayListThread.daemon = True
        displayListThread.start()

    def updateDisplayListThread(self):
        while True:
            if self.updateDisplayList == True:
                self.updateDisplayList = False
                
                for element in self.elementsList:
                    element.grid_remove()

                for element in self.elementsList:
                    element.destroy()

                self.elementsList = []
                elements = []
                added = []
                if self.actualOpt.get() == "Items":
                    elements = self.items
                    if os.path.exists(os.path.join(self.runningDir, self.lastOutputFolder, "items.txt")):
                        added = getItemsFromIndexFile(os.path.join(self.runningDir, self.lastOutputFolder, "items.txt"))
                elif self.actualOpt.get() == "Blocks":
                    elements = self.blocks
                    if os.path.exists(os.path.join(self.runningDir, self.lastOutputFolder, "blocks.txt")):
                        added = getItemsFromIndexFile(os.path.join(self.runningDir, self.lastOutputFolder, "blocks.txt"))

                if (not self.lastSearchText == ""):
                    elements = difflib.get_close_matches(self.lastSearchText, elements, cutoff=0.4)
                
                if self.showModifiedVar.get() == "off":
                    elements = deleteMatches(elements, added)

                if self.showUnmodifiedVar.get() == "off":
                    elements = checkForMatches(elements, added)

                for i in range(0, len(elements)):
                    self.listElement = customtkinter.CTkButton(self.elementsFrame, text=elements[i], fg_color="transparent", anchor="w", command=lambda v=elements[i]: self.threadListElement(v))
                    self.listElement.grid(row=i, column=0, padx=5, pady=(5, 0), sticky="w")
                    self.elementsList.append(self.listElement)
                    if self.updateDisplayList == True:
                        break
            time.sleep(0.5)

    def threadChangeTexture(self):
        threading.Thread(target=self.changeTexture).start()
        return

    def changeTexture(self):
        if not self.selected.get() == "":
            value = self.selected.get()
            actualOpt = self.actualOpt.get()
            runningDir = self.runningDir
            lastOutputFolder = self.lastOutputFolder
            items = self.items
            blocks = self.blocks
            app_path = self.app_path
            sourceFolder = self.sourceFolder

            # Load indexes
            added = []
            if actualOpt == "Items":
                if os.path.exists(os.path.join(runningDir, lastOutputFolder, "items.txt")):
                    added = getItemsFromIndexFile(os.path.join(runningDir, lastOutputFolder, "items.txt"))
            elif actualOpt == "Blocks":
                if os.path.exists(os.path.join(runningDir, lastOutputFolder, "blocks.txt")):
                    added = getItemsFromIndexFile(os.path.join(runningDir, lastOutputFolder, "blocks.txt"))

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
                        addToItemAtlas(position, filePath, os.path.join(app_path, sourceFolder), os.path.join(runningDir, lastOutputFolder))
                        duplicated = checkForMatch(items[matchwith], added)
                        if duplicated == -1:
                            addElementToFile(items[matchwith], os.path.join(runningDir, lastOutputFolder, "items.txt"))
                    elif actualOpt == "Blocks":
                        addToBlockAtlas(position, filePath, os.path.join(app_path, sourceFolder), os.path.join(runningDir, lastOutputFolder))
                        duplicated = checkForMatch(blocks[matchwith], added)
                        if duplicated == -1:
                            addElementToFile(blocks[matchwith], os.path.join(runningDir, lastOutputFolder, "blocks.txt"))
                    self.threadListElement(value)  

    def threadListElement(self, value):
        threading.Thread(target=self.listElementClicked, args=(value,)).start()
        return

    def listElementClicked(self, value):
        if self.selected.get() == "":
            self.noSelectedText.destroy()
            self.buttonChange.configure(state="normal")
        self.selected.set(value=value)

        # Calculate positions
        if self.actualOpt.get() == "Items":
            matchwith = checkForMatch(value, self.items)
            position = calculateGrid(matchwith, 32, 13, 16)
        elif self.actualOpt.get() == "Blocks":
            matchwith = checkForMatch(value, self.blocks)
            position = calculateGrid(matchwith, 25, 22, 20)
            position = (position[0] + 2, position[1] + 2)

        # Load atlas image from output folder
        if self.actualOpt.get() == "Items":
            if os.path.exists(os.path.join(self.runningDir, f"{self.lastOutputFolder}/atlas/atlas.items.meta_79954554_0.3dst")):
                self.atlas = Texture3dst().open(os.path.join(self.runningDir, f"{self.lastOutputFolder}/atlas/atlas.items.meta_79954554_0.3dst"))
                self.atlas.flipX()
                loaded = True
            else:
                self.atlas = Texture3dst().new(512, 256, 1)
                loaded = False
        elif self.actualOpt.get() == "Blocks":
            if os.path.exists(os.path.join(self.runningDir, f"{self.lastOutputFolder}/atlas/atlas.terrain.meta_79954554_0.3dst")):
                self.atlas = Texture3dst().open(os.path.join(self.runningDir, f"{self.lastOutputFolder}/atlas/atlas.terrain.meta_79954554_0.3dst"))
                self.atlas.flipX()
                loaded = True
            else:
                self.atlas = Texture3dst().new(512, 512, 3)
                loaded = False

        # Load atlas image from soruce if not output
        if loaded == False:
            if self.actualOpt.get() == "Items":
                atlasImg = Image.open(os.path.join((self.app_path), f"{self.sourceFolder}/atlas/atlas.items.vanilla.png"))
            elif self.actualOpt.get() == "Blocks":
                atlasImg = Image.open(os.path.join((self.app_path), f"{self.sourceFolder}/atlas/atlas.terrain.vanilla.png"))
            atlasImg.convert("RGBA")
            x = 0
            y = 0
            for i in range(0, atlasImg.size[1]):
                for j in range(0, atlasImg.size[0]):
                    r, g, b, a = atlasImg.getpixel((x, y))
                    self.atlas.setPixelRGBA(x, y, r, g, b, a)
                    x += 1
                x = 0
                y += 1
            atlasImg.close()

        portview = Image.new("RGBA", (16, 16))
        for i in range(0, 16):
            for j in range(0, 16):
                pixelrgba = self.atlas.getPixelData(position[0] + j, position[1] + i)
                portview.putpixel((j, i), (pixelrgba[0], pixelrgba[1], pixelrgba[2], pixelrgba[3]))

        portviewRes = portview.resize((256, 256), Image.Resampling.NEAREST)
        self.portview.configure(dark_image=portviewRes)

    def clickedModify(self):
        if self.statusModify == False:
            self.modifyTextVar.set("Save")
            self.textFolderEntry.configure(state="normal")
            self.statusModify = True
            
        elif self.statusModify == True:
            if self.textFolderEntry.get() == "":
                self.outputFolder.set(self.lastOutputFolder)
            if not self.outputFolder.get() == self.lastOutputFolder:
                self.lastOutputFolder = self.outputFolder.get()
                self.updateDisplayList = True
            self.modifyTextVar.set("Modify")
            self.textFolderEntry.configure(state="disabled")
            self.statusModify = False

    def comboBoxShowMenu(self, opt):
        self.actualOpt.set(opt)
        print(self.actualOpt.get())
        if opt == "Items":
            self.elementsFrame.configure(label_text="Items:")
        elif opt == "Blocks":
            self.elementsFrame.configure(label_text="Blocks:")
        self.updateDisplayList = True

    def saveSearch(self):
        if (not self.lastSearchText == self.searchText.get()) or (not self.lastModifiedVar == self.showModifiedVar.get()) or (not self.lastUnmodifiedVar == self.showUnmodifiedVar.get()):
            self.lastSearchText = self.searchText.get()
            self.lastModifiedVar = self.showModifiedVar.get()
            self.lastUnmodifiedVar = self.showUnmodifiedVar.get()
            self.updateDisplayList = True

    def openTools(self):
        if self.toolsWindow is None or not self.toolsWindow.winfo_exists():
            self.toolsWindow = customtkinter.CTkToplevel(self)
            self.toolsWindow.geometry("400x300")
            self.toolsWindow.focus()
        else:
            self.toolsWindow.focus()
        return

customtkinter.set_default_color_theme("blue")
customtkinter.set_appearance_mode("dark")
app = App()
app.mainloop()
