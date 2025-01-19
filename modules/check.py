from PIL import Image

def deleteMatches(list1: list, list2: list):
    matches = []
    for i in range(0, len(list1)):
        if not (list1[i] in list2):
            matches.append(list1[i])

    return matches

def checkForMatch(value, list1: list):
    position = -1
    for i in range(0, len(list1)):
        if value == list1[i]:
            position = i

    return position

def checkForMatches(list1: list, list2: list):
    matches = []
    for i in range(0, len(list1)):
        if list1[i] in list2:
            matches.append(list1[i])

    return matches

def canOpenImage(texture_path) -> bool:
    try:
        img = Image.open(texture_path)
        return True
    except:
        return False

def isImage16x16(texture_path):
    img = Image.open(texture_path)
    if img.size[0] == 16 and img.size[1] == 16:
        img.close()
        return True
    else:
        img.close()
        return False
    
def isImageSize(image: Image.Image, width: int, height: int):
    if image.size[0] == width and image.size[1] == height:
        return True
    else:
        return False