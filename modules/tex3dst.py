from PIL import Image

class Texture3dstException(Exception):
    def __init__(self, message):
        super().__init__(message)

def setPixelRGBAfromList(data: list, xy: tuple, size: tuple, rgba: list):
        if type(data) != list:
            raise Texture3dstException("data expected to be a list.")
        if not (type(size) == tuple and all(isinstance(num, int) for num in size) and all(num > 0 for num in size)):
            raise Texture3dstException("Invalid size.")
        if not (type(xy) == tuple and all(isinstance(num, int) for num in xy) and all((xy[i] < 0 or xy[i] >= size[i]) for i in range(len(xy)))):
            raise Texture3dstException("Invalid coordinates.")
        if not (type(rgba) == list and len(rgba) == 4 and all(isinstance(num, int) for num in rgba) and all((num >= 0 and num <= 255) for num in rgba)):
            raise Texture3dstException("Invalid color.")
        x = xy[0]
        y = xy[1]
        width = size[0]
        listPosition = ((y * width) + x) * 4
        data[listPosition:(listPosition + 4)] = rgba
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
        rgba = data[listPosition:(listPosition + 4)]
        return rgba

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
                                            convertedData = setPixelRGBAfromList(convertedData, (x, y), (width, height), [r, g, b, a])
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
        
        # Empieza el analisis de la cabecera-Marca de agua
        if fileData[0:4] != [51, 68, 83, 84]:
            raise Texture3dstException("The texture does not contain the type mark.")
        
        # Modo de textura
        localmode = int.from_bytes(bytearray(fileData[4:8]), "little")
        if localmode != 3:
            raise Texture3dstException("Texture mode not supported.")
        
        # Verifica que no haya bytes no esperados
        if int.from_bytes(bytearray(fileData[8:12]), "little") != 0:
            raise Texture3dstException(f"Unexpected byte between {hex(8)} and {hex(11)} positions.")
        
        # Obtiene las dimensiones de la textura
        localwidth = int.from_bytes(bytearray(fileData[12:16]), "little")
        localheight = int.from_bytes(bytearray(fileData[16:20]), "little")

        # Verifica que las dimensiones no sean 0
        if localwidth <= 0:
            raise Texture3dstException("The texture width cannot be 0.")
        if localheight <= 0:
            raise Texture3dstException("The texture height cannot be 0.")
        
        # Obtiene el checksum
        localcwidth = int.from_bytes(bytearray(fileData[20:24]), "little")
        localcheight = int.from_bytes(bytearray(fileData[24:28]), "little")

        # Verifica que las dimensiones sean iguales al checksum
        if localwidth != localcwidth:
            raise Texture3dstException("The texture width must be the same as width checksum.")
        if localheight != localcheight:
            raise Texture3dstException("The texture height must be the same as height checksum.")

        # Verifica que las dimensiones sean soportadas
        if localwidth % 8 != 0 and localheight % 8 != 0:
            raise Texture3dstException("Unsupported texture resolution.")
        
        # Verifica que el nivel de mip este dentro de los valores soportados
        localmiplevel = int.from_bytes(bytearray(fileData[28:32]), "little")
        if localmiplevel <= 0:
            raise Texture3dstException("MaxMipLevel must be greater than 0.")
        
        # Verifica el nivel de mipmap
        if not ((localwidth / (2 ** (localmiplevel - 1)) >= 8) and (localheight / (2 ** (localmiplevel - 1)) >= 8)):
            raise Texture3dstException("MaxMipLevel not supported.")

        self.texturemode = localmode
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
        self.data[listPosition:(listPosition + 4)] = [red, green, blue, alpha]
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
        rgba = self.data[listPosition:(listPosition + 4)]
        return rgba
    
    def copy(self, x1: int, y1: int, x2: int, y2: int):
        copyData = [[] for i in  range(y2 - y1)]
        for i in range(y1, y2):
            for j in range(x1, x2):
                copyData[i - y1].append(self.getPixelData(j, i))
        return copyData

    def paste(self, image: Image, x: int, y: int):
        width = image.size[0]
        height = image.size[1]
        imageRgba = image.convert("RGBA")
        imgData = imageRgba.load()
        for i in range(0, height):
            for j in range(0, width):
                r, g, b, a = imgData[j, i]
                self.setPixelRGBA(j, i, r, g, b, a)

    def flipX(self):
        flippedTexture = [0] * self.height * self.width * 4

        x = 0
        y = 0
        y_flipped = self.height - 1
        for i in range(0, self.height):
            for j in range(0, self.width):
                pixelData = self.getPixelData(x, y)
                r, g, b, a = pixelData[0:4]
                flippedTexture = setPixelRGBAfromList(flippedTexture, (x, y_flipped), (self.width, self.height), [r, g, b, a])
                x += 1
            x = 0
            y += 1
            y_flipped -= 1

        self.data = flippedTexture
        return

    def flipY(self):
        flippedTexture = [0] * self.height * self.width * 4

        y = 0
        for i in range(0, self.height):
            x = 0
            x_flipped = self.width - 1
            for j in range(0, self.width):
                pixelData = self.getPixelData(x, y)
                r, g, b, a = pixelData[0:4]
                flippedTexture = setPixelRGBAfromList(flippedTexture, (x_flipped, y), (self.width, self.height), [r, g, b, a])
                x += 1
                x_flipped -= 1
            y += 1

        self.data = flippedTexture
        return

    def getData(self):
        return self.data
    
    def getOutputData(self):
        return self.output

    def convertData(self):        
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
                    r, g, b, a = pixelData[0:4]
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
                        mipTmpData.extend([pixelData[0], pixelData[1], pixelData[2], pixelData[3]])
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
        self.output.extend(self.texturemode.to_bytes(4, "little"))
        self.output.extend([0] * 4)

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