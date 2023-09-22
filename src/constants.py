"""Defines constants used all over the codebase"""

from src.termutil import term

class staticproperty(property):
    def __get__(self, owner_self, owner_cls):         
        return self.fget()

class Vector2(object):
    """I needed this Vector2. I had enough of using arrays"""
    x:float = 0
    y:float = 0

    @staticproperty
    def zero(): #pylint: disable=no-method-argument
        """The (0,0) vector"""
        return Vector2(0,0)

    @staticmethod
    def from_list(input_list:list):
        """Converts a list (gross, ugly!!!) into a Vector2 (slick, very smort!)"""
        return Vector2(input_list[0], input_list[1])

    def to_list(self) -> list:
        """Converts a Vector2 (chad) back into a list (cringe)"""
        return [self.x, self.y]

    def __init__(self, x=0, y=0) -> None:
        self.x = x
        self.y = y

    def __add__(self, other):
        if isinstance(other, Vector2):
            return Vector2(
                self.x + other.x,
                self.y + other.y
            )

    def __str__(self) -> str:
        return f"[{self.x}, {self.y}]"

    def __getitem__(self, item) -> float:
        return self.x if item == 0 else (self.y if item == 1 else getattr(self, item))

class Vector2i(Vector2):
    """Vector2 but integers only"""
    x:int = 0
    y:int = 0

    @staticproperty
    def zero(): #pylint: disable=no-method-argument
        """The (0,0) vector"""
        return Vector2i()

    def __add__(self, other):
        if isinstance(other, Vector2i):
            return Vector2i(
                self.x + other.x,
                self.y + other.y
            )


#Text object anchors
CENTER = 0
LEFT = 1
DOWN = 2
UP = 3
RIGHT = 4
DOWN_LEFT = 5
DOWN_RIGHT = 6
UP_LEFT = 7
UP_RIGHT = 8

#Text object alignment
ALIGN_LEFT = 0
ALIGN_CENTER = 1
ALIGN_RIGHT = 2

default_size:Vector2i = Vector2i(80, 24)

INPUT_FREQUENCY = 9999

hitWindows = [0.05, 0.1, 0.2, 0.3, 0.4]
class Color:
    r:int = 255
    g:int = 255
    b:int = 255

    def __init__(self, hexcode:str) -> None:
        self.hex_value = hexcode

    @property
    def col(self):
        return term.color_rgb(self.r, self.g, self.b)

    @property
    def on_col(self):
        return term.on_color_rgb(self.r, self.g, self.b)

    @property
    def hex_value(self):
        return hex(self.r * 256**2 + \
                   self.g * 256 + \
                   self.b)[2:]

    @hex_value.setter
    def hex_value(self, hexcode:str):
        val = int(hexcode, 16)
        self.r = val//256**2
        self.g = (val%256**2)//256
        self.b = val%256

colors = [
    term.normal,
    Color("fc220a"), # term.red,
    Color("fc9b0a"), # term.orange,
    Color("f4fc0a"), # term.yellow,
    Color("0efc0a"), # term.green,
    Color("0afcfc"), # term.cyan,
    Color("0a36fc"), # term.blue,
    Color("830afc"), # term.purple
    Color("0ab7fc"), # term.aqua,
    Color("fc0ab3"), # term.magenta,
    Color("72737c") # term.gray
]

blockStates = [" ", "▏", "▎", "▍", "▌", "▋", "▊", "▉", "█"]

# [
#     Rank icon
#     Minimum score
#     Color
#     Background color (Accuracy)
#     Background color
# ]
RANKS = [
    [
        "@",
        1000000,
        Color("C500D5"),
        Color("8C0097"),
        Color("6D0077")
    ],	# @
    [
        "S",
        950000,
        Color("00FFFF"),
        Color("008F8F"),
        Color("006F6F"),
    ],	# #
    [
        "A",
        825000,
        Color("00FF1F"),
        Color("009F2F"),
        Color("006F00")
    ],	# $
    [
        "B",
        700000,
        Color("FFFF00"),
        Color("8F8F2F"),
        Color("6F6F3F")
    ],	# *
    [
        "C",
        600000,
        Color("fc9b0a"),
        Color("914712"),
        Color("944d1d")
    ],	# ;
    [
        "D",
        500000,
        Color("fc2323"),
        Color("960101"),
        Color("530e0e")
    ],	# /
    [
        "F",
        0,
        Color("a1a6af"),
        Color("010101"),
        Color("000000")
    ],	# _
]
JUDGEMENT_NAMES = [
    f"{RANKS[0][2].col}MARV", 
    f"{RANKS[1][2].col}PERF", 
    f"{RANKS[2][2].col}EPIC", 
    f"{RANKS[3][2].col}GOOD", 
    f"{RANKS[4][2].col} EH ", 
    f"{RANKS[5][2].col}MISS"
]

JUDGEMENT_NAMES_SHORT = [
    f"{RANKS[0][2].col}@", 
    f"{RANKS[1][2].col}#", 
    f"{RANKS[2][2].col}$", 
    f"{RANKS[3][2].col}*", 
    f"{RANKS[4][2].col};", 
    f"{RANKS[5][2].col}/"
]
accMultiplier = [1, 0.95, 0.85, 0.75, 0.5, 0]

MAX_SCORE = 1000000

__version__ = "1.2.0"
