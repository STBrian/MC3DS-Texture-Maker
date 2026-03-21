from dataclasses import dataclass, field
from types import MethodType, FunctionType
from typing import Any
from modules import atlasTexture3dst, IndexFile

def dummyFn():
    pass

@dataclass
class GlobalState:
    searchData: list = field(default_factory=list)
    selected: str = ""
    treeElementSelected: dict = field(default_factory=dict)
    elementList: list = field(default_factory=list)
    openedProject: bool = False
    saved: bool = True
    atlas: list = field(default_factory=list)
    atlasPath: str = ""
    uvsPath: str = ""
    atlasType: str = ""
    tilePadding: int = 0
    outputFolder: str = ""
    showPreviewBg: bool = True
    allowResize: bool = True
    resamplingType: str = ""
    items: dict = field(default_factory=dict)
    uvs: dict = field(default_factory=dict)
    atlasHandler: atlasTexture3dst = field(default_factory=atlasTexture3dst)
    addedItems: IndexFile = field(default_factory=IndexFile)
    updateList: MethodType | FunctionType = dummyFn

    def __setattr__(self, name: str, value: Any) -> None:
        expected_type = self.__class__.__annotations__.get(name)
        if expected_type and not isinstance(value, expected_type):
            raise TypeError(f"{name} must be {expected_type}")
        super().__setattr__(name, value)


GLOBAL_STATE = GlobalState()