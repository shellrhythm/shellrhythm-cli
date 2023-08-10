import platform
import asyncio
from src.termutil import too_small, refresh, check_term_size
from src.options import OptionsManager
from src.conductor import Conductor
from src.translate import LocaleManager, Locale

class BaseScene:
    """Base scene class. Use this when creating a scene."""
    turn_off:bool = False
    deltatime:float = 0.0
    conduc:Conductor = None
    loc:Locale = LocaleManager.current_locale()

    async def draw(self) -> None:
        """Use this when drawing text on the screen"""

    async def handle_input(self) -> None:
        """As the name says, this function handles user input,\
        but can also double as an update function."""

    async def handle_screen_too_small(self) -> None:
        """Display a message on the screen instead of drawing \
        when the screen does not meet the minimum size requirements"""

    def loop(self) -> None:
        """The looping mechanism. May need to be redone."""
        self.deltatime = self.conduc.update()
        if not too_small(OptionsManager.bypass_minimum_size):
            asyncio.run(self.draw())
        else:
            asyncio.run(self.handle_screen_too_small())

        refresh()
        asyncio.run(self.handle_input())

        if platform.system() == "Windows":
            check_term_size()

    def on_close(self) -> None:
        """Define stuff that happens when the scene ends"""

    def on_open(self) -> None:
        """Define stuff that happens when the scene begins"""

    def __init__(self) -> None:
        pass
