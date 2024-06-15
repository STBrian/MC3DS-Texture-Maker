import argparse, os, sys, customtkinter
import traceback
from tkinter import messagebox
from PIL import Image
from pathlib import Path
from modules.tex3dst import *

class App(customtkinter.CTk):
    def __init__(self, title: str, image: Image.Image):
        super().__init__()

        minwidth = 256
        minheight = 256
        if image.size[0] < minwidth:
            width = minwidth
        else:
            width = image.size[0]

        if image.size[1] < minheight:
            height = minheight
        else:
            height = image.size[1]

        self.title(f"{title} - 3dstViewer")
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.configure(fg_color="black")

        portviewImg = customtkinter.CTkImage(light_image=image, dark_image=image, size=(image.size[0], image.size[1]))
        portviewFrame = customtkinter.CTkLabel(self, image=portviewImg, text="", compound="top", bg_color="black")
        portviewFrame.grid(row=0, column=0, padx=0, pady=0)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        messagebox.showerror(title="Error", message="No file provided")
        sys.exit()

    parser = argparse.ArgumentParser(description='A 3dst texture file viewer')
    parser.add_argument('path', type=str, help="The path of the file")
    args = parser.parse_args()

    if os.path.exists(args.path):
        path = Path(args.path)
        try:
            texture = Texture3dst().open(path)
        except Exception:
            messagebox.showerror(title="Error - 3dstViewer", message=f"Error while opening file.\n{traceback.format_exc()}")
            sys.exit()
        texture.flipX()
        preview = texture.copy(0, 0, texture.width, texture.height)
        preview = preview.convert("RGBA")

        customtkinter.set_appearance_mode("dark")
        app = App(path.name, preview)
        app.mainloop()