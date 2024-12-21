import argparse, os, sys, customtkinter
import traceback
import CTkMenuBar

from modules.MyCTkTopLevel import *
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw
from pathlib import Path
from py3dst import Texture3dst, Texture3dstUnsupported, Texture3dstNoSignature
from py3dst.tex3dst import _createPixelDataStructure, _getTexturePosition
from py3dst.error_classes import Texture3dstUnexpectedEndOfFile

VERSION = "0.8.1"

def _generateChessboardPattern(width, height, tileSize = 10):
    chessboard = Image.new("RGBA", (width, height), (180, 180, 180, 255))
    draw = ImageDraw.Draw(chessboard)

    for y in range(0, height, tileSize):
        for x in range(0, width, tileSize):
            if (x // tileSize + y // tileSize) % 2 == 0:
                draw.rectangle(
                    [(x, y), (x + tileSize - 1, y + tileSize - 1)], 
                    fill=(128, 128, 128, 255)
                )
    
    return chessboard

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
        fileMenu.add_option("Export as...", command=self.exportAs)
        fileMenu.add_separator()
        fileMenu.add_option("Close file", command=self.closeFile)
        fileMenu.add_separator()
        fileMenu.add_option("Exit", command=self.closeApp)

        viewMenu = CTkMenuBar.CustomDropdownMenu(widget=menu_bar.add_cascade("View"))
        viewMenu.add_option("Show mipmaps", command=self.showMipmaps)

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
        infoFrame.grid_rowconfigure(7, weight=1)

        propertiesLabel = customtkinter.CTkLabel(infoFrame, text="Properties", width=200, font=(None, 13, "bold"))
        propertiesLabel.grid(column=0, row=0, sticky="we", pady=(5,0))

        sizeLabel = customtkinter.CTkLabel(infoFrame, text="Texture size", width=200, font=(None, 12), anchor="w")
        sizeLabel.grid(column=0, row=1, sticky="we", padx=10, pady=(5,0))

        sizeValue = customtkinter.StringVar()
        self.sizeValue = sizeValue
        sizeField = customtkinter.CTkEntry(infoFrame, state="readonly", textvariable=sizeValue)
        sizeField.grid(column=0, row=2, sticky="we", padx=10)

        formatLabel = customtkinter.CTkLabel(infoFrame, text="Pixel format", width=200, font=(None, 12), anchor="w")
        formatLabel.grid(column=0, row=3, sticky="we", padx=10, pady=(5,0))

        formatValue = customtkinter.StringVar()
        self.formatValue = formatValue
        formatField = customtkinter.CTkEntry(infoFrame, state="readonly", textvariable=formatValue)
        formatField.grid(column=0, row=4, sticky="we", padx=10)

        mipLevelLabel = customtkinter.CTkLabel(infoFrame, text="Mipmap levels", width=200, font=(None, 12), anchor="w")
        mipLevelLabel.grid(column=0, row=5, sticky="we", padx=10, pady=(5,0))

        mipLevelValue = customtkinter.StringVar()
        self.mipLevelValue = mipLevelValue
        mipLevelField = customtkinter.CTkEntry(infoFrame, state="readonly", textvariable=mipLevelValue)
        mipLevelField.grid(column=0, row=6, sticky="we", padx=10)

        ignoreAlphaValue = customtkinter.BooleanVar()
        self.ignoreAlphaValue = ignoreAlphaValue
        ignAlphaCheckbox = customtkinter.CTkCheckBox(infoFrame, variable=ignoreAlphaValue, text="Ignore alpha channel", checkbox_width=16, checkbox_height=16, border_width=1, command=self.reload_texture)
        ignAlphaCheckbox.grid(column=0, row=7, pady=(5, 0), padx=10, sticky="ws")

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
        self.mipLevelValue.set("")

    def exportAs(self):
        if self.imgOpen:
            supportedExtensions = Image.registered_extensions()
            saveSupportedExtensions = {ex for ex, f in supportedExtensions.items() if f in Image.SAVE}
            saveSuppExtStr = ""
            for ex in saveSupportedExtensions:
                saveSuppExtStr += f"{ex} "
            filePath = customtkinter.filedialog.asksaveasfilename(filetypes=[("Image files", ".png .jpeg .jpg .webp .bmp"), ("All image files", saveSuppExtStr)])
            if filePath != '':
                texture = Texture3dst().open(self.imgPath)
                imgCopy = texture.copy(0, 0, texture.size[0], texture.size[1])
                try:
                    imgCopy.save(filePath)
                except ValueError:
                    try:
                        imgCopy.save(f"{filePath}.png")
                    except:
                        messagebox.showerror("Error - 3DSTViewer", "An exception occurred while exporting the texture")

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

                    if self.ignoreAlphaValue.get():
                        pixels = preview.load()
                        for y in range(preview.size[1]):
                            for x in range(preview.size[0]):
                                r, g, b, a = pixels[x, y]
                                pixels[x, y] = (r, g, b, 255)

                    # Generates the chessboard pattern in a secondary image then fuses with the source image
                    if not self.ignoreAlphaValue.get():
                        chessboard = _generateChessboardPattern(texture.size[0], texture.size[1])
                        previewFinal = Image.alpha_composite(chessboard, preview)
                    else:
                        previewFinal = preview

                    self.title(f"{path.name} - 3DSTViewer")
                    portviewImg = customtkinter.CTkImage(light_image=previewFinal, dark_image=previewFinal, size=(preview.size[0], preview.size[1]))
                    self.portviewFrame.configure(image=portviewImg)

                    self.sizeValue.set(f"{preview.size[0]} x {preview.size[1]}")
                    self.formatValue.set(f"{texture._getFormatInfo(texture.header.format)["name"].upper()}")
                    self.mipLevelValue.set(f"{texture.header.mip_level}")

                    self.imgName = path.name
                    self.imgPath = path.absolute()
                    self.imgOpen = True
                except Texture3dstUnsupported:
                    messagebox.showerror(title="Error - 3DSTViewer", message=f"Error while opening file.\n{filePath}\n\nUnsupported texture format")
                except Texture3dstNoSignature:
                    messagebox.showerror(title="Error - 3DSTViewer", message=f"Error while opening file.\n{filePath}\n\nInvalid or unsupported 3DST file")
                except:
                    messagebox.showerror(title="Error - 3DSTViewer", message=f"Unhandled error while opening file.\n{traceback.format_exc()}")

    def reload_texture(self):
        if self.imgOpen:
            current_path = self.imgPath
            self.closeFile()
            self.openPath(current_path)

    def showMipmaps(self):
        if self.imgOpen:
            texture = Texture3dst().open(self.imgPath)
            if texture.header.mip_level > 1:
                secondary_window = MyCTkTopLevel(self)
                secondary_window.title("Mipmap viewer")
                secondary_window.geometry(f"{int(texture.header.full_size[0]/2)}x{int(texture.header.full_size[1]/2)}")

                texPixelFormat = texture._getFormatInfo(texture.header.format)
                texPixelLenght = texPixelFormat["pixel_lenght"]
                
                start_idx = 0x20
                mipData_end_idx = start_idx + texPixelLenght * texture.header.full_size[0] * texture.header.full_size[1]
                
                mipmapsFrames = 0
                for i in range(0, texture.header.mip_level - 1):
                    miptexWidth = int(texture.header.full_size[0] / (2 * (i+1)))
                    miptexHeight = int(texture.header.full_size[1] / (2 * (i+1)))
                    mipData_start_idx = mipData_end_idx 
                    mipData_end_idx = mipData_start_idx + (texPixelLenght * miptexWidth * miptexHeight)

                    unarranged_pixelData = _createPixelDataStructure(miptexWidth, miptexHeight, texPixelLenght)
                    with open(self.imgPath, "rb") as f:
                        f.seek(mipData_start_idx)
                        for j in range(miptexHeight):
                            for k in range(miptexWidth):
                                pixelRead = f.read(texPixelLenght)
                                if not pixelRead:
                                    raise Texture3dstUnexpectedEndOfFile
                                unarranged_pixelData[j][k] = pixelRead
                    
                    textureData = _createPixelDataStructure(miptexWidth, miptexHeight, texPixelLenght)
                    for j in range(miptexHeight):
                        for k in range(miptexWidth):
                            dst_pos = _getTexturePosition(k, j, miptexWidth)
                            textureData[j][k] = unarranged_pixelData[dst_pos[1]][dst_pos[0]]

                    textureData.reverse()

                    tmpTexture = Texture3dst().new(miptexWidth, miptexHeight, format=texPixelFormat["name"])
                    for j in range(miptexHeight):
                        for k in range(miptexWidth):
                            pixel_values = tmpTexture._convertBytesToPixelData(textureData[j][k])
                            tmpTexture.setPixel(k, j, pixel_values)

                    preview = _generateChessboardPattern(miptexWidth, miptexHeight)
                    preview = Image.alpha_composite(preview, tmpTexture.copy(0, 0, tmpTexture.size[0], tmpTexture.size[1]))

                    portviewFrame = customtkinter.CTkLabel(secondary_window, width=miptexWidth, height=miptexHeight, text="", compound="top", bg_color="black")
                    portviewFrame.grid(column=i, row=0, sticky="n")
                    
                    portviewImg = customtkinter.CTkImage(light_image=preview, dark_image=preview, size=(miptexWidth, miptexHeight))
                    portviewFrame.configure(image=portviewImg)
                    
                    mipmapsFrames += 1
                
                finalWidth = 0
                finalHeight = int(texture.header.full_size[1] / 2)
                for i in range(mipmapsFrames):
                    finalWidth += texture.header.full_size[0] / (2 * (i+1))

                secondary_window.geometry(f"{int(finalWidth)}x{finalHeight}")
            else:
                messagebox.showinfo("No mipmaps available", "Texture does not contain mipmap data\nMipmap level is 1")

    def showAbout(self):
        about_text = f"3DSTViewer\nVersion {self.version}\n\nMade by: STBrian\nGitHub: https://github.com/STBrian"
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
            except Texture3dstUnsupported:
                messagebox.showerror(title="Error - 3DSTViewer", message=f"Error while opening file.\n{path}\n\nUnsupported texture format")
                sys.exit(1)
            except Texture3dstNoSignature:
                messagebox.showerror(title="Error - 3DSTViewer", message=f"Error while opening file.\n{path}\n\nInvalid or unsupported 3DST file")
                sys.exit(2)
            except:
                messagebox.showerror(title="Error - 3DSTViewer", message=f"Unhandled error while opening file.\n{traceback.format_exc()}")
                sys.exit(3)
            texture = None

            customtkinter.set_appearance_mode("dark")
            app = App(path)
            app.mainloop()
    else:
        customtkinter.set_appearance_mode("dark")
        app = App(None)
        app.mainloop()