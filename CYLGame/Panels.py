import traceback
from collections import defaultdict
from copy import copy
from functools import reduce

from CYLGame.Utils import deprecated

DEFAULT_CHAR = ' '


def is_char(c):
    return type(c) == str and len(c) == 1


def is_coord(p):
    return type(p) == tuple and len(p) == 2 and type(p[0]) == int and type(p[1]) == int


class Map(object):
    """
    char_to_ps: This is a dictionary which has a character for the keys and the value for the key is a set of all the
                positions where that char is located.
    p_to_char:  The is a dictionary which has a position(tuple with two elements: x and y) as a key and the current
                ColoredChar as the value.
    """

    def __init__(self, width, height, default_char=DEFAULT_CHAR):
        self.w = width
        self.h = height
        self.default_char = default_char
        self.char_to_ps = defaultdict(set)
        self.p_to_char = defaultdict(lambda: self.default_char)
        self.changes = {}

    def __setitem__(self, key, value):
        self.add(value, key)

    def __getitem__(self, item):
        return self.get_char_at(item)

    def get_x_y_dist_to_foo(self, pos, foo, wrapping=False, diagonal_moving=False, default=None):
        if type(pos) == list:
            pos = tuple(pos)
        assert is_coord(pos), "pos is not a coord: %r" % pos
        assert is_char(foo), "foo is not a char: %r" % foo

        dists = []
        x, y = pos
        for foo_pos in self.get_all_pos(foo):
            foo_x, foo_y = foo_pos
            # TODO(derpferd): Implement wrapping
            if wrapping or diagonal_moving:
                # for i, j in product(range(-1, 0, 1), range(-1, 0, 1)):
                #     pass
                raise NotImplementedError("Wrapping and Diagonal_moving not implemented")
            else:
                d_x, d_y = foo_x - x, foo_y - y
                dists += [(d_x, d_y)]
        if len(dists) == 0:
            return default
        else:
            return min(dists, key=lambda d: abs(d[0]) + abs(d[1]))

    # checks if pos is in bound of the map
    def in_bounds(self, pos):
        assert is_coord(pos), "pos: '{}', isn't a coord".format(pos)
        x, y = pos
        return 0 <= x < self.w and 0 <= y < self.h

    def wrap(self, pos, wrap_x=False, wrap_y=False):
        x, y = pos
        if wrap_x:
            x %= self.w
        if wrap_y:
            y %= self.h
        return (x, y)

    # changes in the format of a dictionary
    # key: (x, y)
    # value: new_char
    def get_diff(self):
        changes = self.changes
        self.changes = {}
        return changes

    # pos must be tuple
    def add(self, char, pos):
        assert is_char(char), "'{}' isn't a char".format(char)
        assert self.in_bounds(pos), "'{}' isn't in bounds".format(pos)

        if pos in self.p_to_char.keys():
            self.rm_char(pos)
        self.char_to_ps[char].add(pos)
        self.p_to_char[pos] = char
        self.changes[pos] = char

    # pos must be tuple
    def rm_char(self, pos):
        assert self.in_bounds(pos)
        char = self.p_to_char[pos]
        del self.p_to_char[pos]
        if char in self.char_to_ps and pos in self.char_to_ps[char]:
            self.char_to_ps[char].remove(pos)
            self.changes[pos] = self.default_char

    # returns a set of pos
    def get_all_pos(self, char):
        assert is_char(char)
        return copy(self.char_to_ps[char])

    # will return default_char if the position is not set
    def get_char_at(self, pos):
        assert self.in_bounds(pos)
        return copy(self.p_to_char[pos])

    # offset should be in the format tuple(x, y)
    def shift_all(self, offset, wrap_x=False, wrap_y=False):
        assert type(offset) == tuple
        old_char_to_ps = copy(self.char_to_ps)
        self.char_to_ps = defaultdict(set)
        self.p_to_char = defaultdict(lambda: self.default_char)
        for char, ps in old_char_to_ps.items():
            for p in ps:
                if p not in self.changes:
                    self.changes[p] = self.default_char
                new_pos = self.wrap((p[0] + offset[0], p[1] + offset[1]), wrap_x, wrap_y)
                if self.in_bounds(new_pos):
                    self.add(char, new_pos)


