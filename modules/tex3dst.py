from PIL import Image

class Texture3dstException(Exception):
    def __init__(self, message):
        super().__init__(message)

def setPixelRGBAfromList(data: list, x: int, y: int, width: int, height: int, red: int, green: int, blue: int, alpha: int):
        if type(data) != list:
            raise Texture3dstException("data expected to be a list.")
        if type(x) != int:
            raise Texture3dstException("x coordinates expected to be an integer.")
        if type(y) != int:
            raise Texture3dstException("y coordinates expected to be an integer.")
        if type(width) != int:
            raise Texture3dstException("width expected to be an integer.")
        if type(height) != int:
            raise Texture3dstException("height expected to be an integer.")
        if x < 0 or x >= width:
            raise Texture3dstException("x coordinates out of range.")
        if y < 0 or y >= height:
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
        listPosition = ((y * width) + x) * 4
        data[listPosition] = red
        data[listPosition + 1] = green
        data[listPosition + 2] = blue
        data[listPosition + 3] = alpha
        return data

def getPixelDataFromList(data: list, x: int, y: int, width: int, height: int):
        if type(data) != list:
            raise Texture3dstException("data expected to be a list.")
        if type(x) != int:
            raise Texture3dstException("x coordinates expected to be an integer.")
        if type(y) != int:
            raise Texture3dstException("y coordinates expected to be an integer.")
        if type(width) != int:
            raise Texture3dstException("width expected to be an integer.")
        if type(height) != int:
            raise Texture3dstException("height expected to be an integer.")
        if x < 0 or x >= width:
            raise Texture3dstException("x coordinates out of range.")
        if y < 0 or y >= height:
            raise Texture3dstException("y coordinates out of range.")
        listPosition = ((y * width) + x) * 4
        r = data[listPosition]
        g = data[listPosition + 1]
        b = data[listPosition + 2]
        a = data[listPosition + 3]
        return [r, g, b, a]

