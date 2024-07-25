import numpy
from PIL import Image
from pathlib import Path

from .utils import *

class Texture3dstException(Exception):
    def __init__(self, message):
        super().__init__(message)

def isPowerOfTwo(num: int):
    return (num & (num - 1)) == 0

def getClosestPowerOfTwo(num: int):
    min = 2
    while min < num:
        min *= 2
    return min

def maxIntBits(n: int):
    # Verificar que n sea un número entero positivo
    if n <= 0:
        raise ValueError("El número de bits debe ser un entero positivo.")
    
    # Calcular el número máximo representable con n bits
    max_num = (2 ** n) - 1
    return max_num

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

        if len(pixel_data) != len(data[pos[1]][pos[0]]):
            raise ValueError("Pixel_data lenght does not match with original pixel")

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

def convertRGBA5551toRGBA8(data: list):
    tmpData = []
    for i in range(len(data)):
        tmpData.append([])
        for j in range(len(data[i])):
            tmpData[-1].append([])
            byte1 = data[i][j][0]
            byte2 = data[i][j][1]

            combined = (byte2 << 8) | byte1

            a = int((combined >> 0) & 0b1)
            b = int((combined >> 1) & 0b11111)
            g = int((combined >> 6) & 0b11111)
            r = int((combined >> 11) & 0b11111)

            a = a * 255
            b = int((b/maxIntBits(5))*255)
            g = int((g/maxIntBits(5))*255)
            r = int((r/maxIntBits(5))*255)

            tmpData[-1][-1].extend([a, b, g, r])
    return tmpData

def convertRGB565toRGB8(data: list):
    tmpData = []
    for i in range(len(data)):
        tmpData.append([])
        for j in range(len(data[i])):
            tmpData[-1].append([])
            byte1 = data[i][j][0]
            byte2 = data[i][j][1]

            combined = (byte2 << 8) | byte1

            b = int((combined >> 0) & 0b11111)
            g = int((combined >> 5) & 0b111111)
            r = int((combined >> 11) & 0b11111)

            b = int((b/maxIntBits(5))*255)
            g = int((g/maxIntBits(6))*255)
            r = int((r/maxIntBits(5))*255)

            tmpData[-1][-1].extend([b, g, r])
    return tmpData

def convertRGBA4toRGBA8(data: list):
    tmpData = []
    for i in range(len(data)):
        tmpData.append([])
        for j in range(len(data[i])):
            tmpData[-1].append([])
            byte1 = data[i][j][0]
            byte2 = data[i][j][1]

            combined = (byte2 << 8) | byte1

            a = int((combined >> 0) & 0b1111)
            b = int((combined >> 4) & 0b1111)
            g = int((combined >> 8) & 0b1111)
            r = int((combined >> 12) & 0b1111)

            a = int((a/maxIntBits(4))*255)
            b = int((b/maxIntBits(4))*255)
            g = int((g/maxIntBits(4))*255)
            r = int((r/maxIntBits(4))*255)

            tmpData[-1][-1].extend([a, b, g, r])
    return tmpData

