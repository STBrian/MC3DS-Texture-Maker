def getItemsFromIndexFile(filename):
    items = []
    with open(filename, "r") as f:
        content = f.read()
        items = content.split("\n")
    
    return items

def deleteMatches(list1: list, list2: list):
    matches = []
    for i in range(0, len(list1)):
        if not (list1[i] in list2):
            matches.append(list1[i])

    return matches