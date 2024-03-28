import numpy, math
from PIL import Image

from .utils import *

class Texture3dstException(Exception):
    def __init__(self, message):
        super().__init__(message)

def setPixelRGBAfromList(data: list, pos: tuple, pixel_data: tuple | list) -> list:
        if type(data) != list:
            raise TypeError("Data expected to be a list.")

        if type(pos) != tuple:
            raise TypeError("Position expected to be a tuple.")
        if len(pos) == 2:
            if not all(isinstance(num, int) for num in pos):
                raise TypeError("Coordinates must be integers.")
        else:
            raise ValueError("Position must have 2 values.")
        
        if type(pixel_data) == list:
            pixel_data = tuple(pixel_data)
        if type(pixel_data) != tuple:
            raise ValueError("Pixel_data expected to be a tuple or list.")
        for num in pixel_data:
            if isinstance(num, int):
                if num < 0 or num > 255:
                    raise Texture3dstException("Pixel_data values must be between 0 and 255.")
            else:
                raise Texture3dstException("Pixel_data must be only integers.")

        data[pos[1]][pos[0]] = list(pixel_data)
        return data

def getPixelDataFromList(data: list, pos: tuple) -> list:
        if type(data) != list:
            raise Texture3dstException("data expected to be a list.")
        
        if type(pos) != tuple:
            raise TypeError("Position expected to be a tuple.")
        if len(pos) == 2:
            if not all(isinstance(num, int) for num in pos):
                raise TypeError("Coordinates must be integers.")
        else:
            raise ValueError("Position must have 2 values.")
        return data[pos[1]][pos[0]]

