from math import sqrt
from PIL import Image, ImageTk

import pathlib
localPath : pathlib.Path = pathlib.Path(__file__).parent.resolve()

from Logger import Logger, MessageLevel

defaultVpetDataFile = """# this file holds the data for the vpet in this folder
vpetFrameRate:20 # this is the amount of times the application should update the vpet every second"""

defaultAnimationDataFile = """# this file holds the data for the animation in this folder/ named the same as the file.  All values are caps insensitive, and can have as much whitespace as required.
HoldLastFrame:false # 1 or true to hold the last frame after the animation ends, any other value and the animation repeats after reaching the last frame
UpdatesPerFrame:1 # The amount of vpet updates until it changes the frame of the animation.  First value should always be one number which is the default for unspecified values, then you can specify by frame index (eg "1, 3:10" makes every frame except frame 3 take 1 update, and frame 3 take 10 updates)"""

def GenerateDefaultAnimationDataFile(animationName : str, pathToAnimation : pathlib.Path):
    Logger.instance.Log(MessageLevel.MESSAGE, f"| | Generating default AnimationData file for animation: {animationName}")

    if pathToAnimation.suffix == "": # if it's a directory then create the data file inside the directory
        datafile = open(pathToAnimation.joinpath("animationData.txt"), "w")
    else:
        datafile = open(pathToAnimation.name.split(".")[0] + ".txt", "w")
    datafile.write(defaultAnimationDataFile)
    pass

def GenerateDefaultVpetDataFile(vpetName : str, pathToVpet : pathlib.Path):
    Logger.instance.Log(MessageLevel.MESSAGE, f"| Generating default VpetData file for Vpet: {vpetName}")

    if pathToVpet.suffix == "": # if it's a directory then create the data file inside the directory
        datafile = open(pathToVpet.joinpath("vpetData.txt"), "w")
    else:
        datafile = open(pathToVpet.name.split(".")[0] + ".txt", "w")
    datafile.write(defaultVpetDataFile)
    pass

def CallIfNotNone(function : callable, arg = None):
    if function is not None:
        if arg is not None:
            function(arg)
        else:
            function()
    pass

def LoadImage(pathToImage : pathlib.Path, scale : float):
    image = Image.open(pathToImage)
    image = image.resize((int(image.size[0] * scale), int(image.size[1] * scale)), Image.Resampling.NEAREST)
    return ImageTk.PhotoImage(image)

def Clamp(value, min, max):
    if value > max:
        return max
    if value < min:
        return min
    return value

# this is a vector class made for being used in pixel coordinates for the window
class Vector2:
    def __init__(self, x : int, y : int) -> None:
        self._x = x
        self._y = y
        self.magnitude = sqrt(self.x * self.x + self.y * self.y)
        pass

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value
        self.magnitude = sqrt(self.x * self.x + self.y * self.y)

    # @x.getter
    # def

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = value
        self.magnitude = sqrt(self.x * self.x + self.y * self.y)

    def __add__(self, other):
        x = self.x + other.x
        y = self.y + other.y
        return Vector2(x, y)
    
    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, other : int):
        return Vector2(self.x * other, self.y * other)
    
    def __rmul__(self, other):
        return self.__mul__(other)
    
    def __truediv__(self, other : int):
        x = self.x / other
        y = self.y / other
        return Vector2(x, y)
    
    def __str__(self) -> str:
        return f'Vector2({self.x}, {self.y})'

    def AverageVector(vectors : list):
        totalVector = Vector2(0, 0)

        for vector in vectors:
            totalVector += vector

        return totalVector / len(vectors)
    
import tkinter as tk
from tkinter import ttk


class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="horizontal", command=canvas.xview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.configure(xscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="bottom", fill="x")
