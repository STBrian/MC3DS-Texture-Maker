import customtkinter
from appGlobalVars import appGlobalVars

class SearchOptionsFrame(customtkinter.CTkFrame):
    def __init__(self, master, globalVars: appGlobalVars, **kwargs):
        super().__init__(master, **kwargs)

        self.globalVars = globalVars

        # Variables
        self.searchText = customtkinter.StringVar(value="")
        self.showModifiedVar = customtkinter.StringVar(value="off")
        self.showUnmodifiedVar = customtkinter.StringVar(value="on")
        self.globalVars.searchData = ["", "off", "on"]

        self.grid_columnconfigure(0, weight=1)

        self.searchOptionsLabel = customtkinter.CTkLabel(self, text="Search options:")
        self.searchOptionsLabel.grid(row=0, column=0, padx=5, sticky="wn")

        self.showUnmodifiedSwitch = customtkinter.CTkSwitch(self, text="Show unmodified elements", onvalue="on", offvalue="off", variable=self.showUnmodifiedVar)
        self.showUnmodifiedSwitch.grid(row=1, column=0, padx=5, pady=0, sticky="wn")

        self.showModifiedSwitch = customtkinter.CTkSwitch(self, text="Show modified elements", onvalue="on", offvalue="off", variable=self.showModifiedVar)
        self.showModifiedSwitch.grid(row=2, column=0, padx=5, pady=5, sticky="wn")

        self.entryText = customtkinter.CTkEntry(self, textvariable=self.searchText, placeholder_text="Search")
        self.entryText.grid(row=3, column=0, padx=(5, 0), pady=5, sticky="wen")

        self.button = customtkinter.CTkButton(self, text="Search", width=80, command=self.saveSearch)
        self.button.grid(row=3, column=1, padx=5, pady=5, sticky="wn")
        
    def saveSearch(self):
        if self.globalVars.openedProject:
            searchText = self.searchText.get()
            modifiedVar = self.showModifiedVar.get()
            unmodifiedVar = self.showUnmodifiedVar.get()

            if self.globalVars.searchData != [searchText, modifiedVar, unmodifiedVar]:
                self.globalVars.searchData = [searchText, modifiedVar, unmodifiedVar]
                self.globalVars.updateList()