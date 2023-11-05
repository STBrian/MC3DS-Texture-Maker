class Texture3dstException(Exception):
    def __init__(self, message):
        super().__init__(message)

class NewTexture3dst:
    def __init__(self, width: int, height: int, maxmiplevel: int):
        if type(width) != int:
            raise Texture3dstException("Width expected to be an integer.")
        if type(height) != int:
            raise Texture3dstException("Height expected to be an integer.")
        if type(maxmiplevel) != int:
            raise Texture3dstException("MaxMipLevel expected to be an integer.")
        if width <= 0:
            raise Texture3dstException("Width must be greater than 0.")
        if width > 61440:
            raise Texture3dstException("Width cannot be greater than 61440.")
        if height <= 0:
            raise Texture3dstException("Height must be greater than 0.")
        if height > 61440:
            raise Texture3dstException("Height cannot be greater than 61440.")
        if maxmiplevel <= 0:
            raise Texture3dstException("MaxMipLevel must be greater than 0.")
        if not ((width / (2 ** (maxmiplevel - 1)) >= 8) and (height / (2 ** (maxmiplevel - 1)) >= 8)):
            raise Texture3dstException("MaxMipLevel value greater than supported.")
        if width % 8 != 0:
            raise Texture3dstException("Width must be a multiple of 8.")
        if height % 8 != 0:
            raise Texture3dstException("Height must be a multiple of 8.")
        self.width = width
        self.height = height
        self.maxmiplevel = maxmiplevel
        self.texturemode = 3
        self.data = []
        for i in range(0, height):
            for j in range(0, width):
                for k in range(0, 4):
                    self.data.append(0)
        self.convertedData = []
        self.output = []
        return

    def setPixelRGBA(self, x: int, y: int, red: int, green: int, blue: int, alpha: int):
        if type(x) != int:
            raise Texture3dstException("x coordinates expected to be an integer.")
        if type(y) != int:
            raise Texture3dstException("y coordinates expected to be an integer.")
        if x < 0 or x >= self.width:
            raise Texture3dstException("x coordinates out of range.")
        if y < 0 or y >= self.height:
            raise Texture3dstException("y coordinates out of range.")
        if type(red) != int:
            raise Texture3dstException("red value expected to be an integer.")
        if type(green) != int:
            raise Texture3dstException("green value expected to be an integer.")
        if type(blue) != int:
            raise Texture3dstException("blue value expected to be an integer.")
        if type(alpha) != int:
            raise Texture3dstException("alpha value expected to be an integer.")
        if red < 0 or red > 255:
            raise Texture3dstException("red value must be between 0 and 255.")
        if green < 0 or green > 255:
            raise Texture3dstException("green value must be between 0 and 255.")
        if blue < 0 or blue > 255:
            raise Texture3dstException("blue value must be between 0 and 255.")
        if alpha < 0 or alpha > 255:
            raise Texture3dstException("alpha value must be between 0 and 255.")
        listPosition = ((y * self.width) + x) * 4
        self.data[listPosition] = red
        self.data[listPosition + 1] = green
        self.data[listPosition + 2] = blue
        self.data[listPosition + 3] = alpha
        return

    def getPixelData(self, x: int, y: int):
        if type(x) != int:
            raise Texture3dstException("x coordinates expected to be an integer.")
        if type(y) != int:
            raise Texture3dstException("y coordinates expected to be an integer.")
        if x < 0 or x >= self.width:
            raise Texture3dstException("x coordinates out of range.")
        if y < 0 or y >= self.height:
            raise Texture3dstException("y coordinates out of range.")
        listPosition = ((y * self.width) + x) * 4
        r = self.data[listPosition]
        g = self.data[listPosition + 1]
        b = self.data[listPosition + 2]
        a = self.data[listPosition + 3]
        return [r, g, b, a]
    
    def flipX(self):
        return

    def flipY(self):
        return

    def getData(self):
        return self.data
    
    def getOutputData(self):
        return self.output

    def convertData(self):        
        self.convertedData = []
        x = 0
        y = 0
        for i in range(0, self.height // 8):
            for j in range(0, self.width // 8):
                for k in range(0, 2):
                    for l in range(0, 2):
                        for m in range(0, 2):
                            for n in range(0, 2):
                                for o in range(0, 2):
                                    for p in range(0, 2):
                                        pixelData = self.getPixelData(x, y)
                                        if pixelData[3] == 0:
                                            for q in range(0, 4):
                                                self.convertedData.append(0)
                                        else:
                                            self.convertedData.append(pixelData[3])
                                            self.convertedData.append(pixelData[2])
                                            self.convertedData.append(pixelData[1])
                                            self.convertedData.append(pixelData[0])
                                        x += 1
                                    x -= 2
                                    y += 1
                                x += 2
                                y -= 2
                            x -= 4
                            y += 2
                        x += 4
                        y -= 4
                    x -= 8
                    y += 4
                x += 8
                y -= 8
            x = 0
            y += 8

        return
    
    def export(self, directory: str):
        self.output = []

        # Convierte las dimensiones al formato de 16, 256
        width2 = self.width // 256
        height2 = self.height // 256
        width1 = self.width - (width2 * 256)
        height1 = self.height - (height2 * 256)

        # Se crea la cabecera
        ## Marca de formato
        self.output = [51, 68, 83, 84]
        self.output.append(self.texturemode)
        for i in range(0, 7):
            self.output.append(0)

        ## Se repite dos veces para las dimensiones y el checksum
        for i in range(0, 2):
            self.output.append(width1)
            self.output.append(width2)
            for j in range(0, 2):
                self.output.append(0)
            self.output.append(height1)
            self.output.append(height2)
            for j in range(0, 2):
                self.output.append(0)
        self.output.append(self.maxmiplevel)
        for i in range(0, 3):
            self.output.append(0)

        ## Se copia la lista de convertedData a output
        for i in range(0, len(self.convertedData)):
            self.output.append(self.convertedData[i])
        
        fileData = bytearray(self.output)

        with open(f"{directory}", "wb") as f:
            f.write(fileData)

        return