class PanelPadding(object):
    TOP = 1
    RIGHT = 2
    LEFT = 4
    BOTTOM = 8
    DEFAULT_SIZE = 0

    def __init__(self, sides=0, size=0):
        self.sides = sides
        self.style = {self.sides: size}

    @staticmethod
    def create(top=False, bottom=False, right=False, left=False):
        paddings = [PanelPadding()]
        if type(top) == bool and top:
            paddings += [PanelPadding(PanelPadding.TOP)]
        elif type(top) == int:
            paddings += [PanelPadding(PanelPadding.TOP, top)]
        if type(bottom) == bool and bottom:
            paddings += [PanelPadding(PanelPadding.BOTTOM)]
        elif type(bottom) == int:
            paddings += [PanelPadding(PanelPadding.BOTTOM, bottom)]
        if type(right) == bool and right:
            paddings += [PanelPadding(PanelPadding.RIGHT)]
        elif type(right) == int:
            paddings += [PanelPadding(PanelPadding.RIGHT, right)]
        if type(left) == bool and left:
            paddings += [PanelPadding(PanelPadding.LEFT)]
        elif type(left) == int:
            paddings += [PanelPadding(PanelPadding.LEFT, left)]

        return reduce(lambda x, y: x | y, paddings)

    def __or__(self, other):
        assert isinstance(other, PanelPadding)
        new_padding = PanelPadding()
        new_padding.sides = other.sides | self.sides
        new_padding.style = self.style
        new_padding.style.update(other.style)
        return new_padding

    def __getitem__(self, item):
        if item in self.style:
            if self.style[item]:
                return self.style[item]
        return self.DEFAULT_SIZE

    def __contains__(self, item):
        return self.has_side(item)

    def has_side(self, side):
        return True
        # return side in self.style


class PanelBorder(object):
    TOP = 1
    RIGHT = 2
    LEFT = 4
    BOTTOM = 8
    DEFAULT_CHARS = {TOP: chr(196), BOTTOM: chr(196), RIGHT: chr(179), LEFT: chr(179),
                     TOP | RIGHT: chr(191), TOP | LEFT: chr(218), BOTTOM | RIGHT: chr(217), BOTTOM | LEFT: chr(192)}

    def __init__(self, sides=0, char=None):
        self.sides = sides
        self.style = {self.sides: char}

    @staticmethod
    def create(top=False, bottom=False, right=False, left=False, top_right=False, top_left=False, bottom_right=False,
               bottom_left=False):
        """
        Use this method for an easy way to create nice borders. Set any side to true to create a border with the default
        characters. You can also set any side to a character which will create a border with that character instead.
        In order for the corners (top_right, top_left, ...) to be rendered both of their respective sides must be set
        to True or a char.

        Ex.
        >>> PanelBorder.create(top=True)  # This will create a top border with the default char

        >>> PanelBorder.create(top='$')  # This will create a top border of '$'s.

        >>> PanelBorder.create(top='=', left='!', top_left='?')  # This will create a border looking like some thing below.
            ?====
            !
            !
        """
        borders = []
        if type(top) == bool and top:
            borders += [PanelBorder(PanelBorder.TOP)]
        elif type(top) == str:
            borders += [PanelBorder(PanelBorder.TOP, char=top)]
        if type(bottom) == bool and bottom:
            borders += [PanelBorder(PanelBorder.BOTTOM)]
        elif type(bottom) == str:
            borders += [PanelBorder(PanelBorder.BOTTOM, char=bottom)]
        if type(right) == bool and right:
            borders += [PanelBorder(PanelBorder.RIGHT)]
        elif type(right) == str:
            borders += [PanelBorder(PanelBorder.RIGHT, char=right)]
        if type(left) == bool and left:
            borders += [PanelBorder(PanelBorder.LEFT)]
        elif type(left) == str:
            borders += [PanelBorder(PanelBorder.LEFT, char=left)]
        if type(top_right) == bool and top_right:
            borders += [PanelBorder(PanelBorder.TOP | PanelBorder.RIGHT)]
        elif type(top_right) == str:
            borders += [PanelBorder(PanelBorder.TOP | PanelBorder.RIGHT, char=top_right)]
        if type(top_left) == bool and top_left:
            borders += [PanelBorder(PanelBorder.TOP | PanelBorder.LEFT)]
        elif type(top_left) == str:
            borders += [PanelBorder(PanelBorder.TOP | PanelBorder.LEFT, char=top_left)]
        if type(bottom_right) == bool and bottom_right:
            borders += [PanelBorder(PanelBorder.BOTTOM | PanelBorder.RIGHT)]
        elif type(bottom_right) == str:
            borders += [PanelBorder(PanelBorder.BOTTOM | PanelBorder.RIGHT, char=bottom_right)]
        if type(bottom_left) == bool and bottom_left:
            borders += [PanelBorder(PanelBorder.BOTTOM | PanelBorder.LEFT)]
        elif type(bottom_left) == str:
            borders += [PanelBorder(PanelBorder.BOTTOM | PanelBorder.LEFT, char=bottom_left)]

        return reduce(lambda x, y: x | y, borders)

    def __or__(self, other):
        assert isinstance(other, PanelBorder)
        new_border = PanelBorder()
        new_border.sides = other.sides | self.sides
        new_border.style = self.style
        new_border.style.update(other.style)
        return new_border

    def __getitem__(self, item):
        if item in self.style:
            if self.style[item]:
                return self.style[item]
        return self.DEFAULT_CHARS[item]

    def __contains__(self, item):
        return self.has_side(item)

    def has_side(self, side):
        return side in self.style


