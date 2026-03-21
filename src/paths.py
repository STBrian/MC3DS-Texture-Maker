from pathlib import Path
import sys, os

if getattr(sys, 'frozen', False):
    RUNNING_IN = "exe"
    RESOURCES_PATH = Path(getattr(sys, "_MEIPASS")).joinpath("assets")
    APP_DIR = Path(os.path.dirname(sys.executable))
elif __file__:
    RUNNING_IN = "src"
    RESOURCES_PATH = Path(os.path.dirname(__file__)).parent.joinpath("assets")
    APP_DIR = Path(os.path.dirname(__file__))

class paths:
    @staticmethod
    def getAppPath(fp: str):
        return APP_DIR.joinpath(fp)

    @staticmethod
    def getResource(fp: str):
        return RESOURCES_PATH.joinpath(fp)

    @staticmethod
    def openResource(fp: str, mode: str, encoding: str | None = None):
        return open(paths.getResource(fp), mode, encoding=encoding)
    
    @staticmethod
    def openAppPath(fp: str, mode: str, encoding: str | None = None):
        return open(paths.getAppPath(fp), mode, encoding=encoding)