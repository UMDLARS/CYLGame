from copy import copy, deepcopy


class FrameBuffer(object):
    # TODO: decide what should go here.
    pass
    # def __init__(self, width, height):
    #     self.x = width
    #     self.y = height


class GridFrameBuffer(FrameBuffer):
    def __init__(self, width, height, charset=None, init_value=0):
        """
        Args:
            width(int):
            height(int):
            charset(CharSet): The char set to use when drawing this frame buffer. (This is optional. If you don't set
                              then any draw function will not work.)
            init_value:
        """
        # super(GridFrameBuffer, self).__init__(width, height)
        self.x = width
        self.y = height
        self.charset = charset
        self.arr = []
        for i in range(height):
            self.arr += [[init_value]*width]

    def set(self, x, y, char):
        """

        Args:
            x(int):
            y(int):
            char(int): The id of the char.
        """
        if isinstance(char, str):
            assert len(char) == 1
            char = ord(char)
        self.arr[y][x] = char

    def draw_to_surface(self, surface):
        if not self.charset:
            raise ValueError("CharSet must be set if you would like to draw anything!")
        # TODO: handle background better
        surface.fill((0, 0, 0))
        for y, row in enumerate(self.arr):
            for x, char in enumerate(row):
                surface.blit(self.charset.get_img(char), self.charset.char_size_to_pix((x, y)))

    def dump(self):
        """

        Returns:
            List[List[int]]: a copy of the frame buffer's grid
        """
        return list(map(copy, self.arr))


# TODO: given this class a better name.
class GameFrame(FrameBuffer):
    def __init__(self):
        self.objs = []

    def draw_char(self, c, x, y, height, width):
        self.objs.append(["char", [c, x, y, height, width]])

    def draw_tank(self, x, y, rotation, turret, fire, led, color):
        self.objs.append(["tank", [x, y, rotation, turret, fire, led, color]])

    def draw_crater(self, x, y, rotation, color):
        self.objs.append(["crater", [x, y, rotation, color]])

    def draw_sensors(self, x, y, rotation, turret, color, sensors):
        self.objs.append(["sensors", [x, y, rotation, turret, color, deepcopy(sensors)]])

    def get_obj_array(self):
        return self.objs
