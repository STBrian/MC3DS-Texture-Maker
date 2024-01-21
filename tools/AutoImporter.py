import customtkinter
from PIL import ImageTk

from .MyCTkTopLevel import *

class AIInputFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_columnconfigure(0, weight=1)

        self.label = customtkinter.CTkLabel(self, text="Select Minecraft texture folder:")
        self.label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        self.button = customtkinter.CTkButton(self, text="Select folder", width=100)
        self.button.grid(row=1, column=0, padx=10, pady=(5, 10), sticky="w")


class AutoImporter(MyCTkTopLevel):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.geometry("320x420")
        self.resizable(False, False)
        self.title("Auto importer")

        self.grid_columnconfigure(0, weight=1)

        self.inputFrame = AIInputFrame(self)
        self.inputFrame.grid(row=0, column=0, padx=5, pady=5, sticky="we")

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