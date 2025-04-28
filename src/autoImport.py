import customtkinter, glob, threading, json, os
from PIL import ImageTk, Image
from pathlib import Path

from modules import *
from modules.MyCTkTopLevel import *

def getFileNamesWithExtensionInDir(path: Path, ext: str):
    matches = []
    for file in path.glob(f"**/*.{ext}"):
        if file.is_file():
            matches.append(file.stem)
    return matches

class OptionsFrame(customtkinter.CTkFrame):
    def __init__(self, master, globalVars, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.title = customtkinter.CTkLabel(self, text="Options:", font=("default", 13, "bold"))
        self.title.grid(row=0, column=0, padx=10, pady=0, sticky="w")

        self.label2 = customtkinter.CTkLabel(self, text="Version:")
        self.label2.grid(row=1, column=0, padx=10, pady=0, sticky="w")

        rules = getFileNamesWithExtensionInDir(Path(globalVars.assetsPath, "rules"), "json")

        self.rule = customtkinter.StringVar(value="nn3ds 1.9.19")

        self.cb2 = customtkinter.CTkComboBox(self, values=rules, variable=self.rule, state="readonly")
        self.cb2.grid(row=2, column=0, padx=10, pady=(5, 10), sticky="w")

class StartFrame(customtkinter.CTkFrame):
    def __init__(self, master, globalVars, **kwargs):
        super().__init__(master, **kwargs)

        self.root = master
        self.globalVars = globalVars

        self.grid_columnconfigure(0, weight=1)

        self.title = customtkinter.CTkLabel(self, text="Auto Import:", font=("default", 13, "bold"))
        self.title.grid(row=0, column=0, padx=10, pady=0, sticky="w")

        self.label = customtkinter.CTkLabel(self, text="Folder selected:")
        self.label.grid(row=1, column=0, padx=10, pady=0, sticky="w")

        self.cb = customtkinter.CTkButton(self, text="Select textures folder", command=self.selectFolder)
        self.cb.grid(row=2, column=0, padx=10, pady=0, sticky="we")

        self.button = customtkinter.CTkButton(self, text="Start", command=self.startAutoImportCallback, state="disabled")
        self.button.grid(row=3, column=0, padx=10, pady=5, sticky="we")
        
        self.dirPath = ""

    def selectFolder(self):
        dirPathInput = customtkinter.filedialog.askdirectory()
        self.focus()
        if dirPathInput != "":
            self.dirPath = dirPathInput
            dirPath = Path(self.dirPath)
            self.label.configure(text=f"Folder selected: {dirPath.stem}")
            self.button.configure(state="normal")

    def startAutoImportCallback(self):
        autoImportThread = threading.Thread(target=self.autoImport)
        autoImportThread.daemon = True
        autoImportThread.start()

    def loadRulesFile(self, ruleName: str, source: list, out: list, atlasType: str):
        if Path(self.globalVars.assetsPath, f"rules/{ruleName}.json").exists():
            with open(Path(self.globalVars.assetsPath, f"rules/{ruleName}.json"), "r") as f:
                ruleData = json.loads(f.read())

            if "parent" in ruleData:
                self.loadRulesFile(ruleData["parent"], source, out, atlasType)

            if atlasType in ruleData:
                for element in ruleData[atlasType]:
                    if element["name"] in source:
                        out[source.index(element["name"])] = element["value"]
    
    def autoImport(self):
        root = self.root
        atlasType = self.globalVars.atlasType
        ruleFile = root.optionsFrame.rule.get()
        inputDir = self.dirPath
        outputDir = self.globalVars.outputFolder
        allowResize = self.globalVars.allowResize
        appPath = self.globalVars.appPath
        self.button.configure(state="disabled")
        self.button.configure(text="Please wait...")
        print(atlasType)
        print(inputDir)
        print(outputDir)
        print(appPath)

        index: dict = self.globalVars.items
        added: IndexFile = self.globalVars.addedItems
        atlas: atlasTexture3dst = self.globalVars.atlasHandler
        textureDestDir = "textures"

        # Load rules
        atlasType = "Blocks" if atlasType == "Terrain" else atlasType
        sourceIndex = list(index.keys())
        sourceIndex.sort()
        modifiedIndex = sourceIndex[::]
        self.loadRulesFile(ruleFile, sourceIndex, modifiedIndex, atlasType)

        not_found_textures: list = modifiedIndex[::]

        # Get pillow supported image extensions
        supportedExtensions = Image.registered_extensions()
        openSupportedExtensions = [ex for ex, f in supportedExtensions.items() if f in Image.OPEN]
        
        patterns = [os.path.join(inputDir, f"**/*{ext}") for ext in openSupportedExtensions]
        image_files = []
        for pattern in patterns:
            image_files.extend(glob.iglob(pattern, recursive=True))

        for file in image_files:
            filepath = Path(file)
            value = filepath.stem

            if value in modifiedIndex and value in not_found_textures:
                not_found_textures.pop(not_found_textures.index(value))
                print(f"--------------- {value} ---------------")
                # Calculate position
                element = index[sourceIndex[modifiedIndex.index(value)]]
                position = element["uv"]

                if canOpenImage(file):
                    textureToReplace = Image.open(file)
                    isSized = isImageSize(textureToReplace, position[2] - position[0], position[3] - position[1])
                    if not (not isSized and not allowResize):
                        # Replace texture
                        print("Opening new texture and replacing...")
                        
                        if not isSized:
                            resampling = Image.Resampling.LANCZOS
                            if self.globalVars.resamplingType == "Bilinear":
                                resampling = Image.Resampling.BILINEAR
                            elif self.globalVars.resamplingType == "Nearest":
                                resampling = Image.Resampling.NEAREST
                            textureToReplace = textureToReplace.resize((position[2] - position[0], position[3] - position[1]), resampling)
                        # Show new texture in preview frame
                        portviewRes = textureToReplace.resize((256, 256), Image.Resampling.NEAREST)
                        root.previewFrame.portview.configure(dark_image=portviewRes)
                        # Replace
                        atlas.addElement(position, textureToReplace)

                        if not Path(f"{outputDir}/{textureDestDir}").exists():
                            Path(f"{outputDir}/{textureDestDir}").mkdir(parents=True)
                        #newTexture = Texture3dst().fromImage(textureToReplace)
                        #newTexture.export(f"{outputDir}/{textureDestDir}/{sourceIndex[modifiedIndex.index(value)]}.3dst")

                        # Check for duplicated
                        duplicated = checkForMatch(sourceIndex[modifiedIndex.index(value)], added.getItems())
                        if duplicated == -1:
                            added.addItem(sourceIndex[modifiedIndex.index(value)])
                    else:
                        print("Image is not sized. Skipping")
                else:
                    print("Cannot open image. Skipping")

        # Print not found textures
        print("The following textures were not found")
        for item in not_found_textures:
            print(item)
        print("Total textures not found:", len(not_found_textures))

        # Finish reloading lists in main app
        self.globalVars.saved = False
        mainApp = self.root.root
        infoDispFrame = mainApp.mainFrame.infoDispFrame
        infoDispFrame.showItemInfo(infoDispFrame.selected.get())
        self.globalVars.updateList()

        portviewImage = Image.new("RGBA", (16, 16))
        portviewRes = portviewImage.resize((256, 256), Image.Resampling.NEAREST)
        root.previewFrame.portview.configure(dark_image=portviewRes)

        self.button.configure(text="Start")
        self.button.configure(state="normal")

class PreviewFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.portview = customtkinter.CTkImage(dark_image=Image.new("RGBA", (16, 16)), size=(128, 128))

        self.portviewFrameCanvas = customtkinter.CTkCanvas(self, width=128, height=128)
        self.portviewFrameCanvas.grid(row=0, column=0, padx=5, pady=5)

        self.portviewFrameCanvas.grid_rowconfigure(0, weight=1)
        self.portviewFrameCanvas.grid_columnconfigure(0, weight=1)

        self.portviewFrame = customtkinter.CTkLabel(self.portviewFrameCanvas, image=self.portview, text="", compound="top", bg_color="black")
        self.portviewFrame.grid(row=0, column=0, padx=2, pady=2, sticky="wnse")

class AutoImport(MyCTkTopLevel):
    def __init__(self, master, globalVars, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.geometry("400x240")
        self.resizable(False, False)
        self.title("Auto Import")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.globalVars = globalVars

        self.root = master
        self.itemsAtlas = self.globalVars.atlasHandler
        self.items = self.globalVars.items
        self.addedItems = self.globalVars.addedItems

        self.app_path = self.globalVars.appPath
        os_name = os.name
        if os_name == "nt" or os_name == "posix":
            iconpath = ImageTk.PhotoImage(file=(self.globalVars.iconPath.joinpath("icon2.png")))
            self.wm_iconbitmap()
            self.iconphoto(False, iconpath)

        self.output_dir = self.globalVars.outputFolder
        self.inputDir = customtkinter.StringVar(value="")

        self.optionsFrame = OptionsFrame(self, globalVars)
        self.optionsFrame.grid(row=0, column=0, padx=5, pady=5, sticky="we")

        self.startFrame = StartFrame(self, globalVars)
        self.startFrame.grid(row=1, column=0, padx=5, pady=(0, 5), sticky="wens")

        self.previewFrame = PreviewFrame(self)
        self.previewFrame.grid(row=0, rowspan=2, column=1, padx=(0, 5), pady=5, sticky="wnes")