def convertLA4toLA8(data: list):
    tmpData = []
    for i in range(len(data)):
        tmpData.append([])
        for j in range(len(data[i])):
            tmpData[-1].append([])
            byte1 = data[i][j][0]

            a = int((byte1 >> 0) & 0b1111)
            l = int((byte1 >> 4) & 0b1111)

            a = int((a/maxIntBits(4))*255)
            l = int((l/maxIntBits(4))*255)

            tmpData[-1][-1].extend([a, l])
    return tmpData

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
        
        channels = len(data[0][0])

        convertedData = [[] for _ in range(height)]
        for i in range(height):
            for j in range(width):
                convertedData[i].append([0] * channels)

        # Bucle que itera siguiendo el patron de guardado visto en estas texturas
        for x in range(width):
            for y in range(height):
                dstPos = ((((y >> 3) * (width >> 3) + (x >> 3)) << 6) + ((x & 1) | ((y & 1) << 1) | ((x & 2) << 1) | ((y & 2) << 2) | ((x & 4) << 2) | ((y & 4) << 3)))
                y2 = (dstPos//width)
                x2 = dstPos - (y2*width)
                if conversiontype == 1:
                    # For convert from linear raw pixel data to 3dst texture data
                    pixelData = getPixelDataFromList(data, (x, y))
                    setPixelRGBAfromList(convertedData, (x2, y2), pixelData[::-1])
                elif conversiontype == 2:
                    # This does the opposite
                    setPixelRGBAfromList(convertedData, (x, y), data[y2][x2][::-1])

        return convertedData

class Texture3dst:
    formats = ("rgba8", "rgb8", "rgba5551", "rgb565", "rgba4", "la8", "", "", "", "la4")

    def __init__(self):
        return

    def open(self, path: str | Path):
        if type(path) == str:
            path = Path(path)
        if not isinstance(path, Path):
            raise Texture3dstException("Expected str or Path type for path.")
        
        with open(path, "rb") as f:
            fileData = f.read()
        
        # Empieza el analisis de la cabecera-Marca de agua
        if extract_chunk(fileData, 0) != bytes.fromhex("33445354"):
            raise Texture3dstException("The texture does not contain the type mark.")
        
        # Modo de textura y formato
        ## l = escala de grises
        mode = bytes_to_uint(extract_chunk(fileData, 1), "little")
        format = bytes_to_uint(extract_chunk(fileData, 2), "little")
        if mode == 3:
            if format < 0 or format > len(self.formats) - 1:
                raise Texture3dstException(f"Texture format unsupported: {format}.")
            else:
                format = self.formats[format]
                if format == "":
                    raise Texture3dstException(f"Texture format unsupported: {format}.")
        else:
            raise Texture3dstException(f"Unsupported mode: {mode}.")
        
        # Obtiene las dimensiones de la textura
        texwidth = bytes_to_uint(extract_chunk(fileData, 3), "little")
        texheight = bytes_to_uint(extract_chunk(fileData, 4), "little")

        # Verifica que las dimensiones son una potencia de dos
        if not isPowerOfTwo(texwidth):
            raise Texture3dstException(f"Invalid texture width '{texwidth}'.")
        if not isPowerOfTwo(texheight):
            raise Texture3dstException(f"Invalid texture height '{texheight}'.")
        
        # Obtiene las dimensiones originales de la textura
        width = bytes_to_uint(extract_chunk(fileData, 5), "little")
        height = bytes_to_uint(extract_chunk(fileData, 6), "little")
        
        # Verifica que el nivel de mip este dentro de los valores soportados
        miplevel = bytes_to_uint(extract_chunk(fileData, 7), "little")
        if miplevel <= 0:
            raise Texture3dstException("MipLevel must be greater than 0.")
        
        # Verifica el nivel de mipmap
        if not ((texwidth / (2 ** (miplevel - 1)) >= 8) and (texheight / (2 ** (miplevel - 1)) >= 8)):
            raise Texture3dstException("MipLevel not supported.")

        self.mode = mode
        self.format = format
        self.width = width
        self.texwidth = texwidth
        self.height = height
        self.texheight = texheight
        self.miplevel = miplevel
        self.convertedData = []
        self.mipoutput = []
        self.output = []

        # Establece la longitud de bytes que tiene cada pixel en cada formato
        match format:
            case "rgba8":
                lenpixel = 4
            case "rgb8":
                lenpixel = 3
            case "rgba5551":
                lenpixel = 2
            case "rgba565":
                lenpixel = 2
            case "rgba4":
                lenpixel = 2
            case "la4":
                lenpixel = 1
            case "la8":
                lenpixel = 2

        data = list(fileData[(4*8):len(fileData)])
        shorted_data = [[] for _ in range(texheight)]
        for i in range(texheight):
            for j in range(texwidth):
                shorted_data[i].append(data[((i * texwidth) + j) * lenpixel:(((i * texwidth) + j) * lenpixel) + lenpixel])

        # Aplica metodos de conversion si es necesario
        match format:
            case "rgba5551":
                shorted_data = convertRGBA5551toRGBA8(shorted_data)
            case "rgb565":
                shorted_data = convertRGB565toRGB8(shorted_data)
            case "rgba4":
                shorted_data = convertRGBA4toRGBA8(shorted_data)
            case "la4":
                shorted_data = convertLA4toLA8(shorted_data)

        # Se utiliza el segundo método de conversion para cargar la textura
        self.data = convertFunction(shorted_data, texwidth, texheight, 2)

        # Establece la cantidad de canales que resultan al final en cada formato
        match format:
            case "rgba8":
                self.channels = 4
            case "rgb8":
                self.channels = 3
            case "rgba5551":
                self.channels = 4
            case "rgb565":
                self.channels = 3
            case "rgba4":
                self.channels = 4
            case "la4":
                self.channels = 2

        return self

    def new(self, width: int, height: int, miplevel: int = 1, format: str = "rgba8"):
        if type(width) != int:
            raise Texture3dstException("Width expected to be an integer.")
        if type(height) != int:
            raise Texture3dstException("Height expected to be an integer.")
        if type(miplevel) != int:
            raise Texture3dstException("MaxMipLevel expected to be an integer.")
        if width <= 0:
            raise Texture3dstException("Width must be greater than 0.")
        if height <= 0:
            raise Texture3dstException("Height must be greater than 0.")
        texwidth = getClosestPowerOfTwo(width)
        texheight = getClosestPowerOfTwo(height)
        if miplevel <= 0:
            raise Texture3dstException("MipLevel must be greater than 0.")
        if not ((width / (2 ** (miplevel - 1)) >= 8) and (height / (2 ** (miplevel - 1)) >= 8)):
            raise Texture3dstException("MipLevel value greater than supported.")
        if not (format in self.formats and format != ""):
            raise Texture3dstException(f"Unsupported format '{format}'")
        
        if format == "rgba8":
            self.channels = 4
        elif format == "rgb8":
            self.channels = 3
        self.format = format
        self.texwidth = texwidth
        self.width = width
        self.texheight = texheight
        self.height = height
        self.miplevel = miplevel
        self.mode = 3
        data = [[] for _ in range(texheight)]
        for i in range(texheight):
            for j in range(texwidth):
                data[i].append([0] * self.channels)
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
        if len(pixel_data) != self.channels:
            raise Texture3dstException("pixel_data lenght does not match with texture channels")
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
        if not (x1 >= 0 and x1 <= self.width):
            raise Texture3dstException("x1 coordinates out of range")
        if not (x2 >= 0 and x2 <= self.width and x2 >= x1):
            raise Texture3dstException("x2 coordinates out of range or invalid value")
        if not (y1 >= 0 and y1 <= self.height):
            raise Texture3dstException("y1 coordinates out of range")
        if not (y2 >= 0 and y2 <= self.height and y2 >= y1):
            raise Texture3dstException("y2 coordinates out of range or invalid value")
        copyData = [[] for _ in  range(y2 - y1)]
        for i in range(y1, y2):
            for j in range(x1, x2):
                copyData[i - y1].append(self.data[i][j])
        buffer = numpy.asarray(copyData, dtype=numpy.uint8)
        return Image.fromarray(buffer)

    def fromImage(self, image: Image.Image):
        img_w, img_h = image.size
        texture = self.new(img_w, img_h, 1)
        texture.paste(image, 0, 0)
        return self

    def paste(self, image: Image.Image, x: int, y: int) -> None:
        if self.format == "rgba8" or self.format == "rgba5551":
            tformat = "RGBA"
        elif self.format == "rgb8":
            tformat = "RGB"
        width = image.size[0]
        height = image.size[1]
        if width > self.width or height > self.height:
            raise Texture3dstException("Source image is bigger than destination texture")
        imageRgba = image.convert(tformat)
        imgData = imageRgba.load()
        for i in range(y, height):
            for j in range(x, width):
                self.setPixelRGBA(j, i, list(imgData[j, i])[::])
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
        self.convertedData = convertFunction(self.data, self.texwidth, self.texheight, 1)

        if self.miplevel > 1:
            self.mipoutput = []
            width = self.texwidth
            height = self.texheight
            resizedwidth = self.texwidth
            resizedheight = self.texheight

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
    
    def export(self, path: str | Path) -> None:
        if type(path) == str:
            path = Path(path)
        if not isinstance(path, Path):
            raise TypeError("Expected str or Path type for path.")

        # Se crea la cabecera
        ## Marca de formato
        self.output = bytearray(uint_to_bytes(bytes_to_uint(bytes.fromhex("33445354"), "little"), "little"))
        ## Modo de textura
        self.output.extend(uint_to_bytes(self.mode, "little"))
        ## No sé aún pero mientras tanto xd (posiblemente es el formato)
        self.output.extend(uint_to_bytes(self.formats.index(self.format), "little"))

        ## Se escriben las dimensiones de la textura
        self.output.extend(uint_to_bytes(self.texwidth, "little"))
        self.output.extend(uint_to_bytes(self.texheight, "little"))

        ## Se escriben las dimensiones de la textura original
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
        with open(path, "wb") as f:
            f.write(self.output)
        return
    