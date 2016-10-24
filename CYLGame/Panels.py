from collections import defaultdict

DEFAULT_CHAR = ' '


# WARNING: this does not do bounds checking
# TODO: Should the map do bounds checking?
class Map(object):
    def __init__(self, default_char=DEFAULT_CHAR):
        self.char_to_ps = defaultdict(set)
        self.p_to_char = defaultdict(lambda: default_char)
        self.default_char = default_char
        self.changes = {}

    def __setitem__(self, key, value):
        self.add(value, key)

    def __getitem__(self, item):
        return self.get_char_at(item)

    # changes in the format of a dictionary
    # key: (x, y)
    # value: new_char
    def get_diff(self):
        changes = self.changes
        self.changes = {}
        return changes

    # pos must be tuple
    def add(self, char, pos):
        assert type(pos) == tuple
        if pos in self.p_to_char.keys():
            self.rm_char(pos)
        self.char_to_ps[char].add(pos)
        self.p_to_char[pos] = char
        self.changes[pos] = char

    # pos must be tuple
    def rm_char(self, pos):
        assert type(pos) == tuple
        char = self.p_to_char[pos]
        del self.p_to_char[pos]
        if char in self.char_to_ps and pos in self.char_to_ps[char]:
            self.char_to_ps[char].remove(pos)
            self.changes[pos] = self.default_char

    # returns a set of pos
    def get_all_pos(self, char):
        return self.char_to_ps[char]

    # will return default_char if the position is not set
    def get_char_at(self, pos):
        return self.p_to_char[pos]


class PanelBorder(object):
    TOP = 1
    RIGHT = 2
    LEFT = 4
    BOTTOM = 8
    DEFAULT_CHARS = {TOP: chr(196), BOTTOM: chr(196), RIGHT: chr(179), LEFT: chr(179),
                     TOP | RIGHT: chr(191), TOP | LEFT: chr(218), BOTTOM | RIGHT: chr(217), BOTTOM | LEFT: chr(192)}

    def __init__(self, sides=0, char=None):
        self.sides = sides
        self.char = char
        self.style = {self.sides: self.char}

    def __or__(self, other):
        assert isinstance(other, PanelBorder)
        # make sure the sides aren't over lapping
        assert other.sides & self.sides == 0
        new_border = PanelBorder()
        new_border.style = self.style
        new_border.style.update(other.style)

    def __getitem__(self, item):
        if self.char:
            return self.char
        else:
            return self.DEFAULT_CHARS[item]

    def __contains__(self, item):
        return self.has_side(item)

    def has_side(self, side):
        result = False
        for sides in self.style:
            if sides & side:
                result = True
                break
        return result


class Panel(Map):
    def __init__(self, x, y, w, h, background_char=DEFAULT_CHAR, border=PanelBorder()):
        super(Panel, self).__init__(background_char)
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.border = border
        self.real_y = y
        self.real_x = x
        self.real_w = w
        self.real_h = h
        if PanelBorder.TOP in self.border:
            self.real_y = self.y
            self.y += 1
            self.h -= 1
        if PanelBorder.LEFT in self.border:
            self.real_x = self.x
            self.x += 1
            self.w -= 1
        if PanelBorder.BOTTOM in self.border:
            self.real_h = self.h
            self.h -= 1
        if PanelBorder.RIGHT in self.border:
            self.real_w = self.w
            self.w -= 1

    def redraw(self, libtcod, console):
        if PanelBorder.TOP in self.border:
            for i in range(self.real_w):
                libtcod.console_put_char(console, self.real_x + i, self.real_y, self.border[PanelBorder.TOP],
                                         libtcod.BKGND_NONE)
        if PanelBorder.LEFT in self.border:
            for i in range(self.real_h):
                libtcod.console_put_char(console, self.real_x, self.real_y + i, self.border[PanelBorder.LEFT],
                                         libtcod.BKGND_NONE)
        if PanelBorder.BOTTOM in self.border:
            for i in range(self.real_w):
                libtcod.console_put_char(console, self.real_x + i, self.y + self.h, self.border[PanelBorder.BOTTOM],
                                         libtcod.BKGND_NONE)
        if PanelBorder.BOTTOM in self.border:
            for i in range(self.real_h):
                libtcod.console_put_char(console, self.x + self.w, self.real_y + i, self.border[PanelBorder.RIGHT],
                                         libtcod.BKGND_NONE)
        if PanelBorder.TOP in self.border and PanelBorder.LEFT in self.border:
            libtcod.console_put_char(console, self.real_x, self.real_y, self.border[PanelBorder.TOP | PanelBorder.LEFT],
                                     libtcod.BKGND_NONE)
        if PanelBorder.BOTTOM in self.border and PanelBorder.LEFT in self.border:
            libtcod.console_put_char(console, self.real_x, self.real_y + self.real_h, self.border[PanelBorder.BOTTOM | PanelBorder.LEFT],
                                     libtcod.BKGND_NONE)
        if PanelBorder.TOP in self.border and PanelBorder.RIGHT in self.border:
            libtcod.console_put_char(console, self.real_x + self.real_w, self.real_y, self.border[PanelBorder.TOP | PanelBorder.RIGHT],
                                     libtcod.BKGND_NONE)
        if PanelBorder.BOTTOM in self.border and PanelBorder.RIGHT in self.border:
            libtcod.console_put_char(console, self.real_x + self.real_w, self.real_y + self.real_h, self.border[PanelBorder.BOTTOM | PanelBorder.RIGHT],
                                     libtcod.BKGND_NONE)


class MapPanel(Panel):
    def __init__(self, x, y, w, h, default_char=DEFAULT_CHAR, border=PanelBorder()):
        super(MapPanel, self).__init__(x, y, w, h, default_char, border)

    def redraw(self, libtcod, console):
        super(MapPanel, self).redraw(libtcod, console)
        diff = self.get_diff()
        for pos in diff:
            char = diff[pos]
            # Check that the position is in bounds
            if 0 <= pos[0] < self.w and 0 <= pos[1] < self.h:
                libtcod.console_put_char(console, self.x + pos[0], self.y + pos[1], char, libtcod.BKGND_NONE)
            else:
                raise Warning("Char out of bounds: Decided to skip drawing it!")


class MessagePanel(Panel):
    def __init__(self, x, y, w, h, default_char=DEFAULT_CHAR, border=PanelBorder()):
        super(MessagePanel, self).__init__(x, y, w, h, default_char, border)
        self.msgs = []
        self.rows = self.h - 2
        self.max_len = self.w - 2

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

    def redraw(self, libtcod, console):
        super(MessagePanel, self).redraw(libtcod, console)
        msgs_to_display = self.get_current_messages()
        for j in range(len(msgs_to_display)):
            msg = msgs_to_display[j]
            # TODO: optimize this
            # Clear msg board
            for i in range(self.max_len):
                libtcod.console_put_char(console, self.x + 1 + i, self.y + 1 + j, self.default_char)
            # Print msg
            for i in range(min(len(msg), self.max_len)):
                libtcod.console_put_char(console, self.x + 1 + i, self.y + 1 + j, msg[i])


class StatusPanel(MessagePanel):
    def __init__(self, x, y, w, h, default_char=DEFAULT_CHAR, border=PanelBorder()):
        super(StatusPanel, self).__init__(x, y, w, h, default_char, border)
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