def convertFunction(data: list, width: int, height: int, conversiontype: int):
        if type(data) != list:
            raise Texture3dstException("data expected to be a list.")
        if type(width) != int:
            raise Texture3dstException("width expected to be an integer.")
        if type(height) != int:
            raise Texture3dstException("height expected to be an integer.")
        if type(conversiontype) != int:
            raise Texture3dstException("conversiontype must be and integer.")
        if not (conversiontype >= 1 and conversiontype <= 2):
            raise Texture3dstException("conversiontype must be 1 or 2.")
        
        convertedData = []
        # Si es de tipo 2 significa que va a abrir una textura
        # Y se ocupa tener una lista con todos los espacios necesarios que represente una imagen vacia
        if conversiontype == 2:
            convertedData = [0] * width * height * 4

        x = 0
        y = 0
        z = 0
        # Bucle que itera siguiendo el patron de guardado visto en estas texturas
        for i in range(0, height // 8):
            for j in range(0, width // 8):
                for k in range(0, 2):
                    for l in range(0, 2):
                        for m in range(0, 2):
                            for n in range(0, 2):
                                for o in range(0, 2):
                                    for p in range(0, 2):
                                        if conversiontype == 1:
                                            pixelData = getPixelDataFromList(data, x, y, width, height)
                                            if pixelData[3] == 0:
                                                for q in range(0, 4):
                                                    convertedData.append(0)
                                            else:
                                                # Como es de tipo 1 se tendrán que guardar los valores rgba invertidos
                                                r = pixelData[0]
                                                g = pixelData[1]
                                                b = pixelData[2]
                                                a = pixelData[3]
                                                convertedData.extend([a, b, g, r])
                                        else:
                                            # Como es de tipo 2 los valores rgba están en posiciones invertidas
                                            r = data[z + 3]
                                            g = data[z + 2]
                                            b = data[z + 1]
                                            a = data[z]
                                            convertedData = setPixelRGBAfromList(convertedData, x, y, width, height, r, g, b, a)
                                            z += 4
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

        return convertedData

class Texture3dst:
    def __init__(self):
        return

    def open(self, path: str):
        if type(path) != str:
            raise Texture3dstException("path expected to be a string.")
        
        with open(f"{path}", "rb") as f:
            fileData = list(f.read())
        
        # Empieza el analisis de la cabecera
        if not (fileData[0] == 51 and fileData[1] == 68 and fileData[2] == 83 and fileData[3] == 84):
            raise Texture3dstException("The texture does not contain the type mark.")
        if not (fileData[4] == 3):
            raise Texture3dstException("Texture mode not supported.")
        
        # Verifica que no haya bytes no esperados
        for i in range(0, 7):
            if not (fileData[5 + i] == 0):
                raise Texture3dstException(f"Unexpected byte at {hex(5 + i)} position.")
        
        # Verifica que las dimensiones de la textura textura no sean mayor a las soportadas
        if not (fileData[14] == 0 and fileData[15] == 0):
            raise Texture3dstException("Texture width greater than supported.")
        if not (fileData[18] == 0 and fileData[19] == 0):
            raise Texture3dstException("Texture height greater than supported.")

        # Verifica que las dimensiones no sean 0
        if fileData[12] == 0 and fileData[13] == 0:
            raise Texture3dstException("The texture width cannot be 0.")
        if fileData[16] == 0 and fileData[17] == 0:
            raise Texture3dstException("The texture height cannot be 0.")
        
        # Verifica que las dimensiones y el checksum sean las mismas
        if not (fileData[12] == fileData[20] and fileData[13] == fileData[21]):
            raise Texture3dstException("The texture width must be the same as width checksum.")
        if not (fileData[16] == fileData[24] and fileData[17] == fileData[25]):
            raise Texture3dstException("The texture height must be the same as height checksum.")
        
        localwidth = int.from_bytes(bytearray([fileData[12], fileData[13]]), "little")
        localheight = int.from_bytes(bytearray([fileData[16], fileData[17]]), "little")

        if localwidth % 8 != 0 and localheight % 8 != 0:
            raise Texture3dstException("Unsupported texture resolution.")
        
        # Verifica que el nivel de mip este dentro de los valores soportados
        if fileData[28] == 0:
            raise Texture3dstException("MaxMipLevel cannot be equal to 0.")
        if fileData[29] != 0 and fileData[30] != 0 and fileData[31] != 0:
            raise Texture3dstException("MaxMipLevel greater than supported.")
        
        localmiplevel = fileData[28]

        if not ((localwidth / (2 ** (localmiplevel - 1)) >= 8) and (localheight / (2 ** (localmiplevel - 1)) >= 8)):
            raise Texture3dstException("MaxMipLevel not supported.")

        self.texturemode = 3
        self.width = localwidth
        self.height = localheight
        self.maxmiplevel = localmiplevel

        localdata = fileData[32:len(fileData)]

        # Se utiliza el segundo método de conversion para cargar la textura
        self.data = convertFunction(localdata, localwidth, localheight, 2)

        return self

    def new(self, width: int, height: int, maxmiplevel: int):
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
        self.data = [0] * height * width * 4
        self.convertedData = []
        self.mipoutput = []
        self.output = []
        return self

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
        flippedTexture = []
        for i in range(0, self.height):
            for j in range(0, self.width):
                for k in range(0, 4):
                    flippedTexture.append(0)

        x = 0
        y = 0
        y_flipped = self.height - 1
        for i in range(0, self.height):
            for j in range(0, self.width):
                pixelData = self.getPixelData(x, y)
                r = pixelData[0]
                g = pixelData[1]
                b = pixelData[2]
                a = pixelData[3]
                flippedTexture = setPixelRGBAfromList(flippedTexture, x, y_flipped, self.width, self.height, r, g, b, a)
                x += 1
            x = 0
            y += 1
            y_flipped -= 1

        self.data = flippedTexture

        return

    def flipY(self):
        return

    def getData(self):
        return self.data
    
    def getOutputData(self):
        return self.output

    def convertData(self):        
        self.convertedData = []
        self.convertedData = convertFunction(self.data, self.width, self.height, 1)

        if self.maxmiplevel > 1:
            mipToExport = []
            self.mipoutput = []
            width = self.width
            height = self.height
            resizedwidth = self.width
            resizedheight = self.height

            # Copia la información de data a una imagen temporal
            tmpImage = Image.new("RGBA", (width, height))
            tmpImagePixels = tmpImage.load()
            x = 0
            y = 0
            for i in range(0, height):
                for j in range(0, width):
                    pixelData = getPixelDataFromList(self.data, x, y, width, height)
                    r = pixelData[0]
                    g = pixelData[1]
                    b = pixelData[2]
                    a = pixelData[3]
                    tmpImagePixels[x, y] = (r, g, b, a)
                    x += 1
                x = 0
                y += 1

            for i in range(0, self.maxmiplevel - 1):
                # Se reescala la imagen
                resizedwidth = resizedwidth // 2
                resizedheight = resizedheight // 2
                wpercent = (resizedwidth/float(width))
                hsize = int((float(height)*float(wpercent)))
                tmpImage = tmpImage.resize((resizedwidth, hsize), Image.Resampling.LANCZOS)

                # Se obtiene los datos de la imagen reescalada
                mipToExport = []
                mipTmpData = []
                x = 0
                y = 0
                for j in range(0, resizedheight):
                    for k in range(0, resizedwidth):
                        pixelData = tmpImage.getpixel((x, y))
                        mipTmpData.extend(pixelData[0], pixelData[1], pixelData[2], pixelData[3])
                        x += 1
                    x = 0
                    y += 1

                # Se convierte los datos usando la funcion
                mipToExport = convertFunction(mipTmpData, resizedwidth, resizedheight, 1)

                # Se copian los datos a la lista de salida
                self.mipoutput.extend(mipToExport)

                # Se reducen las dimensiones en caso de usarse de nuevo
                width = width // 2
                height = height // 2

            mipToExport = []
            mipTmpData = []
            
        return
    
    def export(self, path: str):
        if type(path) != str:
            raise Texture3dstException("path expected to be a string.")

        # Convierte las dimensiones al formato de 16, 256
        width = list(self.width.to_bytes(2, "little"))
        height = list(self.height.to_bytes(2, "little"))

        # Se crea la cabecera
        ## Marca de formato
        self.output = [51, 68, 83, 84]
        self.output.append(self.texturemode)
        self.output.extend([0] * 7)

        ## Se repite dos veces para las dimensiones y el checksum
        for i in range(0, 2):
            self.output.extend(width)
            self.output.extend([0] * 2)
            self.output.extend(height)
            self.output.extend([0] * 2)
        self.output.append(self.maxmiplevel)
        self.output.extend([0] * 3)

        ## Se copia la lista de convertedData a output (Nivel primario)
        self.output.extend(self.convertedData)
        
        ## Se copia la lista mipoutput (Niveles de mip)
        if self.maxmiplevel > 1:
            self.output.extend(self.mipoutput)

        # Se escriben los bytes en un archivo
        with open(f"{path}", "wb") as f:
            f.write(bytearray(self.output))
        return