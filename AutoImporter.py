import customtkinter, glob, threading, json
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

        self.label2 = customtkinter.CTkLabel(self, text="Rules file:")
        self.label2.grid(row=1, column=1, padx=10, pady=0, sticky="w")

        app_path = master.app_path
        rules = getFilesWithExtensionInDir(os.path.join(app_path, "assets/rules/"), "json")

        self.rule = customtkinter.StringVar(value="default3ds")

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
    
    def autoImport(self):
        root = self.root
        mainApp = root.root
        atlasType = root.optionsFrame.type.get()
        ruleFile = root.optionsFrame.rule.get()
        inputDir = self.dirPath
        outputDir = mainApp.outputFolder
        appPath = root.app_path
        sourceFolder = "assets"
        self.button.configure(state="disabled")
        self.button.configure(text="Please wait...")
        print(atlasType)
        print(inputDir)
        print(outputDir)
        print(appPath)

        # Load index
        if atlasType == "Items":
            path = "items"
        elif atlasType == "Blocks":
            path = "blocks"
        index = getItemsFromIndexFile(os.path.join(appPath, f"assets/indexes/{path}.txt"))

        # Load rules
        modifiedIndex = index[::]
        with open(os.path.join(appPath, f"assets/rules/{ruleFile}.json")) as f:
            ruleData = json.loads(f.read())
        if atlasType in ruleData:
            for element in ruleData[atlasType]:
                if element["name"] in modifiedIndex:
                    modifiedIndex[modifiedIndex.index(element["name"])] = element["value"]

        # Load the atlas to modify
        if atlasType == "Items":
            if os.path.exists(os.path.join(outputDir, "atlas/atlas.items.meta_79954554_0.3dst")):
                atlas = atlasTexture3dst().open(os.path.join(outputDir, "atlas/atlas.items.meta_79954554_0.3dst"), "Items")
            else:
                atlas = atlasTexture3dst().open(os.path.join(appPath, sourceFolder, "atlas/atlas.items.vanilla.png"), "Items")
        elif atlasType == "Blocks":
            if os.path.exists(os.path.join(outputDir, "atlas/atlas.terrain.meta_79954554_0.3dst")):
                atlas = atlasTexture3dst().open(os.path.join(outputDir, "atlas/atlas.terrain.meta_79954554_0.3dst"), "Blocks")
            else:
                atlas = atlasTexture3dst().open(os.path.join(appPath, sourceFolder, "atlas/atlas.terrain.vanilla.png"), "Blocks")

        for file in glob.iglob(os.path.join(inputDir, "**/*.png"), recursive=True):
            filepath = Path(file)
            value = filepath.stem

            if value in modifiedIndex:
                print(f"--------------- {value} ---------------")
                # Calculate position
                matchwith = checkForMatch(value, modifiedIndex)
                if atlasType == "Items":
                    position = calculateGrid(matchwith, 32, 13, 16)
                elif atlasType == "Blocks":
                    position = calculateGrid(matchwith, 25, 22, 20)

                if isImage16x16(file):
                    # Show new texture in preview frame
                    portviewImage = Image.open(file)
                    portviewRes = portviewImage.resize((256, 256), Image.Resampling.NEAREST)
                    root.previewFrame.portview.configure(dark_image=portviewRes)

                    # Replace texture
                    print("Opening new texture and replacing...")
                    atlas.addElement(position, Image.open(file))

                    # Get index of changed items
                    added = []
                    if atlasType == "Items":
                        if os.path.exists(os.path.join(outputDir, "items.txt")):
                            added = getItemsFromIndexFile(os.path.join(outputDir, "items.txt"))
                    elif atlasType == "Blocks":
                        if os.path.exists(os.path.join(outputDir, "blocks.txt")):
                            added = getItemsFromIndexFile(os.path.join(outputDir, "blocks.txt"))

                    # Check for duplicated
                    duplicated = checkForMatch(index[matchwith], added)
                    if duplicated == -1:
                        if atlasType == "Items":
                            path = "items.txt"
                        elif atlasType == "Blocks":
                            path = "blocks.txt"
                        if not os.path.exists(outputDir):
                            os.makedirs(outputDir)
                        addElementToFile(index[matchwith], os.path.join(outputDir, path))

        # Save new atlas
        if atlasType == "Items":
            atlas.save(os.path.join(outputDir, "atlas/atlas.items.meta_79954554_0.3dst"))
        elif atlasType == "Blocks":
            atlas.save(os.path.join(outputDir, "atlas/atlas.terrain.meta_79954554_0.3dst"))

        # Finish reloading sources in main app
        mainApp.reloadAtlas()
        mainApp.updateList = True
        mainApp.mainFrame.listElementCall(mainApp.mainFrame.infoDispFrame.selected.get())

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

class AutoImporter(MyCTkTopLevel):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.geometry("400x240")
        self.resizable(False, False)
        self.title("Auto Importer")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.root = master

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

        self.previewFrame = PreviewFrame(self)
        self.previewFrame.grid(row=0, rowspan=2, column=1, padx=(0, 5), pady=5, sticky="wnes")