class Panel(Map):
    def __init__(self, x, y, w, h, background_char=DEFAULT_CHAR, border=PanelBorder(), padding=PanelPadding()):
        super(Panel, self).__init__(w, h, background_char)
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.border = border
        self.padding = padding
        self.real_y = y
        self.real_x = x
        self.real_w = w
        self.real_h = h
        if PanelBorder.TOP in self.border:
            self.real_y -= 1
            self.real_h += 1
        if PanelBorder.LEFT in self.border:
            self.real_x -= 1
            self.real_w += 1
        if PanelBorder.BOTTOM in self.border:
            self.real_h += 1
        if PanelBorder.RIGHT in self.border:
            self.real_w += 1
        if PanelPadding.TOP in self.padding:
            self.y += self.padding[PanelPadding.TOP]
            self.h -= self.padding[PanelPadding.TOP]
        if PanelPadding.LEFT in self.padding:
            self.x += self.padding[PanelPadding.LEFT]
            self.w -= self.padding[PanelPadding.LEFT]
        if PanelPadding.BOTTOM in self.padding:
            self.h -= self.padding[PanelPadding.BOTTOM]
        if PanelPadding.RIGHT in self.padding:
            self.w -= self.padding[PanelPadding.RIGHT]

    def draw_char(self, char, pos, frame_buffer):
        # TODO: add asserts for these
        x, y = pos
        assert is_char(char)
        frame_buffer.set(x, y, char)

    def redraw(self, frame_buffer):
        try:
            if PanelBorder.TOP in self.border:
                for i in range(self.real_w):
                    frame_buffer.set(self.real_x + i, self.real_y, self.border[PanelBorder.TOP])
            if PanelBorder.LEFT in self.border:
                for i in range(self.real_h):
                    frame_buffer.set(self.real_x, self.real_y + i, self.border[PanelBorder.LEFT])
            if PanelBorder.BOTTOM in self.border:
                for i in range(self.real_w):
                    frame_buffer.set(self.real_x + i, self.real_y + self.real_h - 1,
                                     self.border[PanelBorder.BOTTOM])
            if PanelBorder.RIGHT in self.border:
                for i in range(self.real_h):
                    frame_buffer.set(self.real_x + self.real_w - 1, self.real_y + i,
                                     self.border[PanelBorder.RIGHT])
            if PanelBorder.TOP in self.border and PanelBorder.LEFT in self.border:
                frame_buffer.set(self.real_x, self.real_y, self.border[PanelBorder.TOP | PanelBorder.LEFT])
            if PanelBorder.BOTTOM in self.border and PanelBorder.LEFT in self.border:
                frame_buffer.set(self.real_x, self.real_y + self.real_h - 1,
                                 self.border[PanelBorder.BOTTOM | PanelBorder.LEFT])
            if PanelBorder.TOP in self.border and PanelBorder.RIGHT in self.border:
                frame_buffer.set(self.real_x + self.real_w - 1, self.real_y,
                                 self.border[PanelBorder.TOP | PanelBorder.RIGHT])
            if PanelBorder.BOTTOM in self.border and PanelBorder.RIGHT in self.border:
                frame_buffer.set(self.real_x + self.real_w - 1, self.real_y + self.real_h - 1,
                                 self.border[PanelBorder.BOTTOM | PanelBorder.RIGHT])
        except IndexError:
            raise IndexError("Out of bounds while drawing border. This is normally caused by the forgetting that the"
                             "x,y adn width, height of a Panel doesn't include the border.")


