import os
import struct
import json
from pathlib import Path
from typing import BinaryIO

from pyBjson.string_hash import get_JOAAT_hash

def readString(f: BinaryIO) -> bytes:
    string = b""
    char = f.read(1)
    if len(char) != 1:
        raise Exception("End of file")
    while char != b'\0':
        string += char
        char = f.read(1)
        if len(char) != 1:
            raise Exception("End of file")
    return string

def readU16(f: BinaryIO) -> int:
    binary = f.read(2)
    if len(binary) != 2:
        raise Exception("End of file")
    num = int.from_bytes(binary, "little", signed=False)
    return num

def readU32(f: BinaryIO) -> int:
    binary = f.read(4)
    if len(binary) != 4:
        raise Exception("End of file")
    num = int.from_bytes(binary, "little", signed=False)
    return num

def readFloat(f: BinaryIO) -> float:
    num = struct.unpack("<f", f.read(4))[0]
    return num

def searchHash(elements: list[dict], hashval: int) -> str|None:
    for element in elements:
        if element["hash"] == hashval:
            return element["name"]
    return None

def exportUVs(fp: str | Path, out_path: str | Path, verbose: bool = False):
    if isinstance(fp, str):
        fp = Path(fp).absolute()
    if isinstance(out_path, str):
        out_path = Path(out_path).absolute()
    with open(fp, "rb") as f:
        header_1 = readU32(f) # Total amount of elements not repeated
        header_2 = readU32(f) # Amount of elements including repeated
        header_3 = readU32(f) # Length of all strings
        if verbose:
            print(f"Header 1: {header_1}") 
            print(f"Header 2: {header_2}")
            print(f"Header 3: {header_3}")

        string_ids: list[str] = []
        for i in range(header_2):
            string_ids.append(readString(f).decode("utf-8"))
        f.seek(0x04 * 3 + header_3) # (Header) + (Length) = Start of UVs data

        uvs_data = {}
        hashvals = []
        for i in range(header_2):
            uv_1 = readFloat(f) # u1 [0-1]
            uv_2 = readFloat(f) # v1 [0-1]
            uv_3 = readFloat(f) # u2 [0-1]
            uv_4 = readFloat(f) # v2 [0-1]
            w = readU16(f) # Texture width
            h = readU16(f) # Texture height
            unknown1 = readU32(f) # Idk
            unknown2 = readU32(f) # Could be some kind of binary value ? 
            strip = string_ids[i].split("/")[-1]
            if verbose:
                print(string_ids[i])
                print(f"Unknown 1: {hex(unknown1)}")
                print(format(unknown2, "032b"))
            uvs_data[strip] = {"uv": [int(uv_1 * w), int(uv_2 * h), int(uv_3 * w), int(uv_4 * h)]}
            uvs_data[strip]["tileSize"] = uvs_data[strip]["uv"][2] - uvs_data[strip]["uv"][0]
            if verbose:
                print(uvs_data[strip])
            hashvals.append({"name": strip, "hash": get_JOAAT_hash(strip.lower().encode("utf-8"))})

        matched = 0
        # This last section seems like an index section
        for i in range(header_1):
            unknown3 = readU32(f) # Maybe a hash used to sort data ?
            unknown4 = readU32(f) # Looks like some repetition value ?
            unknown5 = readU32(f) # Looks like an index ?
            if verbose:
                str_id = searchHash(hashvals, unknown3)
                if str_id != None:
                    print(str_id)
                    matched += 1
                print(unknown3, unknown4, unknown5)

        if verbose:
            print(f"Strings that matched: {matched}")
            print(f"Elements in output: {len(uvs_data)}")
            print(f"Header 1: {header_1}") 
            print(f"Header 2: {header_2}")
            print(f"Header 3: {header_3}")
            print(f"Final position: {hex(f.tell())}")

        with open(out_path, "w") as o:
            json.dump(uvs_data, o, indent=4)

if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    exportUVs("./atlas.items.vanilla.uvs", "./atlas.items.vanilla.uvs.json", verbose=True)