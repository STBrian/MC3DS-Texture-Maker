import os
import sys
import customtkinter

class WorkingFolderFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.outputFolder = "MC3DS"

        self.label = customtkinter.CTkLabel(self, text="Output folder:")
        self.label.grid(row=0, column=0, padx=5, pady=0, sticky="wne")

        self.label2 = customtkinter.CTkLabel(self, text=self.outputFolder, justify="left", fg_color="#343638")
        self.label2.grid(row=1, column=0, padx=5, pady=5, sticky="wne")

        self.modifyButton = customtkinter.CTkButton(self, text="Modify", command=self.clickedModify)
        self.modifyButton.grid(row=2, column=0, padx=5, pady=5, sticky="wne")

        self.statusModify = False

    def clickedModify(self):
        if self.statusModify == False:
            self.label2.destroy()

            self.textEntry = customtkinter.CTkEntry(self, placeholder_text=self.outputFolder)
            self.textEntry.grid(row=1, column=0, padx=5, pady=5, sticky="wne")

            self.modifyButton.configure(text="Save")

            self.statusModify = True
        elif self.statusModify == True:
            self.textEntry.destroy()

            self.label2 = customtkinter.CTkLabel(self, text=self.outputFolder)
            self.label2.grid(row=1, column=0, padx=5, pady=5, sticky="wn")

            self.modifyButton.configure(text="Modify")

            self.statusModify = False

class ShowMenuFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.label = customtkinter.CTkLabel(self, text="Show:")
        self.label.grid(row=0, column=0, padx=5, pady=0, sticky="wn")
        self.itemsButton = customtkinter.CTkButton(self, text="Items", command=self.changeToItems)
        self.itemsButton.grid(row=1, column=0, padx=5, pady=(5, 0))
        self.blocksButton = customtkinter.CTkButton(self, text="Blocks", command=self.changeToBlocks)
        self.blocksButton.grid(row=2, column=0, padx=5, pady=5)

    def changeToItems(self):
        print("To items")

    def changeToBlocks(self):
        print("To blocks")

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
        self.iconbitmap(default=os.path.join(self.app_path, "icon.ico"))
        self.geometry("400x300")
        self.resizable(False, True)

        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure((0, 1), weight=0)

        self.workingFolderFrame = WorkingFolderFrame(self)
        self.workingFolderFrame.grid(row=0, column=0, padx=5, pady=(5, 0), sticky="wn")

        self.showMenuFrame = ShowMenuFrame(self)
        self.showMenuFrame.grid(row=1, column=0, padx=5, pady=5, sticky="wn")

        self.button = customtkinter.CTkButton(self, text="my button", command=self.button_callback)
        self.button.grid(row=2, column=0, padx=10, pady= 10, sticky="ew", columnspan=2)

    def button_callback(self):
        print("Hi")

customtkinter.set_default_color_theme("blue")
app = App()
app.mainloop()

