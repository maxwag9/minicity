import pygame

class MenuManager:
    def __init__(self):
        self.current_menu = None

    class Button:
        def __init__(self, color, top_left, bottom_right):
            if len(top_left) != 2 or len(bottom_right) != 2:
                raise ValueError(
                    f"top_left and bottom_right must be (x, y) tuples, got {top_left} and {bottom_right}"
                )

            self.color = color
            self.top_left = top_left
            self.bottom_right = bottom_right

        @property
        def width(self): return self.bottom_right[0] - self.top_left[0]
        @property
        def height(self): return self.bottom_right[1] - self.top_left[1]
        @property
        def cx(self): return self.top_left[0] + self.width / 2
        @property
        def cy(self): return self.top_left[1] + self.height / 2
        @property
        def rect(self):
            """Return a pygame-compatible rect tuple (x, y, width, height)."""
            return self.top_left[0], self.top_left[1], self.width, self.height

        @classmethod
        def from_center(cls, color, center, size):
            cx, cy = center
            w, h = size
            top_left = (cx - w / 2, cy - h / 2)
            bottom_right = (cx + w / 2, cy + h / 2)
            return cls(color, top_left, bottom_right)

    class MenuScreen:
        def __init__(self, name: str, buttons: list['MenuManager.Button']):
            if not all(isinstance(b, MenuManager.Button) for b in buttons):
                raise TypeError("All elements in 'buttons' must be Button instances!!!")
            self.name = name
            self.buttons = buttons