class MapPanel(Panel):
    def __init__(self, x, y, w, h, default_char=DEFAULT_CHAR, border=PanelBorder(), padding=PanelPadding()):
        """

        Args:
            x: The x value of the position of top left corner (not including the border)
            y: The y value of the position of top left corner (not including the border)
            w: The width of the panel not including the border
            h: The height of the panel not including the border
            default_char:
            border:
            padding:
        """
        super(MapPanel, self).__init__(x, y, w, h, default_char, border, padding)
        self.is_first = True

    def first_draw(self, frame_buffer):
        # pass
        for x in range(self.w):
            for y in range(self.h):
                self.draw_char(self[(x, y)], (self.x + x, self.y + y), frame_buffer)

    def redraw(self, frame_buffer):
        super(MapPanel, self).redraw(frame_buffer)
        if self.is_first:
            self.first_draw(frame_buffer)
            self.is_first = False
        diff = self.get_diff()
        for pos in diff:
            char = diff[pos]

            # Check that the position is in bounds
            if 0 <= pos[0] < self.w and 0 <= pos[1] < self.h:
                self.draw_char(char, (self.x + pos[0], self.y + pos[1]), frame_buffer)
            else:
                raise Warning("Char out of bounds: Decided to skip drawing it!")


class MessagePanel(Panel):
    """ This panel contains messages to be displayed to the user. It acts as a scrolling text log.
        This means that the first message is display on the first line and some on till you have
        enough messages to fill the height. Then the next message added will push all the other
        messages up and the first message will be discarded.

        Example:
            A MessagePanel with height of 3. Add messages "A", "B" and "C". It will display like the following:
                A
                B
                C
            Add message "D" and it will display like the following:
                B
                C
                D

        Note:
            The following is deprecated:
            >>> m = MessagePanel()
            >>> m += ["Hi"]
            You should do this instead:
            >>> m = MessagePanel()
            >>> m.add("Hi")

    """
    def __init__(self, x, y, w, h, default_char=DEFAULT_CHAR, border=PanelBorder(),
                 padding=PanelPadding.create(*[1] * 4)):
        super(MessagePanel, self).__init__(x, y, w, h, default_char, border, padding)
        self.msgs = []
        self.rows = self.h
        self.max_len = self.w

    @deprecated("Please use the `add` method instead.")
    def __add__(self, other):
        self.add(other)
        return self

    def __getitem__(self, item):
        assert isinstance(item, int)
        return self.msgs[item]

    # TODO: Decide if this should be allowed
    # Message should act like a stack without popping only adding
    def __setitem__(self, key, value):
        assert isinstance(key, int)
        assert isinstance(value, str)
        assert "\n" not in value
        if 0 <= key < len(self.msgs):
            self.msgs[key] = value

    def __iter__(self):
        return self.msgs.__iter__()

    def __contains__(self, item):
        return item in self.msgs

    def add(self, messages):
        assert isinstance(messages, str) or hasattr(messages, '__iter__')
        if isinstance(messages, str):
            messages = [messages]
        for message in messages:
            self.msgs += message.split("\n")

    def clear(self):
        self.msgs = []

    def get_current_messages(self):
        return self.msgs[-self.rows:]

    def redraw(self, frame_buffer):
        super(MessagePanel, self).redraw(frame_buffer)
        msgs_to_display = self.get_current_messages()

        # Clear the WHOLE message panel
        for j in range(self.rows):
            # TODO: optimize this by only clearing what should be changed.
            # Clear msg row
            for i in range(self.max_len):
                frame_buffer.set(self.x + i, self.y + j, self.default_char)

        # Write the message we have to the panel
        for j in range(len(msgs_to_display)):
            msg = msgs_to_display[j]
            # Print msg
            for i in range(min(len(msg), self.max_len)):
                frame_buffer.set(self.x + i, self.y + j, msg[i])


class StatusPanel(MessagePanel):
    def __init__(self, x, y, w, h, default_char=DEFAULT_CHAR, border=PanelBorder(),
                 padding=PanelPadding().create(*[1] * 4)):
        super(StatusPanel, self).__init__(x, y, w, h, default_char, border, padding)
        self.info = {}

    def __getitem__(self, item):
        return self.info[item]

    def __setitem__(self, key, value):
        self.info[str(key)] = str(value)

    def __contains__(self, item):
        return item in self.info

    def get_current_messages(self):
        self.msgs = []
        for key in self.info:
            self.msgs += [key + ": " + self.info[key]]
        return super(StatusPanel, self).get_current_messages()
