import customtkinter, glob, threading, json, os
from PIL import ImageTk, Image
from pathlib import Path

from modules import *
from modules.MyCTkTopLevel import *

def getFilesWithExtensionInDir(path: str, ext: str):
    matches = []
    for file in glob.iglob(os.path.join(os.path.abspath(f"{path}"), f"**/*.{ext}"), recursive=True):
        filepath = Path(file)
        matches.append(filepath.stem)
    return matches

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

        self.cb = customtkinter.CTkComboBox(self, values=["Items", "Blocks"], variable=self.type, state="readonly")
        self.cb.grid(row=2, column=0, padx=10, pady=(5, 10), sticky="w")

        self.label2 = customtkinter.CTkLabel(self, text="Version:")
        self.label2.grid(row=1, column=1, padx=10, pady=0, sticky="w")

        app_path = master.app_path
        rules = getFilesWithExtensionInDir(os.path.join(app_path, "assets/rules/"), "json")

        self.rule = customtkinter.StringVar(value="nn3ds 1.9.19")

        self.cb2 = customtkinter.CTkComboBox(self, values=rules, variable=self.rule, state="readonly")
        self.cb2.grid(row=2, column=1, padx=10, pady=(5, 10), sticky="w")

class StartFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.root = master

        self.grid_columnconfigure(0, weight=1)

        self.title = customtkinter.CTkLabel(self, text="Auto Import:", font=("default", 13, "bold"))
        self.title.grid(row=0, column=0, padx=10, pady=0, sticky="w")

        self.label = customtkinter.CTkLabel(self, text="Folder selected:")
        self.label.grid(row=1, column=0, padx=10, pady=0, sticky="w")

        self.type = customtkinter.StringVar(value="Items")

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
        appPath = self.root.app_path
        if os.path.exists(os.path.join(appPath, f"assets/rules/{ruleName}.json")):
            with open(os.path.join(appPath, f"assets/rules/{ruleName}.json")) as f:
                ruleData = json.loads(f.read())

            if "parent" in ruleData:
                self.loadRulesFile(ruleData["parent"], source, out, atlasType)

            if atlasType in ruleData:
                for element in ruleData[atlasType]:
                    if element["name"] in source:
                        out[source.index(element["name"])] = element["value"]
    
    def autoImport(self):
        root = self.root
        mainApp = root.root
        atlasType = root.optionsFrame.type.get()
        ruleFile = root.optionsFrame.rule.get()
        inputDir = self.dirPath
        outputDir = mainApp.outputFolder
        appPath = root.app_path
        self.button.configure(state="disabled")
        self.button.configure(text="Please wait...")
        print(atlasType)
        print(inputDir)
        print(outputDir)
        print(appPath)

        items: list[str] = root.items.getItems()
        blocks: list[str] = root.blocks.getItems()
        addedItems: IndexFile = root.addedItems
        addedBlocks: IndexFile = root.addedBlocks

        # Get specific data and set variables
        if atlasType == "Items":
            index = items
            added = addedItems
            atlas: atlasTexture3dst = root.itemsAtlas
            textureDestDir = "textures/items"
        elif atlasType == "Blocks":
            index = blocks
            added = addedBlocks
            atlas: atlasTexture3dst = root.blocksAtlas
            textureDestDir = "textures/blocks"

        # Load rules
        modifiedIndex = index[::]
        self.loadRulesFile(ruleFile, index, modifiedIndex, atlasType)

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
                matchwith = checkForMatch(value, modifiedIndex)
                if atlasType == "Items":
                    position = calculateGrid(matchwith, 32, 13, 16)
                elif atlasType == "Blocks":
                    position = calculateGrid(matchwith, 25, 22, 20)

                if canOpenImage(file) and isImage16x16(file):
                    # Show new texture in preview frame
                    portviewImage = Image.open(file)
                    portviewRes = portviewImage.resize((256, 256), Image.Resampling.NEAREST)
                    root.previewFrame.portview.configure(dark_image=portviewRes)

                    # Replace texture
                    print("Opening new texture and replacing...")
                    textureToReplace = Image.open(file)
                    atlas.addElement(position, textureToReplace)

                    if not os.path.exists(f"{outputDir}/{textureDestDir}"):
                        os.makedirs(f"{outputDir}/{textureDestDir}")
                    newTexture = Texture3dst().new(textureToReplace.size[0], textureToReplace.size[1], 1)
                    newTexture.paste(textureToReplace, 0, 0)
                    newTexture.export(f"{outputDir}/{textureDestDir}/{index[matchwith]}.3dst")

                    # Check for duplicated
                    duplicated = checkForMatch(index[matchwith], added.getItems())
                    if duplicated == -1:
                        added.addItem(index[matchwith])

        # Print not found textures
        print("The following textures were not found")
        for item in not_found_textures:
            print(item)
        print("Total textures not found:", len(not_found_textures))

        # Finish reloading lists in main app
        mainApp.updateList = True
        mainApp.saved = False
        mainApp.mainFrame.listElementFun(mainApp.mainFrame.infoDispFrame.selected.get(), mainApp.mainFrame.infoDispFrame.lastActualOption)

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
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.geometry("400x240")
        self.resizable(False, False)
        self.title("Auto Import")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.root = master
        self.itemsAtlas = master.itemsAtlas
        self.blocksAtlas = master.blocksAtlas
        self.items = master.items
        self.blocks = master.blocks
        self.addedItems = master.addedItems
        self.addedBlocks = master.addedBlocks

        self.app_path = master.app_path
        os_name = os.name
        if os_name == "nt" or os_name == "posix":
            iconpath = ImageTk.PhotoImage(file=os.path.join(self.app_path, "icon2.png"))
            self.wm_iconbitmap()
            self.iconphoto(False, iconpath)

        self.output_dir = master.outputFolder
        self.inputDir = customtkinter.StringVar(value="")

        self.optionsFrame = OptionsFrame(self)
        self.optionsFrame.grid(row=0, column=0, padx=5, pady=5, sticky="we")

        self.startFrame = StartFrame(self)
        self.startFrame.grid(row=1, column=0, padx=5, pady=(0, 5), sticky="wens")

        self.previewFrame = PreviewFrame(self)
        self.previewFrame.grid(row=0, rowspan=2, column=1, padx=(0, 5), pady=5, sticky="wnes")