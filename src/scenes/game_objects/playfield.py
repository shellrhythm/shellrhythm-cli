"""I know how this looks, but this isn't an actually usable object.
It's just used internally to check playfield size and position.
Cry about it."""
from src.constants import Vector2, Vector2i, default_size, term


class Playfield:
    position:Vector2 = Vector2(0.5, 0.5)
    size:Vector2i = Vector2i(1, 1)
    offset:Vector2i = Vector2i.zero

    def __init__(self) -> None:
        self.size.x = default_size.x
        self.size.y = default_size.y

    def top_left(self) -> Vector2i:
        out = Vector2i(
            int((term.width-self.size.x) * self.position.x),
            int((term.height-self.size.y) * self.position.y)
        )
        out += self.offset
        return out
