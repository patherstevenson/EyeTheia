class GazePoint:
    def __init__(self, index, x, y):
        self.index = index
        self.x = x
        self.y = y

    def __str__(self):
        # return f"GazePoint({self.index}, {self.x}, {self.y}),"
        return f"({self.x}:{self.y})"
