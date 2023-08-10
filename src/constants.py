"""Defines constants used all over the codebase"""

from src.termutil import term, reset_color

class Vector2(object):
    """I needed this Vector2. I had enough of using arrays"""
    x:float = 0
    y:float = 0

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

    def __getitem__(self, item) -> float:
        return self.x if item == 0 else (self.y if item == 1 else getattr(self, item))

class Vector2i(Vector2):
    """Vector2 but integers only"""
    x:int = 0
    y:int = 0


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

colors = [
    reset_color,
    term.red,
    term.orange,
    term.yellow,
    term.green,
    term.cyan,
    term.blue,
    term.purple,
    term.aqua,
    term.magenta,
    term.gray
]

default_size:Vector2i = Vector2i(80, 24)

INPUT_FREQUENCY = 999

hitWindows = [0.05, 0.1, 0.2, 0.3, 0.4]
JUDGEMENT_NAMES = [
    f"{term.purple}MARV", 
    f"{term.aqua}PERF", 
    f"{term.green}EPIC", 
    f"{term.yellow}GOOD", 
    f"{term.orange} EH ", 
    f"{term.red}MISS"]

JUDGEMENT_NAMES_SHORT = [
    f"{term.purple}@", 
    f"{term.aqua}#", 
    f"{term.green}$", 
    f"{term.yellow}*", 
    f"{term.orange};", 
    f"{term.red}/"
]
RANKS = [
    ["@", 1000000, term.purple	,term.on_webpurple,		term.on_color_rgb(148, 29, 96)	],	# @
    ["S",  950000, term.aqua	,term.on_cyan4,			term.on_color_rgb(29, 106, 148)	],	# #
    ["A",  825000, term.green	,term.on_darkgreen,		term.on_color_rgb(36, 85, 36)	],	# $
    ["B",  700000, term.yellow	,term.on_yellow4,		term.on_color_rgb(112, 110, 22)	],	# *
    ["C",  600000, term.orange	,term.on_goldenrod4,	term.on_color_rgb(148, 77, 29)	],	# ;
    ["D",  500000, term.red		,term.on_darkred,		term.on_color_rgb(83, 14, 14)	],	# /
    ["F",       0, term.grey	,term.on_black,		],	# _
]
accMultiplier = [1, 0.95, 0.85, 0.75, 0.5, 0]

MAX_SCORE = 1000000

__version__ = "1.1.0"
