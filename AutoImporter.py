import customtkinter, glob
from PIL import ImageTk
from pathlib import Path

from modules import *
from modules.MyCTkTopLevel import *

def getFilesWithExtensionInDir(path: str, ext: str):
    matches = []
    for file in glob.iglob(os.path.join(os.path.abspath(f"{path}"), f"**/*.{ext}"), recursive=True):
        filepath = Path(file)
        matches.append(filepath.stem)
    return matches

class InputDirFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_columnconfigure(0, weight=1)

        self.root = master 

class OptionsFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.title = customtkinter.CTkLabel(self, text="Options:", font=("default", 13, "bold"))
        self.title.grid(row=0, column=0, padx=10, pady=0, sticky="w")

        self.label = customtkinter.CTkLabel(self, text="Atlas type:")
        self.label.grid(row=1, column=0, padx=10, pady=0, sticky="w")

        self.type = customtkinter.StringVar(value="Items")

        self.cb = customtkinter.CTkComboBox(self, values=["Items", "Blocks"], variable=self.type)
        self.cb.grid(row=2, column=0, padx=10, pady=(5, 10), sticky="w")

        self.label2 = customtkinter.CTkLabel(self, text="Rule file:")
        self.label2.grid(row=1, column=1, padx=10, pady=0, sticky="w")

        app_path = master.app_path
        rules = getFilesWithExtensionInDir(os.path.join(app_path, "assets/rules/"), "json")

        self.rule = customtkinter.StringVar(value="default")

        self.cb2 = customtkinter.CTkComboBox(self, values=rules, variable=self.rule)
        self.cb2.grid(row=2, column=1, padx=10, pady=(5, 10), sticky="w")

class StartFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.root = master

        self.grid_columnconfigure(0, weight=1)

        self.label = customtkinter.CTkLabel(self, text="Folder selected:")
        self.label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        self.type = customtkinter.StringVar(value="Items")

        self.button2 = customtkinter.CTkButton(self, text="Select textures folder", command=self.selectFolder)
        self.button2.grid(row=1, column=0, padx=10, pady=0, sticky="we")

        self.button = customtkinter.CTkButton(self, text="Start")
        self.button.grid(row=2, column=0, padx=10, pady=5, sticky="we")
        
        self.dirPath = ""

    def selectFolder(self):
        self.dirPath = customtkinter.filedialog.askdirectory()
        dirPath = Path(self.dirPath)
        self.label.configure(text=f"Folder selected: {dirPath.stem}")
        self.focus()

class AutoImporter(MyCTkTopLevel):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.geometry("400x240")
        self.resizable(False, False)
        self.title("Auto Importer")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.app_path = master.app_path
        os_name = os.name
        if os_name == "nt":
            iconpath = ImageTk.PhotoImage(file=os.path.join(self.app_path, "icon2.png"))
            self.wm_iconbitmap()
            self.iconphoto(False, iconpath)
        elif os_name == "posix":
            iconpath = ImageTk.PhotoImage(file=os.path.join(self.app_path, "icon2.png"))
            self.wm_iconbitmap()
            self.iconphoto(False, iconpath)

        self.output_dir = master.outputFolder
        self.inputDir = customtkinter.StringVar(value="")

        self.optionsFrame = OptionsFrame(self)
        self.optionsFrame.grid(row=0, column=0, padx=5, pady=5, sticky="we")

        self.startFrame = StartFrame(self)
        self.startFrame.grid(row=1, column=0, padx=5, pady=(0, 5), sticky="wens")