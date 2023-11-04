class Texture3dstException(Exception):
    def __init__(self, message):
        super().__init__(message)

class Texture3dst:
    def __init__(self, width: int, height: int, maxmiplevel: int):
        if width >= 1:
            self.width = width
        else:
            raise Texture3dstException("Width must be greater than 0.")
        if height >= 1:
            self.height = height
        else:
            raise Texture3dstException("Height must be greater than 0.")
        if maxmiplevel >= 1:
            self.maxmiplevel = maxmiplevel
        else:
            raise Texture3dstException("MaxMipLevel must be greater than 0.")
        self.data = []
        for i in range(0, height):
            for j in range(0, width):
                for k in range(0, 4):
                    self.data.append(0)
        self.output = []
    
    def setPixelRGBA(self, x: int, y: int, red: int, green: int, blue: int, alpha: int):
        if x < 0 or x > self.width:
            raise Texture3dstException("x coordinates out of range.")
        if y < 0 or y > self.height:
            raise Texture3dstException("y coordinates out of range.")
        if red < 0 or red > 255:
            raise Texture3dstException("red value must be between 0 and 255")
        if green < 0 or green > 255:
            raise Texture3dstException("green value must be between 0 and 255")
        if blue < 0 or blue > 255:
            raise Texture3dstException("blue value must be between 0 and 255")
        if alpha < 0 or alpha > 255:
            raise Texture3dstException("alpha value must be between 0 and 255")
        listPosition = ((y * self.height) + x) * 4
        self.data[listPosition] = red
        self.data[listPosition + 1] = green
        self.data[listPosition + 2] = blue
        self.data[listPosition + 3] = alpha

    def getPixelData(self, x: int, y: int):
        listPosition = ((y * self.height) + x) * 4
        r = self.data[listPosition]
        g = self.data[listPosition + 1]
        b = self.data[listPosition + 2]
        a = self.data[listPosition + 3]
        return [r, g, b, a]
    
    def flipX(self):
        dummy = 0

    def flipY(self):
        dummy = 0

    def getData(self):
        return self.data
