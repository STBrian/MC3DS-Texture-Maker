import os
import struct
import json
from pathlib import Path
from typing import BinaryIO

def readString(f: BinaryIO) -> bytes:
    string = b""
    char = f.read(1)
    while char != b'\0':
        string += char
        char = f.read(1)
    return string

def readU16(f: BinaryIO) -> int:
    binary = f.read(2)
    num = int.from_bytes(binary, "little", signed=False)
    return num

def readU32(f: BinaryIO) -> int:
    binary = f.read(4)
    num = int.from_bytes(binary, "little", signed=False)
    return num

def readFloat(f: BinaryIO) -> float:
    num = struct.unpack("<f", f.read(4))[0]
    return num

def exportUVs(fp: str | Path, out_dir: str | Path):
    if isinstance(fp, str):
        fp = Path(fp).absolute()
    if isinstance(out_dir, str):
        out_dir = Path(out_dir).absolute()
    with open(fp, "rb") as f:
        header_1 = readU32(f)
        header_2 = readU32(f)
        header_3 = readU32(f)

        string_ids = []
        for i in range(header_2):
            string_ids.append(readString(f).decode("utf-8"))

        uvs_data = {}
        for i in range(header_2):
            uv_1 = readFloat(f)
            uv_2 = readFloat(f)
            uv_3 = readFloat(f)
            uv_4 = readFloat(f)
            w = readU16(f)
            h = readU16(f)
            unknown1 = readU32(f)
            unknown2 = readU32(f)
            strip = string_ids[i].split("/")[-1]
            uvs_data[strip] = {"uv": [int(uv_1 * w / 1), int(uv_2 * h / 1), int(uv_3 * w / 1), int(uv_4 * h / 1)]}
            uvs_data[strip]["tileSize"] = uvs_data[strip]["uv"][2] - uvs_data[strip]["uv"][0]

        with open(f"{out_dir.joinpath(fp.stem)}.uvs.json", "w") as o:
            json.dump(uvs_data, o, indent=4)

if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    exportUVs("./atlas.items.vanilla.uvs", ".")