import os
import sys
import json
from types import MethodType
import difflib
import configparser
import customtkinter, CTkMenuBar

from tkinter import ttk
from PIL import Image, ImageTk
from functools import partial
from pathlib import Path
from tkinter import messagebox

from modules import *
from modules.MyCTkTopLevel import *
from modules.uvsExtractor import exportUVs
from appGlobalVars import appGlobalVars

from infoDisplay import InfoDisplayFrame
from searchOptions import SearchOptionsFrame
from autoImport import AutoImport

VERSION = "3.0-dev"

def clearTreeview(tree: ttk.Treeview):
    for item in tree.get_children():
        tree.delete(item)

def parseConfigFile(fp: str):
    config = configparser.ConfigParser()
    if Path(fp).exists():
        config.read(fp)

    if not "Project" in config:
        config["Project"] = {}
    if not "lastdir" in config["Project"]:
        config["Project"]["lastdir"] = ""

    if not "Preferences" in config:
        config["Preferences"] = {}
    if not "theme" in config["Preferences"]:
        config["Preferences"]["theme"] = "dark"    
    if not "showpreviewbg" in config["Preferences"]:
        config["Preferences"]["showpreviewbg"] = "true"
    if not "allowresize" in config["Preferences"]:
        config["Preferences"]["allowresize"] = "true"

    if not Path(config["Project"]["lastdir"]).exists():
        config["Project"]["lastdir"] = ""

    if not config["Preferences"]["theme"] in ("dark", "light"):
        config["Preferences"]["theme"] = "dark"

    if not config["Preferences"]["showpreviewbg"] in ("true", "false"):
        config["Preferences"]["showpreviewbg"] = "true"

    if not config["Preferences"]["allowresize"] in ("true", "false"):
        config["Preferences"]["allowresize"] = "true"
    return config

def createNewConfigFile(fp: str | Path, values: dict):
    configFile = configparser.ConfigParser()
    for section in values.keys():
        configFile[section] = {}
        for field in values[section].keys():
            configFile[section][field] = values[section][field]
    with open(fp, "w") as file:
        configFile.write(file)

