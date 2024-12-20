import argparse, os, sys, customtkinter
import traceback
import CTkMenuBar
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw
from pathlib import Path
from py3dst import Texture3dst

VERSION = "0.6.0"

class App(customtkinter.CTk):
    def __init__(self, imgPath: Path|None):
        super().__init__()

        self.version = VERSION

        if getattr(sys, 'frozen', False):
            self.running = "exe"
            self.app_path = sys._MEIPASS
            self.runningDir = os.path.dirname(sys.executable)
        elif __file__:
            self.running = "src"
            self.app_path = os.path.dirname(__file__)
            self.runningDir = os.path.dirname(__file__)

        self.title("3DSTViewer")
        self.geometry(f"{256+250}x{256+30}")
        self.resizable(False, False)
        self.configure(fg_color="black")

        os_name = os.name
        if os_name == "nt":
            self.iconbitmap(default=os.path.join(self.app_path, "icon_viewer.ico"))
        elif os_name == "posix":
            iconpath = ImageTk.PhotoImage(file=os.path.join(self.app_path, "icon_viewer.png"))
            self.wm_iconbitmap()
            self.iconphoto(False, iconpath)

        menu_bar = CTkMenuBar.CTkMenuBar(master=self, height=15)

        fileMenu = CTkMenuBar.CustomDropdownMenu(widget=menu_bar.add_cascade("File"))
        fileMenu.add_option("Open...", command=self.openFile)
        fileMenu.add_separator()
        fileMenu.add_option("Close file", command=self.closeFile)
        fileMenu.add_separator()
        fileMenu.add_option("Exit", command=self.closeApp)

        helpMenu = CTkMenuBar.CustomDropdownMenu(widget=menu_bar.add_cascade("Help"))
        helpMenu.add_option("About", command=self.showAbout)

        mainFrame = customtkinter.CTkFrame(self)
        mainFrame.pack(side='top', expand=True, fill='both', pady=0)
        mainFrame.grid_columnconfigure(0, weight=1)
        mainFrame.grid_columnconfigure(1, weight=0)
        mainFrame.grid_rowconfigure(0, weight=1)

        portviewFrame = customtkinter.CTkLabel(mainFrame, text="", compound="top", bg_color="black")
        portviewFrame.grid(column=0, row=0, sticky="nswe")
        self.portviewFrame = portviewFrame

        infoFrame = customtkinter.CTkFrame(mainFrame, width=200)
        infoFrame.grid(column=1, row=0, sticky="nswe")
        infoFrame.grid_columnconfigure(0, weight=1)

        propertiesLabel = customtkinter.CTkLabel(infoFrame, text="Properties", width=200, font=(None, 13, "bold"))
        propertiesLabel.grid(column=0, row=0, sticky="we", pady=(5,0))

        sizeLabel = customtkinter.CTkLabel(infoFrame, text="Texture size", width=200, font=(None, 12), anchor="w")
        sizeLabel.grid(column=0, row=1, sticky="we", padx=10, pady=(5,0))

        sizeValue = customtkinter.StringVar()
        self.sizeValue = sizeValue
        sizeField = customtkinter.CTkEntry(infoFrame, state="readonly", textvariable=sizeValue)
        sizeField.grid(column=0, row=2, sticky="we", padx=10)

        formatLabel = customtkinter.CTkLabel(infoFrame, text="Pixel format", width=200, font=(None, 12), anchor="w")
        formatLabel.grid(column=0, row=3, sticky="we", padx=10, pady=(10,0))

        formatValue = customtkinter.StringVar()
        self.formatValue = formatValue
        formatField = customtkinter.CTkEntry(infoFrame, state="readonly", textvariable=formatValue)
        formatField.grid(column=0, row=4, sticky="we", padx=10)

        if imgPath != None:
            self.openPath(imgPath.absolute())
        else:
            self.closeFile()
        
    def closeFile(self):
        portviewImg = customtkinter.CTkImage(dark_image=Image.new("RGBA", (16, 16)), size=(16, 16))
        self.imgName = ""
        self.imgPath = ""
        self.imgOpen = False
        self.portviewFrame.configure(image=portviewImg)
        
        self.title("3DSTViewer")
        self.geometry(f"{256+250}x{256+30}")

        self.sizeValue.set("")
        self.formatValue.set("")

    def openFile(self):
        filePath = customtkinter.filedialog.askopenfilename(filetypes=[("3DST Texture", ".3dst")])
        self.openPath(filePath)

    def openPath(self, filePath):
        if filePath != '':
            if os.path.exists(filePath):
                path = Path(filePath)
                try:
                    texture = Texture3dst().open(path)
                    preview = texture.copy(0, 0, texture.size[0], texture.size[1])
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
                    self.geometry(f"{width+250}x{height+30}")

                    chessboard = Image.new("RGBA", (texture.size[0], texture.size[1]), (180, 180, 180, 255))
                    draw = ImageDraw.Draw(chessboard)

                    tilesize = 10
                    for y in range(0, texture.size[1], tilesize):
                        for x in range(0, texture.size[0], tilesize):
                            if (x // tilesize + y // tilesize) % 2 == 0:
                                draw.rectangle(
                                    [(x, y), (x + tilesize - 1, y + tilesize - 1)], 
                                    fill=(128, 128, 128, 255)
                                )
                    
                    previewFinal = Image.alpha_composite(chessboard, preview)

                    self.title(f"{path.name} - 3DSTViewer")
                    portviewImg = customtkinter.CTkImage(light_image=previewFinal, dark_image=previewFinal, size=(preview.size[0], preview.size[1]))
                    self.portviewFrame.configure(image=portviewImg)

                    self.sizeValue.set(f"{preview.size[0]} x {preview.size[1]}")
                    self.formatValue.set(f"{texture._getFormatInfo(texture.header.format)["name"].upper()}")

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