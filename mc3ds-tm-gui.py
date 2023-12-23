import os
import sys
import customtkinter

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        if getattr(sys, 'frozen', False):
            self.running = "exe"
            self.app_path = sys._MEIPASS
        elif __file__:
            self.running = "src"
            self.app_path = os.path.dirname(__file__)

        self.title("MC3DS Texture Maker")
        if os.name == "nt":
            self.iconbitmap(default=os.path.join(self.app_path, "icon.ico"))
        self.geometry("500x350")
        self.resizable(True, True)

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Secondary Frame
        self.secFrame = customtkinter.CTkFrame(self)
        self.secFrame.grid(row=0, column=0, padx=5, pady=5, sticky="nsw")
        self.secFrame.grid_rowconfigure((0, 1), weight=0)
        self.secFrame.grid_rowconfigure(2, weight=1)

        ## Working Folder Frame
        self.workingFolderFrame = customtkinter.CTkFrame(self.secFrame)
        self.workingFolderFrame.grid(row=0, column=0, padx=5, pady=(5, 0), sticky="wen")

        self.outputFolder = "MC3DS"

        self.workLabel = customtkinter.CTkLabel(self.workingFolderFrame, text="Output folder:")
        self.workLabel.grid(row=0, column=0, padx=5, pady=0, sticky="wne")

        self.noEditableLabel = customtkinter.CTkLabel(self.workingFolderFrame, text=self.outputFolder, fg_color="#343638")
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

        self.showMenuComboBox = customtkinter.CTkComboBox(self.showMenuFrame, values=["Items", "Blocks"], command=self.comboBox_callback)
        self.showMenuComboBox.grid(row=1, column=0, padx=5, pady=5)

        ## Extra Buttons Frame
        self.extraButtonsFrame = customtkinter.CTkFrame(self.secFrame)
        self.extraButtonsFrame.grid(row=2, column=0, padx=5, pady=5, sticky="sw")

        self.button1 = customtkinter.CTkButton(self.extraButtonsFrame, text="Save")
        self.button1.grid(row=0, column=0, padx=5, pady=5, sticky="wen")

        # Main Frame
        self.mainFrame = customtkinter.CTkFrame(self)
        self.mainFrame.grid(row=0, column=1, padx=(0, 5), pady=5, sticky="wens")
        self.mainFrame.grid_columnconfigure(0, weight=1)

        ## Search Options Frame
        self.searchOptionsFrame = customtkinter.CTkFrame(self.mainFrame)
        self.searchOptionsFrame.grid(row=0, column=0, padx=5, pady=5, sticky="wen")
        self.searchOptionsFrame.grid_columnconfigure(0, weight=1)

        self.searchText = "None"

        self.searchOptionsLabel = customtkinter.CTkLabel(self.searchOptionsFrame, text="Search options:")
        self.searchOptionsLabel.grid(row=0, column=0, padx=5, sticky="wn")

        self.byTextVar = customtkinter.StringVar(value="off")
        self.byTextSwitch = customtkinter.CTkSwitch(self.searchOptionsFrame, text="Search by text", onvalue="on", offvalue="off", variable=self.byTextVar, command=self.switchChange)
        self.byTextSwitch.grid(row=1, column=0, padx=5, pady=5, sticky="wn")

        self.showModifiedVar = customtkinter.StringVar(value="off")
        self.showModifiedSwitch = customtkinter.CTkSwitch(self.searchOptionsFrame, text="Show modified elements", onvalue="on", offvalue="off", variable=self.showModifiedVar)
        self.showModifiedSwitch.grid(row=2, column=0, padx=5, pady=5, sticky="wn")

    def clickedModify(self):
        if self.statusModify == False:
            self.noEditableLabel.destroy()

            self.textFolderEntry = customtkinter.CTkEntry(self.workingFolderFrame, placeholder_text=self.outputFolder)
            self.textFolderEntry.grid(row=1, column=0, padx=5, pady=5, sticky="wne")

            self.modifyTextVar.set("Save")

            self.statusModify = True
            
        elif self.statusModify == True:
            if not self.textFolderEntry.get() == "":
                self.outputFolder = self.textFolderEntry.get()
            self.textFolderEntry.destroy()

            self.noEditableLabel = customtkinter.CTkLabel(self.workingFolderFrame, text=self.outputFolder, justify="left", fg_color="#343638")
            self.noEditableLabel.grid(row=1, column=0, padx=5, pady=5, sticky="wne")

            self.modifyTextVar.set("Modify")

            self.statusModify = False

    def comboBox_callback(self, opt):
        print(opt)

    def switchChange(self):
        if self.byTextSwitch.get() == "on":
            self.entryTextFrame = customtkinter.CTkFrame(self.searchOptionsFrame)
            self.entryTextFrame.grid(row=3, column=0, padx=5, pady=5, sticky="wen")
            self.entryTextFrame.grid_columnconfigure(0, weight=1)

            self.entryText = customtkinter.CTkEntry(self.entryTextFrame, placeholder_text=self.searchText)
            self.entryText.grid(row=0, column=0, padx=5, pady=5, sticky="wen")

            self.button = customtkinter.CTkButton(self.entryTextFrame, text="Search", width=80, command=self.saveSearch)
            self.button.grid(row=0, column=1, padx=(0, 5), pady=5, sticky="wn")

        elif self.byTextSwitch.get() == "off":
            self.entryTextFrame.destroy()

    def saveSearch(self):
        if not self.entryText.get() == "":
            self.searchText = self.entryText.get()

customtkinter.set_default_color_theme("blue")
customtkinter.set_appearance_mode("dark")
app = App()
app.mainloop()
