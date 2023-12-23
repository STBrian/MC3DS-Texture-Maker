import os
import sys
import customtkinter

from modules.stbfunctions import *
from modules.tex3dst import *

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # --------------------------------------------

        # Variables declaration
        self.outputFolder = customtkinter.StringVar(value="MC3DS")
        self.actualOpt = customtkinter.StringVar(value="Items")
        self.searchText = customtkinter.StringVar(value="")
        self.sourceFolder = "assets"
        self.byTextVar = customtkinter.StringVar(value="off")
        self.showModifiedVar = customtkinter.StringVar(value="off")

        # --------------------------------------------

        if getattr(sys, 'frozen', False):
            self.running = "exe"
            self.app_path = sys._MEIPASS
        elif __file__:
            self.running = "src"
            self.app_path = os.path.dirname(__file__)

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

        self.noEditableLabel = customtkinter.CTkLabel(self.workingFolderFrame, textvariable=self.outputFolder, fg_color="#343638")
        self.noEditableLabel.grid(row=1, column=0, padx=5, pady=5, sticky="wne")

        self.modifyTextVar = customtkinter.StringVar(value="Modify")
        self.modifyButton = customtkinter.CTkButton(self.workingFolderFrame, textvariable=self.modifyTextVar, command=self.clickedModify)
        self.modifyButton.grid(row=2, column=0, padx=5, pady=5, sticky="wne")

        self.statusModify = False

        ## Show Menu Frame
        self.showMenuFrame = customtkinter.CTkFrame(self.secFrame)
        self.showMenuFrame.grid(row=1, column=0, padx=5, pady=5)

        self.showMenuLabel = customtkinter.CTkLabel(self.showMenuFrame, text="Show:")
        self.showMenuLabel.grid(row=0, column=0, padx=5, pady=0, sticky="wen")

        self.showMenuComboBox = customtkinter.CTkComboBox(self.showMenuFrame, values=["Items", "Blocks"], command=self.comboBox_callback, variable=self.actualOpt)
        self.showMenuComboBox.set("Items")
        self.showMenuComboBox.grid(row=1, column=0, padx=5, pady=5)

        ## Extra Buttons Frame
        self.extraButtonsFrame = customtkinter.CTkFrame(self.secFrame)
        self.extraButtonsFrame.grid(row=2, column=0, padx=5, pady=(0, 5), sticky="sw")

        self.saveButton = customtkinter.CTkButton(self.extraButtonsFrame, text="Save")
        self.saveButton.grid(row=0, column=0, padx=5, pady=5, sticky="wne")

        self.toolsButton = customtkinter.CTkButton(self.extraButtonsFrame, text="Tools")
        self.toolsButton.grid(row=1, column=0, padx=5, pady=(0, 5), sticky="wne")

        self.optionsButton = customtkinter.CTkButton(self.extraButtonsFrame, text="Options")
        self.optionsButton.grid(row=2, column=0, padx=5, pady=(0, 5), sticky="wne")

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

        self.byTextSwitch = customtkinter.CTkSwitch(self.searchOptionsFrame, text="Search by text", onvalue="on", offvalue="off", variable=self.byTextVar, command=self.switchChange)
        self.byTextSwitch.grid(row=1, column=0, padx=5, pady=5, sticky="wn")

        self.showModifiedSwitch = customtkinter.CTkSwitch(self.searchOptionsFrame, text="Show modified elements", onvalue="on", offvalue="off", variable=self.showModifiedVar)
        self.showModifiedSwitch.grid(row=2, column=0, padx=5, pady=5, sticky="wn")

        ## Elements Frame
        self.elementsFrame = customtkinter.CTkScrollableFrame(self.mainFrame)
        self.elementsFrame.grid(row=1, column=0, padx=5, pady=(0, 5), sticky="wens")
        self.elementsFrame.grid_columnconfigure(0, weight=1)

        self.elementsList = []

        ## Info Display Frame
        self.infoDispFrame = customtkinter.CTkFrame(self.mainFrame)
        self.infoDispFrame.grid(row=1, column=1, padx=(0, 5), pady=(0, 5), sticky="nswe")

        self.noSelectedText = customtkinter.CTkLabel(self.infoDispFrame, text="No element selected")
        self.noSelectedText.grid(row=0, column=0, padx=5, pady=0)

        # --------------------------------------------

        # Initial loading
        self.items = getItemsFromIndexFile(f"{self.sourceFolder}/indexes/newitemslist.txt")
        self.blocks = getItemsFromIndexFile(f"{self.sourceFolder}/indexes/newblockslist.txt")

        self.loadAndDisplayList()

    def loadAndDisplayList(self):
        for element in self.elementsList:
            element.destroy()

        elements = []
        added = []
        if self.actualOpt.get() == "Items":
            elements = self.items
            if os.path.exists(os.path.join(self.app_path, self.outputFolder.get(), "items.txt")):
                added = getItemsFromIndexFile(os.path.join(self.app_path, self.outputFolder.get(), "items.txt"))
        elif self.actualOpt.get() == "Blocks":
            elements = self.blocks
            if os.path.exists(os.path.join(self.app_path, self.outputFolder.get(), "blocks.txt")):
                added = getItemsFromIndexFile(os.path.join(self.app_path, self.outputFolder.get(), "items.txt"))

        if self.byTextVar.get() == "on":
            dummy = 0
        
        if self.showModifiedVar.get() == "off":
            elements = deleteMatches(elements, added)

        for i in range(0, len(elements)):
            self.listElement = customtkinter.CTkButton(self.elementsFrame, text=elements[i], fg_color="transparent", anchor="w")
            self.listElement.grid(row=i, column=0, padx=5, pady=(5, 0), sticky="w")
            self.elementsList.append(self.listElement)

    def clickedModify(self):
        if self.statusModify == False:
            self.noEditableLabel.destroy()

            self.textFolderEntry = customtkinter.CTkEntry(self.workingFolderFrame, textvariable=self.outputFolder)
            self.textFolderEntry.grid(row=1, column=0, padx=5, pady=5, sticky="wne")

            self.modifyTextVar.set("Save")

            self.statusModify = True
            
        elif self.statusModify == True:
            if not self.textFolderEntry.get() == "":
                self.outputFolder.set(self.textFolderEntry.get())
            self.textFolderEntry.destroy()

            self.noEditableLabel = customtkinter.CTkLabel(self.workingFolderFrame, textvariable=self.outputFolder, justify="left", fg_color="#343638")
            self.noEditableLabel.grid(row=1, column=0, padx=5, pady=5, sticky="wne")

            self.modifyTextVar.set("Modify")

            self.statusModify = False

    def comboBox_callback(self, opt):
        self.actualOpt.set(opt)
        print(self.actualOpt.get())
        self.loadAndDisplayList()

    def switchChange(self):
        if self.byTextSwitch.get() == "on":
            self.entryTextFrame = customtkinter.CTkFrame(self.searchOptionsFrame)
            self.entryTextFrame.grid(row=3, column=0, padx=5, pady=5, sticky="wen")
            self.entryTextFrame.grid_columnconfigure(0, weight=1)

            self.entryText = customtkinter.CTkEntry(self.entryTextFrame, textvariable=self.searchText)
            self.entryText.grid(row=0, column=0, padx=5, pady=5, sticky="wen")

            self.button = customtkinter.CTkButton(self.entryTextFrame, text="Search", width=80, command=self.saveSearch)
            self.button.grid(row=0, column=1, padx=(0, 5), pady=5, sticky="wn")

        elif self.byTextSwitch.get() == "off":
            self.entryTextFrame.destroy()

    def saveSearch(self):
        if not self.entryText.get() == "":
            self.searchText.set(self.entryText.get())

customtkinter.set_default_color_theme("blue")
customtkinter.set_appearance_mode("dark")
app = App()
app.mainloop()
