import argparse, os, sys, customtkinter
import traceback
import CTkMenuBar
from tkinter import messagebox
from PIL import Image
from pathlib import Path
from py3dst import Texture3dst

VERSION = "0.5.1-dev"

class App(customtkinter.CTk):
    def __init__(self, imgPath: Path|None):
        super().__init__()

        self.version = VERSION

        self.title("3dstViewer")
        self.geometry(f"256x{256+30}")
        self.resizable(False, False)
        self.configure(fg_color="black")

        menu_bar = CTkMenuBar.CTkMenuBar(master=self, height=15)

        fileMenu = CTkMenuBar.CustomDropdownMenu(widget=menu_bar.add_cascade("File"))
        fileMenu.add_option("Open...", command=self.openFile)
        fileMenu.add_separator()
        fileMenu.add_option("Properties", command=self.showInfo)
        fileMenu.add_option("Close texture", command=self.closeFile)
        fileMenu.add_separator()
        fileMenu.add_option("Exit", command=self.closeApp)

        helpMenu = CTkMenuBar.CustomDropdownMenu(widget=menu_bar.add_cascade("Help"))
        helpMenu.add_option("About", command=self.showAbout)

        mainFrame = customtkinter.CTkFrame(self)
        mainFrame.pack(side='top', expand=True, fill='both', pady=0)
        mainFrame.grid_columnconfigure(0, weight=1)
        mainFrame.grid_rowconfigure(0, weight=1)

        portviewFrame = customtkinter.CTkLabel(mainFrame, text="", compound="top", bg_color="black")
        portviewFrame.grid(column=0, row=0, sticky="nswe")
        self.portviewFrame = portviewFrame

        if imgPath != None:
            self.openPath(imgPath.absolute())
        else:
            self.closeFile()
        
    def closeFile(self):
        portviewImg = customtkinter.CTkImage(dark_image=Image.new("RGBA", (16, 16)), size=(16, 16))
        self.imgWidth = 0
        self.imgHeight = 0
        self.imgName = ""
        self.imgPath = ""
        self.imgOpen = False
        self.portviewFrame.configure(image=portviewImg)
        self.geometry(f"256x{256+30}")

    def showInfo(self):
        if self.imgOpen:
            messagebox.showinfo(title=f"Texture info - {self.imgName}", message=f"Texture path: {self.imgPath}\n\nSize: {self.imgWidth} x {self.imgHeight}")

    def openFile(self):
        filePath = customtkinter.filedialog.askopenfilename(filetypes=[("3DST Texture", ".3dst")])
        self.openPath(filePath)

    def openPath(self, filePath):
        if filePath != '':
            if os.path.exists(filePath):
                path = Path(filePath)
                try:
                    texture = Texture3dst().open(path)
                    preview = texture.copy(0, 0, texture.width, texture.height)
                    preview = preview.convert("RGBA")

                    minwidth = 256
                    minheight = 256
                    if preview.size[0] < minwidth:
                        width = minwidth
                    else:
                        width = preview.size[0]
                    if preview.size[1] < minheight:
                        height = minheight
                    else:
                        height = preview.size[1]
                    self.geometry(f"{width}x{height+30}")

                    self.title(f"{path.name} - 3dstViewer")
                    portviewImg = customtkinter.CTkImage(light_image=preview, dark_image=preview, size=(preview.size[0], preview.size[1]))
                    self.portviewFrame.configure(image=portviewImg)
                    self.imgWidth = preview.size[0]
                    self.imgHeight = preview.size[1]
                    self.imgName = path.name
                    self.imgPath = path.absolute()
                    self.imgOpen = True
                except Exception:
                    messagebox.showerror(title="Error - 3dstViewer", message=f"Error while opening file.\n{traceback.format_exc()}")

    def showAbout(self):
        about_text = f"3DST Viewer\nVersion {self.version}\n\nMade by: STBrian\nGitHub: https://github.com/STBrian"
        messagebox.showinfo("About", about_text)

    def closeApp(self):
        sys.exit()

if __name__ == "__main__":
    if len(sys.argv) < 1:
        messagebox.showerror(title="Error", message="No args provided")
        sys.exit()

    parser = argparse.ArgumentParser(description='A 3dst texture file viewer')
    parser.add_argument('path', nargs="?" ,type=str, help="The path of the file")
    args = parser.parse_args()

    if args.path != None:
        if os.path.exists(args.path):
            path = Path(args.path)
            try:
                texture = Texture3dst().open(path)
            except Exception:
                messagebox.showerror(title="Error - 3dstViewer", message=f"Error while opening file.\n{traceback.format_exc()}")
                sys.exit()
            texture = None

            customtkinter.set_appearance_mode("dark")
            app = App(path)
            app.mainloop()
    else:
        customtkinter.set_appearance_mode("dark")
        app = App(None)
        app.mainloop()