class MainFrame(customtkinter.CTkFrame):
    def __init__(self, master, globalVars: appGlobalVars, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_columnconfigure(0, weight=5)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.globalVars = globalVars

        self.searchOptionsFrame = SearchOptionsFrame(self, globalVars)
        self.searchOptionsFrame.grid(row=0, column=0, padx=5, pady=5, sticky="wen", columnspan=2)

        elementsFrame = customtkinter.CTkFrame(self)
        elementsFrame.grid_columnconfigure(0, weight=1)
        elementsFrame.grid_rowconfigure(0, weight=1)
        elementsFrame.grid(row=1, column=0, padx=5, pady=(0, 5), sticky="wens")

        elementsFrame2 = customtkinter.CTkFrame(elementsFrame)
        elementsFrame2.grid_columnconfigure(0, weight=1)
        elementsFrame2.grid_rowconfigure(0, weight=1)
        elementsFrame2.grid(row=0, column=0, sticky="wens")

        self.elementsTreeView = ttk.Treeview(elementsFrame2, show="tree", selectmode="browse")
        self.elementsTreeView.bind('<<TreeviewSelect>>', self.showItemInfoCallback)
        self.elementsTreeView.grid(row=0, column=0, padx=(5, 0), pady=5, sticky="wens")
        self.elementsTreeView.icons = []
        self.scrollbar = customtkinter.CTkScrollbar(elementsFrame2, command=self.elementsTreeView.yview)
        self.elementsTreeView.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.grid(row=0, column=1, padx=0, pady=0, sticky="ns")

        self.infoDispFrame = InfoDisplayFrame(self, globalVars)
        self.infoDispFrame.grid(row=1, column=1, padx=(0, 5), pady=(0, 5), sticky="nswe")

        self.globalVars.updateList = self.updateList

    def showItemInfoCallback(self, *event):
        self.globalVars.treeElementSelected = self.elementsTreeView.item(self.elementsTreeView.selection())
        self.infoDispFrame.showItemInfo()

    def updateList(self):
        searchData = self.globalVars.searchData
        items = self.globalVars.items
        addedItems: IndexFile = self.globalVars.addedItems

        clearTreeview(self.elementsTreeView)

        elements: dict = items
        added = addedItems

        elements = list(elements.keys())
        elements.sort()

        if (not searchData[0] == ""):
            elements = difflib.get_close_matches(searchData[0], elements, n = len(elements), cutoff=0.4)
        
        if searchData[1] == "off":
            elements = deleteMatches(elements, added.getItems())

        if searchData[2] == "off":
            elements = checkForMatches(elements, added.getItems())

        self.elementsTreeView.icons = []
        for i in range(0, len(elements)):
            self.elementsTreeView.insert("", "end", text="  " + elements[i], values=(i, elements[i]))
        self.updateTreeIcons()

    def updateTreeIcons(self):
        tree = self.elementsTreeView
        tree.icons.clear()
        children = tree.get_children("")
        for child in children:
            item = tree.item(child)
            values = item["values"]

            atlas = self.globalVars.atlasHandler
            element = self.globalVars.items[values[1]]
            position = element["uv"]

            textureExtract = atlas.atlas.copy(position[0], position[1], position[2], position[3])
            if textureExtract.size != (16, 16):
                textureExtract = textureExtract.resize((16, 16), Image.Resampling.LANCZOS)
            iconTk = ImageTk.PhotoImage(textureExtract)
            tree.icons.append(iconTk)
            tree.item(child, image=iconTk)

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.version = VERSION

        # ----------------------------------------------------------------------
        # Variables declaration
        self.globalVars = appGlobalVars(
            [("searchData", list), 
             ("searchDataLoc", list), 
             ("selected", str), 
             ("treeElementSelected", dict), 
             ("elementsList", list), 
             ("saved", bool), 
             ("atlas", list), 
             ("running", str), 
             ("appPath", Path), 
             ("assetsPath", Path), 
             ("iconPath", Path), 
             ("runningDir", Path),
             ("outputFolder", str), 
             ("atlasPath", str), 
             ("uvsPath", str), 
             ("showPreviewBg", bool), 
             ("allowResize", bool),
             ("items", dict),
             ("uvs", dict),
             ("atlasHandler", atlasTexture3dst),
             ("addedItems", IndexFile),
             ("updateList", MethodType)
            ])
        self.globalVars.searchData = ["", "off", "on", "Items"]
        self.globalVars.selected = ""
        self.globalVars.elementsList = []
        self.globalVars.saved = True
        self.globalVars.atlas = []
        self.globalVars.treeElementSelected = {}
        self.globalVars.items = {}
        
        self.newProjectWindow = None
        self.settingsWindow = None

        # ----------------------------------------------------------------------

        if getattr(sys, 'frozen', False):
            self.globalVars.running = "exe"
            self.globalVars.appPath = Path(sys._MEIPASS)
            self.globalVars.assetsPath = Path(sys._MEIPASS).joinpath("assets")
            self.globalVars.iconPath = Path(sys._MEIPASS)
            self.globalVars.runningDir = Path(os.path.dirname(sys.executable))
        elif __file__:
            self.globalVars.running = "src"
            self.globalVars.appPath = Path(os.path.dirname(__file__))
            self.globalVars.assetsPath = Path(os.path.dirname(__file__)).parent.joinpath("assets")
            self.globalVars.iconPath = Path(os.path.dirname(__file__)).parent
            self.globalVars.runningDir = Path(os.path.dirname(__file__))
        
        # ----------------------------------------------------------------------
        # Ini file
        print("Parsing config file")
        self.config = parseConfigFile(self.globalVars.runningDir.joinpath("mc3ds-tm.ini"))
        # ----------------------------------------------------------------------

        self.theme = self.config["Preferences"]["theme"]
        self.globalVars.outputFolder = self.config["Project"]["lastdir"]
        self.globalVars.showPreviewBg = self.config["Preferences"]["showpreviewbg"] == "true"
        self.globalVars.allowResize = self.config["Preferences"]["allowresize"] == "true"

        self.saveChangesForIniFile()
        self.changeTheme()

        self.title("MC3DS Texture Maker")
        os_name = os.name
        if os_name == "nt":
            self.iconbitmap(default=self.globalVars.iconPath.joinpath("icon.ico"))
        elif os_name == "posix":
            iconpath = ImageTk.PhotoImage(file=self.globalVars.iconPath.joinpath("icon.png"))
            self.wm_iconbitmap()
            self.iconphoto(False, iconpath)

        self.geometry("580x420")
        self.minsize(580, 420)
        self.resizable(True, True)

        # --------------------------------------------

        # Menu bar
        menu_bar = CTkMenuBar.CTkMenuBar(master=self, height=15)

        fileMenu = CTkMenuBar.CustomDropdownMenu(widget=menu_bar.add_cascade("File"))
        fileMenu.add_option("New project", command=self.newProject)
        fileMenu.add_option("Open project", command=self.askOpenProject)
        fileMenu.add_separator()
        fileMenu.add_option("Save", command=self.saveChanges)
        fileMenu.add_separator()
        fileMenu.add_option("Settings", command=self.openSettings)
        fileMenu.add_separator()
        fileMenu.add_option("Exit", command=self.closeApp)

        toolsMenu = CTkMenuBar.CustomDropdownMenu(widget=menu_bar.add_cascade("Tools"))
        toolsMenu.add_option("Auto Import", command=self.openAutoImport)

        helpMenu = CTkMenuBar.CustomDropdownMenu(widget=menu_bar.add_cascade("Help"))
        helpMenu.add_option("About", command=self.about_popup)

        # --------------------------------------------

        # Main frame
        self.mainFrame = MainFrame(self, self.globalVars, fg_color="transparent")
        self.mainFrame.pack(side='left', expand=True, fill='both')

        # --------------------------------------------

        if self.globalVars.outputFolder != "":
            if not Path(self.globalVars.outputFolder).joinpath("project.conf").exists():
                messagebox.showwarning("Missing project", "Last project cannot be opened. Missing path")
                self.globalVars.outputFolder = ""
                self.config["Project"]["lastdir"] = ""
                self.saveChangesForIniFile()
            else:
                self.openProject(self.globalVars.outputFolder)

    def saveChangesForIniFile(self):
        with open(self.globalVars.runningDir.joinpath("mc3ds-tm.ini"), "w") as configfile:
            self.config.write(configfile)

    def newProject(self):
        if self.newProjectWindow is None or not self.newProjectWindow.winfo_exists():
            newProjectWindow = MyCTkTopLevel(self)
            newProjectWindow.title("Create new project")
            newProjectWindow.resizable(False, False)

            windowLabel = customtkinter.CTkLabel(newProjectWindow, text="New project", font=(None, 14, "bold"))
            windowLabel.grid(column=0, row=0, padx=10, pady=(10, 0), sticky="ws")

            projNameLabel = customtkinter.CTkLabel(newProjectWindow, text="Project name", font=(None, 12))
            projNameLabel.grid(column=0, row=1, padx=10, pady=0, sticky="ws")

            nameValue = customtkinter.StringVar(value="")
            projNameEntry = customtkinter.CTkEntry(newProjectWindow, textvariable=nameValue)
            projNameEntry.grid(column=0, row=2, padx=10, pady=(0, 10), sticky="w")

            atlasPathLabel = customtkinter.CTkLabel(newProjectWindow, text="Atlas file", font=(None, 12))
            atlasPathLabel.grid(column=0, row=3, padx=10, pady=0, sticky="ws")

            atlasPathValue = customtkinter.StringVar(value="")
            projAtlasPathEntry = customtkinter.CTkEntry(newProjectWindow, textvariable=atlasPathValue, state="readonly")
            projAtlasPathEntry.grid(column=0, row=4, padx=10, pady=(0, 10), sticky="we", columnspan=2)

            def openAtlasPath():
                atlasPathValue.set(customtkinter.filedialog.askopenfilename(filetypes=[("3DST files", ".3dst")], title="Select atlas file"))
                newProjectWindow.focus()

            selectAtlasPath = customtkinter.CTkButton(newProjectWindow, text="Select", command=openAtlasPath)
            selectAtlasPath.grid(column=2, row=4, padx=10, pady=(0, 10), sticky="e")

            uvsPathLabel = customtkinter.CTkLabel(newProjectWindow, text="UVs file", font=(None, 12))
            uvsPathLabel.grid(column=0, row=6, padx=10, pady=0, sticky="ws")

            uvsPathValue = customtkinter.StringVar(value="")
            projUVsPathEntry = customtkinter.CTkEntry(newProjectWindow, textvariable=uvsPathValue, state="readonly")
            projUVsPathEntry.grid(column=0, row=7, padx=10, pady=(0, 10), sticky="we", columnspan=2)

            def openUVsPath():
                uvsPathValue.set(customtkinter.filedialog.askopenfilename(filetypes=[("UVs files", ".uvs")], title="Select UVs file"))
                newProjectWindow.focus()

            selectUVsPath = customtkinter.CTkButton(newProjectWindow, text="Select", command=openUVsPath)
            selectUVsPath.grid(column=2, row=7, padx=10, pady=(0, 10), sticky="e")

            projectPathLabel = customtkinter.CTkLabel(newProjectWindow, text="Project directory", font=(None, 12))
            projectPathLabel.grid(column=0, row=9, padx=10, pady=0, sticky="ws")

            projectPathValue = customtkinter.StringVar(value="")
            projDirPathEntry = customtkinter.CTkEntry(newProjectWindow, textvariable=projectPathValue, state="readonly")
            projDirPathEntry.grid(column=0, row=10, padx=10, pady=(0, 10), sticky="we", columnspan=2)

            def openProjectPath():
                projectPathValue.set(customtkinter.filedialog.askdirectory(title="Select project directory"))
                newProjectWindow.focus()

            selectProjectPath = customtkinter.CTkButton(newProjectWindow, text="Select", command=openProjectPath)
            selectProjectPath.grid(column=2, row=10, padx=10, pady=(0, 10), sticky="e")

            createProject = partial(self.createProject, 
                                   {
                                        "name": nameValue,
                                        "atlaspath": atlasPathValue,
                                        "uvspath": uvsPathValue,
                                        "projectpath": projectPathValue
                                   })
            
            discard = partial(newProjectWindow.destroy)

            cancelButton = customtkinter.CTkButton(newProjectWindow, text="Cancel", command=discard)
            cancelButton.grid(column=0, row=12, padx=10, pady=15, sticky="e")

            applyButton = customtkinter.CTkButton(newProjectWindow, text="Create", command=createProject)
            applyButton.grid(column=1, row=12, padx=10, sticky="e", pady=10)

            self.newProjectWindow = newProjectWindow
        else:
            self.newProjectWindow.focus()

    def createProject(self, values: dict):
        name: str = values["name"].get()
        atlaspath = values["atlaspath"].get()
        uvspath = values["uvspath"].get()
        projectpath = values["projectpath"].get()
        if name == "" or not name.isalnum():
            messagebox.showerror("Invalid field value", "Enter a valid project name")
            self.newProjectWindow.focus()
            return
        if atlaspath == "":
            messagebox.showerror("Invalid field value", "Enter a valid atlas path")
            self.newProjectWindow.focus()
            return
        if uvspath == "":
            messagebox.showerror("Invalid field value", "Enter a valid uvs path")
            self.newProjectWindow.focus()
            return
        if projectpath == "":
            messagebox.showerror("Invalid field value", "Enter a valid project path")
            self.newProjectWindow.focus()
            return
        atlaspath = Path(atlaspath)
        uvspath = Path(uvspath)
        projectpath = Path(projectpath)

        if projectpath.joinpath(name, "project.conf").exists():
            messagebox.showerror("Existing project", "The directory already has an existing project. Please select another directory or name.")
            self.newProjectWindow.focus()
            return
        
        projectConfigValues = {"Project": {"name": name}}
        if not projectpath.joinpath(name, "atlas").exists():
            projectpath.joinpath(name, "atlas").mkdir(parents=True)
        with open(projectpath.joinpath(name, "atlas", atlaspath.name), "wb") as fout:
            with open(atlaspath, "rb") as fin:
                fout.write(fin.read())
        projectConfigValues["Project"]["atlaspath"] = str(Path("atlas").joinpath(atlaspath.name))

        if not projectpath.joinpath(name, "uvs").exists():
            projectpath.joinpath(name, "uvs").mkdir(parents=True)
        exportUVs(uvspath, projectpath.joinpath(name, "uvs", f"{uvspath.name}.json"))
        projectConfigValues["Project"]["uvspath"] = str(Path("uvs").joinpath(f"{uvspath.name}.json"))

        createNewConfigFile(projectpath.joinpath(name, "project.conf"), projectConfigValues)
        self.newProjectWindow.destroy()
        self.openProject(projectpath.joinpath(name))

    def askOpenProject(self):
        if self.askForChanges():
            dirpath = customtkinter.filedialog.askdirectory()
            if self.globalVars.outputFolder != dirpath and dirpath != "":
                self.openProject(dirpath)

    def openProject(self, dirpath: str | Path):
        if isinstance(dirpath, str):
            dirpath = Path(dirpath)
        if not Path(dirpath).joinpath("project.conf").exists():
            messagebox.showerror("Invalid project folder", "No project config found in directory")
        else:
            config = configparser.ConfigParser()
            config.read(Path(dirpath).joinpath("project.conf"))

            if not "Project" in config:
                messagebox.showerror("Invalid project config file", "Project config file is invalid! Missing 'Project' section")
                return
            if not "name" in config["Project"]:
                messagebox.showerror("Invalid project config file", "Project config file is invalid! Missing 'name' field")
                return
            if not "atlaspath" in config["Project"]:
                messagebox.showerror("Invalid project config file", "Project config file is invalid! Missing 'atlaspath' field")
                return
            if not "uvspath" in config["Project"]:
                messagebox.showerror("Invalid project config file", "Project config file is invalid! Missing 'uvspath' field")
                return

            self.title(f"MC3DS Texture Maker - {config["Project"]["name"]}")
            self.globalVars.atlasPath = config["Project"]["atlaspath"]
            self.globalVars.uvsPath = config["Project"]["uvspath"]

            self.globalVars.outputFolder = str(dirpath.absolute())
            self.config["Project"]["lastdir"] = self.globalVars.outputFolder
            self.saveChangesForIniFile()
            self.loadResources()
            self.globalVars.saved = True
            self.globalVars.updateList()

    def openSettings(self):
        if self.settingsWindow is None or not self.settingsWindow.winfo_exists():
            settingsWindow = MyCTkTopLevel(self)
            settingsWindow.title("Settings")
            settingsWindow.resizable(False, False)

            appearanceLabel = customtkinter.CTkLabel(settingsWindow, text="Appearance", font=(None, 14, "bold"))
            appearanceLabel.grid(column=0, row=0, padx=10, pady=(10, 0), sticky="ws")

            themeLabel = customtkinter.CTkLabel(settingsWindow, text="Theme", font=(None, 12))
            themeLabel.grid(column=0, row=1, padx=10, pady=0, sticky="ws")

            themeValue = customtkinter.StringVar(value=self.theme)
            appThemeCombobox = customtkinter.CTkComboBox(settingsWindow, values=["dark", "light"], variable=themeValue, state="readonly")
            appThemeCombobox.grid(column=0, row=2, padx=10, pady=(0, 10), sticky="w")

            previewBgValue = customtkinter.BooleanVar(value=self.globalVars.showPreviewBg)
            previewBgCheckbox = customtkinter.CTkCheckBox(settingsWindow, text="Show preview background", variable=previewBgValue, border_width=1, checkbox_width=20, checkbox_height=20)
            previewBgCheckbox.grid(column=0, row=3, padx=10, pady=(0, 2), sticky="w")

            allowResizeValue = customtkinter.BooleanVar(value=self.globalVars.allowResize)
            allowResizeCheckbox = customtkinter.CTkCheckBox(settingsWindow, text="Allow resize textures", variable=allowResizeValue, border_width=1, checkbox_width=20, checkbox_height=20)
            allowResizeCheckbox.grid(column=0, row=4, padx=10, pady=(0, 10), sticky="w")

            applyChanges = partial(self.applySettings, 
                                   {
                                       "theme": themeValue,
                                       "showpreviewbg": previewBgValue,
                                       "allowresize": allowResizeValue
                                   })
            
            discardChanges = partial(settingsWindow.destroy)

            cancelButton = customtkinter.CTkButton(settingsWindow, text="Cancel", command=discardChanges)
            cancelButton.grid(column=0, row=5, padx=10, pady=10, sticky="e")

            applyButton = customtkinter.CTkButton(settingsWindow, text="Apply", command=applyChanges)
            applyButton.grid(column=1, row=5, padx=(0, 10), pady=10)

            self.settingsWindow = settingsWindow
        else:
            self.settingsWindow.focus()

    def applySettings(self, newSettings: dict):
        self.settingsWindow.destroy()
        self.theme = newSettings["theme"].get()
        self.globalVars.showPreviewBg = newSettings["showpreviewbg"].get()
        self.globalVars.allowResize = newSettings["allowresize"].get()

        self.changeTheme()
        self.mainFrame.infoDispFrame.showItemInfo()

        self.config["Preferences"]["theme"] = self.theme
        self.config["Preferences"]["showpreviewbg"] = "true" if self.globalVars.showPreviewBg else "false"
        self.config["Preferences"]["allowresize"] = "true" if self.globalVars.allowResize else "false"
        self.saveChangesForIniFile()

    def changeTheme(self):
        customtkinter.set_appearance_mode(self.theme)
        self.updateTreeviewTheme()

    def about_popup(self):
        about_text = f"MC3DS Texture Maker\nVersion: {self.version}\n\nMade by: STBrian\nGitHub: https://github.com/STBrian"
        messagebox.showinfo("About", about_text)

    def updateListCallback(self):
        self.mainFrame.searchOptionsFrame.saveSearch()

    def loadResources(self):
        self.globalVars.atlasHandler = atlasTexture3dst().open(Path(self.globalVars.outputFolder).joinpath(self.globalVars.atlasPath), "Items")
        # Load indexes of blocks and items from source
        with open(Path(self.globalVars.outputFolder).joinpath(self.globalVars.uvsPath), "r") as f:
            self.globalVars.items = json.load(f)

        # Load index of added items if exists
        if Path(f"{self.globalVars.outputFolder}/added.txt").exists():
            self.globalVars.addedItems = IndexFile().open(os.path.normpath(f"{self.globalVars.outputFolder}/items.txt"))
        else:
            self.globalVars.addedItems = IndexFile().new()
    
    def saveChanges(self):
        if not self.globalVars.saved:
            out = os.path.join(self.globalVars.outputFolder, "atlas")
            if not os.path.exists(out):
                os.makedirs(out)
            self.globalVars.atlasHandler.save(os.path.normpath(f"{self.globalVars.outputFolder}/atlas/atlas.items.meta_79954554_0.3dst"))
            self.globalVars.addedItems.save(os.path.normpath(f"{self.globalVars.outputFolder}/added.txt"))
            self.globalVars.saved = True

    def openAutoImport(self):
        autoImport = AutoImport(self, self.globalVars)

    def closeApp(self, val=None):
        if self.globalVars.saved:
            sys.exit()
        else:
            print("Not saved")
            op = messagebox.askyesnocancel(title="Unsaved changes", message="There are unsaved changes. Would you like to save them before exit?")
            if op == True:
                self.saveChanges()
                sys.exit()
            elif op == False:
                sys.exit()
            else:
                pass

    def askForChanges(self):
        if self.globalVars.saved:
            return True
        else:
            print("Not saved")
            op = messagebox.askyesnocancel(title="Unsaved changes", message="There are unsaved changes. Would you like to save them?")
            if op == True:
                self.saveChanges()
                return True
            elif op == False:
                return True
            else:
                return False
            
    def updateTreeviewTheme(self):
        bg_color = self._apply_appearance_mode(customtkinter.ThemeManager.theme["CTkFrame"]["fg_color"])
        text_color = self._apply_appearance_mode(customtkinter.ThemeManager.theme["CTkLabel"]["text_color"])
        selected_color = self._apply_appearance_mode(customtkinter.ThemeManager.theme["CTkButton"]["fg_color"])

        treestyle = ttk.Style()
        treestyle.theme_use('default')
        treestyle.configure("Treeview", background=bg_color, foreground=text_color, fieldbackground=bg_color, borderwidth=0, font=(None, 10), rowheight=36)
        treestyle.map('Treeview', background=[('selected', selected_color)], foreground=[('selected', text_color)])

if __name__ == "__main__":
    customtkinter.set_default_color_theme("blue")
    
    print("Loading app...")
    app = App()

    app.updateTreeviewTheme()
    app.bind("<<TreeviewSelect>>", lambda event: app.focus_set())

    app.bind('<Alt-F4>', app.closeApp)
    app.protocol("WM_DELETE_WINDOW", app.closeApp)

    app.mainloop()