def convertFunction(data: list, width: int, height: int, conversiontype: int):
        if type(data) != list:
            raise Texture3dstException("Data expected to be a list.")
        if type(width) != int:
            raise Texture3dstException("Width expected to be an integer.")
        if type(height) != int:
            raise Texture3dstException("Height expected to be an integer.")
        if type(conversiontype) != int:
            raise Texture3dstException("Conversion type must be and integer.")
        if not (conversiontype >= 1 and conversiontype <= 2):
            raise Texture3dstException("Conversion type must be 1 or 2.")
        
        convertedData = [[] for _ in range(height)]
        for i in range(height):
            for j in range(width):
                convertedData[i].append([])
                convertedData[i][j] = [0] * 4

        x = 0
        y = 0
        x2 = 0
        y2 = 0
        # Bucle que itera siguiendo el patron de guardado visto en estas texturas
        for i in range(0, height // 8):
            for j in range(0, width // 8):
                for k in range(0, 2):
                    for l in range(0, 2):
                        for m in range(0, 2):
                            for n in range(0, 2):
                                for o in range(0, 2):
                                    for p in range(0, 2):
                                        # Tipo 1 es para generar de una imagen su textura en 3dst
                                        # Tipo 2 es para de una textura 3dst crear una imagen
                                        if conversiontype == 1:
                                            pixelData = getPixelDataFromList(data, (x, y))
                                            if pixelData[3] == 0:
                                                for q in range(0, 4):
                                                    # [0] * 4 crea una lista: [0, 0, 0, 0]
                                                    convertedData[y2][x2] = [0] * 4
                                            else:
                                                # Como es de tipo 1 se tendrán que guardar los valores rgba invertidos
                                                # [::-1] crea una lista invertida y la retorna
                                                pixelData = pixelData[::-1]
                                                convertedData[y2][x2] = pixelData
                                        else:
                                            # Como es de tipo 2 los valores rgba están en posiciones invertidas
                                            # data[y2][x2][::-1] obtiene los valores a, b, g, r del pixel y los invierte
                                            # convertedData = setPixelRGBAfromList(convertedData, (x, y), data[y2][x2][::-1])
                                            setPixelRGBAfromList(convertedData, (x, y), data[y2][x2][::-1])
                                        x2 += 1
                                        if x2 >= width:
                                            y2 += 1
                                            x2 = 0
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

    def open(self, path: str = None):
        if type(path) != str or path == None:
            raise Texture3dstException("Invalid path.")
        
        with open(f"{path}", "rb") as f:
            fileData = f.read()
        
        # Empieza el analisis de la cabecera-Marca de agua
        if extract_chunk(fileData, 0) != bytes.fromhex("33445354"):
            raise Texture3dstException("The texture does not contain the type mark.")
        
        # Modo de textura
        mode = bytes_to_uint(extract_chunk(fileData, 1), "little")
        if mode != 3:
            raise Texture3dstException("Texture mode not supported.")
        
        # Verifica que no haya bytes desconocidos
        if bytes_to_uint(extract_chunk(fileData, 2), "little") != 0:
            raise Texture3dstException(f"Unknown data in element 2 of the file. Possible unsupported texture.")
        
        # Obtiene las dimensiones de la textura
        width = bytes_to_uint(extract_chunk(fileData, 3), "little")
        height = bytes_to_uint(extract_chunk(fileData, 4), "little")

        # Verifica que las dimensiones no sean menores a 0 y que sean múltiplo de 8 (Textura soportada actualmente)
        if width <= 0 or width % 8 != 0:
            raise Texture3dstException(f"Unsupported texture width '{width}'.")
        if height <= 0 or height % 8 != 0:
            raise Texture3dstException(f"Unsupported texture height '{height}'.")
        
        # Obtiene el checksum
        cwidth = bytes_to_uint(extract_chunk(fileData, 5), "little")
        cheight = bytes_to_uint(extract_chunk(fileData, 6), "little")

        # Verifica que las dimensiones sean iguales al checksum
        if width != cwidth:
            raise Texture3dstException("The texture width must be the same as width checksum. Possible unsupported texture.")
        if height != cheight:
            raise Texture3dstException("The texture height must be the same as height checksum. Possible unsupported texture.")
        
        # Verifica que el nivel de mip este dentro de los valores soportados
        miplevel = bytes_to_uint(extract_chunk(fileData, 7), "little")
        if miplevel <= 0:
            raise Texture3dstException("MipLevel must be greater than 0.")
        
        # Verifica el nivel de mipmap
        if not ((width / (2 ** (miplevel - 1)) >= 8) and (height / (2 ** (miplevel - 1)) >= 8)):
            raise Texture3dstException("MipLevel not supported.")

        self.mode = mode
        self.width = width
        self.height = height
        self.miplevel = miplevel
        self.convertedData = []
        self.mipoutput = []
        self.output = []

        data = list(fileData[(4*8):len(fileData)])
        shorted_data = [[] for _ in range(height)]
        for i in range(height):
            for j in range(width):
                shorted_data[i].append([])
                shorted_data[i][j] = data[((i * width) + j) * 4:(((i * width) + j) * 4) + 4]

        # Se utiliza el segundo método de conversion para cargar la textura
        self.data = convertFunction(shorted_data, width, height, 2)

        return self

    def new(self, width: int, height: int, miplevel: int = 1):
        if type(width) != int:
            raise Texture3dstException("Width expected to be an integer.")
        if type(height) != int:
            raise Texture3dstException("Height expected to be an integer.")
        if type(miplevel) != int:
            raise Texture3dstException("MaxMipLevel expected to be an integer.")
        if width <= 0:
            raise Texture3dstException("Width must be greater than 0.")
        if width > 61440:
            raise Texture3dstException("Width cannot be greater than 61440.")
        if height <= 0:
            raise Texture3dstException("Height must be greater than 0.")
        if height > 61440:
            raise Texture3dstException("Height cannot be greater than 61440.")
        if width % 8 != 0:
            width = ((width // 8) * 8) + 8
        if height % 8 != 0:
            height = ((height // 8) * 8) + 8
        if miplevel <= 0:
            raise Texture3dstException("MipLevel must be greater than 0.")
        if not ((width / (2 ** (miplevel - 1)) >= 8) and (height / (2 ** (miplevel - 1)) >= 8)):
            raise Texture3dstException("MipLevel value greater than supported.")
        self.width = width
        self.height = height
        self.miplevel = miplevel
        self.mode = 3
        data = [[] for _ in range(height)]
        for i in range(height):
            for j in range(width):
                data[i].append([])
                data[i][j] = [0] * 4
        self.data = data
        self.convertedData = []
        self.mipoutput = []
        self.output = []
        return self

    def setPixelRGBA(self, x: int, y: int, pixel_data: tuple | list) -> None:
        if type(x) != int:
            raise Texture3dstException("x coordinates expected to be an integer.")
        if type(y) != int:
            raise Texture3dstException("y coordinates expected to be an integer.")
        if x < 0 or x >= self.width:
            raise Texture3dstException("x coordinates out of range.")
        if y < 0 or y >= self.height:
            raise Texture3dstException("y coordinates out of range.")
        
        if type(pixel_data) == list:
            pixel_data = tuple(pixel_data)
        if type(pixel_data) != tuple:
            raise Texture3dstException("pixel_data expected to be a tuple or list.")
        for num in pixel_data:
            if isinstance(num, int):
                if num < 0 or num > 255:
                    raise Texture3dstException("pixel_data values must be between 0 and 255.")
            else:
                raise Texture3dstException("pixel_data must be only integers.")
        self.data[y][x] = list(pixel_data)
        self.convertedData = []
        self.mipoutput = []
        return

    def getPixelData(self, x: int, y: int) -> list:
        if type(x) != int:
            raise Texture3dstException("x coordinates expected to be an integer.")
        if type(y) != int:
            raise Texture3dstException("y coordinates expected to be an integer.")
        if x < 0 or x >= self.width:
            raise Texture3dstException("x coordinates out of range.")
        if y < 0 or y >= self.height:
            raise Texture3dstException("y coordinates out of range.")
        return self.data[y][x]
    
    def copy(self, x1: int, y1: int, x2: int, y2: int) -> Image.Image:
        copyData = [[] for _ in  range(y2 - y1)]
        for i in range(y1, y2):
            for j in range(x1, x2):
                if len(self.data[i][j]) < 4:
                    copyData[i - y1].append(self.data[i][j])
                else:
                    copyData[i - y1].append(self.data[i][j])
        buffer = numpy.asarray(copyData, dtype=numpy.uint8)
        return Image.fromarray(buffer)

    def fromImage(self, image: Image.Image):
        img_w, img_h = image.size
        texture = self.new(img_w, img_h, 1)
        texture.paste(image, 0, 0)
        return self

    def paste(self, image: Image.Image, x: int, y: int) -> None:
        width = image.size[0]
        height = image.size[1]
        imageRgba = image.convert("RGBA")
        imgData = imageRgba.load()
        for i in range(y, height):
            for j in range(x, width):
                r, g, b, a = imgData[j, i]
                self.setPixelRGBA(j, i, (r, g, b, a))
        # Avoid export without convert data after a change
        self.convertedData = []
        self.mipoutput = []
        return

    def flipX(self) -> None:
        self.data.reverse()
        self.convertedData = []
        self.mipoutput = []
        return

    def flipY(self) -> None:
        for element in self.data:
            element.reverse()
        self.convertedData = []
        self.mipoutput = []
        return

    def getData(self) -> list:
        return self.data
    
    def getOutputData(self) -> list:
        return self.output

    def convertData(self) -> None:        
        self.convertedData = convertFunction(self.data, self.width, self.height, 1)

        if self.miplevel > 1:
            self.mipoutput = []
            width = self.width
            height = self.height
            resizedwidth = self.width
            resizedheight = self.height

            # Copia la información de data a una imagen temporal
            tmpImage = Image.new("RGBA", (width, height))
            tmpImagePixels = tmpImage.load()
            for y in range(0, height):
                for x in range(0, width):
                    pixelData = getPixelDataFromList(self.data, (x, y))
                    tmpImagePixels[x, y] = tuple(pixelData)

            self.mipoutput = [[] for _ in range(self.miplevel - 1)]
            for i in range(0, self.miplevel - 1):
                # Se reescala la imagen
                resizedwidth = resizedwidth // 2
                resizedheight = resizedheight // 2
                tmpImage = tmpImage.resize((resizedwidth, resizedheight), Image.Resampling.LANCZOS)

                # Se obtiene los datos de la imagen reescalada
                mipTmpData = [[] for _ in range(resizedheight)]
                for y in range(0, resizedheight):
                    for x in range(0, resizedwidth):
                        mipTmpData[y].append([])
                        pixelData = tmpImage.getpixel((x, y))
                        mipTmpData[y][x] = pixelData[:]

                # Se convierte los datos usando la funcion
                self.mipoutput[i] = convertFunction(mipTmpData, resizedwidth, resizedheight, 1)

                # Se reducen las dimensiones en caso de usarse de nuevo
                width = width // 2
                height = height // 2
            mipTmpData = []
        return
    
    def export(self, path: str) -> None:
        if type(path) != str:
            raise TypeError("path expected to be a string.")

        # Se crea la cabecera
        ## Marca de formato
        self.output = bytearray(uint_to_bytes(bytes_to_uint(bytes.fromhex("33445354"), "little"), "little"))
        ## Modo de textura
        self.output.extend(uint_to_bytes(self.mode, "little"))
        ## No sé aún pero mientras tanto debería ser 0 xd
        self.output.extend(uint_to_bytes(0, "little"))

        ## Se repite dos veces para las dimensiones y el checksum
        for i in range(0, 2):
            self.output.extend(uint_to_bytes(self.width, "little"))
            self.output.extend(uint_to_bytes(self.height, "little"))
        ### Mip level
        self.output.extend(uint_to_bytes(self.miplevel, "little"))

        ## Se copia la lista de convertedData a output - Nivel primario
        for y in self.convertedData:
            for pixel in y:
                for channel in pixel:
                    self.output.append(channel)
        
        ## Se copian los niveles de mipoutput (si hay) - Niveles de mip
        if self.miplevel > 1:
            for nivel in self.mipoutput:
                for y in nivel:
                    for pixel in y:
                        for channel in pixel:
                            self.output.append(channel)

        # Se escriben los bytes en un archivo
        with open(f"{path}", "wb") as f:
            f.write(self.output)
        return
    