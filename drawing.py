from copy import deepcopy
import math
import time
import sys


class Painter(object):

    cmap = {
        # key definition
        # (up, down, left)

        # SINGLES
        # straights
        (0, 0, 1, 1): '─', (1, 1, 0, 0): '│',
        # corners
        (0, 1, 0, 1): '┌', (0, 1, 1, 0): '┐', (1, 0, 0, 1): '└', (1, 0, 1, 0): '┘',
        # intersections
        (1, 1, 0, 1): '├', (1, 1, 1, 0): '┤', (0, 1, 1, 1): '┬', (1, 0, 1, 1): '┴', (1, 1, 1, 1): '┼',
        # ends
        (1, 0, 0, 0): '┴', (0, 1, 0, 0): '┬', (0, 0, 1, 0): '┤', (0, 0, 0, 1): '├',

        # DOUBLES
        # straights
        (0, 0, 2, 2): '═', (2, 2, 0, 0): '║',
        # corners
        (0, 2, 0, 2): '╔', (0, 2, 2, 0): '╗', (2, 0, 0, 2): '╚', (2, 0, 2, 0): '╝',
        # intersections
        (2, 2, 0, 2): '╠', (2, 2, 2, 0): '╣', (0, 2, 2, 2): '╦', (2, 0, 2, 2): '╩', (2, 2, 2, 2): '╬',
        # ends
        (2, 0, 0, 0): '╨', (0, 2, 0, 0): '╥', (0, 0, 2, 0): '╡', (0, 0, 0, 2): '╞',

        # INTERSECTION TRANSITION
        (0, 1, 0, 2): '╒', (0, 2, 0, 1): '╓', (0, 1, 2, 0): '╕', (0, 2, 1, 0): '╖', (1, 0, 0, 2): '╘',
        (2, 0, 0, 1): '╙', (1, 0, 2, 0): '╛', (2, 0, 1, 0): '╜', (1, 1, 0, 2): '╞', (2, 2, 0, 1): '╟',
        (1, 1, 2, 0): '╡', (2, 2, 1, 0): '╢', (0, 1, 2, 2): '╤', (0, 2, 1, 1): '╥', (1, 0, 2, 2): '╧',
        (2, 0, 1, 1): '╨', (1, 1, 2, 2): '╪', (2, 2, 1, 1): '╫',
    }

    def __init__(self, width, height, stream=sys.stdout):
        self._width = width
        self._height = height
        self._stream = stream
        self._buffer = [[None for x in range(self._width)] for y in range(self._height)]
        self._area = [0, 0, width, height]
        self._area_stack = []

    ##
    # Drawing Area
    ##

    @property
    def width(self):
        '''Effective drawing width.'''
        return self._area[2]

    @property
    def height(self):
        '''Effective drawing height.'''
        return self._area[3]

    @property
    def size(self):
        '''Effective drawing size.'''
        return [self._area[2], self._area[3]]

    def pushArea(self, x, y, w, h):
        self._area_stack.append(self._area)
        self._area = [self._area[0] + x, self._area[1] + y, w, h]

    def popArea(self):
        self._area = self._area_stack.pop()

    def resetArea(self):
        self._area = [0, 0, self._width, self._height]

    ##
    # Painting Methods
    ##

    def clear(self):
        x0, y0, w, h = self._area
        for y in range(y0, y0+h):
            for x in range(x0, x0+w):
                self._buffer[y][x] = None

    def set(self, x, y, v):
        x0, y0, w, h = self._area
        self._buffer[y0 + y][x0 + x] = v

    def get(self, x, y):
        x0, y0, w, h = self._area
        if (0 <= x < w) and (0 <= y < h):
            return self._buffer[y0 + y][x0 + x]

    def drawText(self, x, y, text):
        for i, c in enumerate(text):
            self.set(x+i, y, c)

    def drawHorizontal(self, x, y, l, v):
        for ix in range(x + l):
            self.set(x+ix, y, v)

    def drawVertical(self, x, y, l, v):
        for iy in range(y + l):
            self.set(x, y+iy, v)

    def drawRectangle(self, x, y, w, h, v):
        '''Draw rectangle with value.'''
        for ix in range(x + w):
            self.set(ix, y, v)
            self.set(ix, y+h-1, v)

        for iy in range(y + h):
            self.set(x, iy, v)
            self.set(x+w-1, iy, v)

    def insert(self, ox, oy, m):
        '''Insert m into buffer at (x, y)'''
        for y, rows in enumerate(m):
            for x, data in enumerate(rows):
                self.set(x+ox, y+oy, data)

    ##
    # Post Processing
    ##

    def boxify(self):
        x0, y0, w, h = self._area
        out = deepcopy(self._buffer)
        for y in range(h):
            for x in range(w):
                # if this is a marker
                if self._getMarker(x, y):
                    key = []
                    count = 0
                    points = ((x, y-1), (x, y+1), (x-1, y), (x+1, y))
                    for point in points:
                        marker = self._getMarker(*point)
                        count += marker != 0
                        key.append(marker)

                    # key error means symbol is adjacent to intersection
                    try:
                        out[y0+y][x0+x] = self.cmap[tuple(key)]
                    except KeyError:
                        pass

                    # if intersection, insert adjacent symbols
                    if count > 2:
                        if key[0]:
                            out[y0+y-1][x0+x] = self.cmap[(key[0], key[0], 0, 0)]
                        if key[1]:
                            out[y0+y+1][x0+x] = self.cmap[(key[1], key[1], 0, 0)]
                        if key[2]:
                            out[y0+y][x0+x-1] = self.cmap[(0, 0, key[2], key[2])]
                        if key[3]:
                            out[y0+y][x0+x+1] = self.cmap[(0, 0, key[3], key[3])]

        self._buffer = out

    def _getMarker(self, x, y):
        marker = self.get(x, y)
        if isinstance(marker, int):
            return marker
        return 0

    ##
    # Printing on Stream
    ##

    def print(self, overdraw=False):
        if overdraw:
            self._return()
        for i, row in enumerate(self._buffer):
            for c in row:
                if c is None:
                    sys.stdout.write(' ')
                else:
                    sys.stdout.write(str(c))
            if i < len(self._buffer):
                sys.stdout.write('\n')

    def _return(self):
        self._stream.write('\033[F' * len(self._buffer))


class Item(object):

    def render(self, p):
        p.drawRectangle(0, 0, p.width, p.height, ' ')


class Layout(object):

    def __init__(self, direction='v', border='2', divider='1'):
        self._direction = direction     # layout direction
        self._divider = divider         # divider marker
        self._border = border           # border marker
        self._items = []                # item list

    def addItem(self, item, weight=1):
        self._items.append((weight, item))

    def render(self, p):
        # draw border and reduce area
        if self._border:
            p.drawRectangle(0, 0, p.width, p.height, self._border)
            p.pushArea(1, 1, p.width-2, p.height-2)

        if self._direction == 'v':
            # get distribution
            dist = self._lengthDistribution(p.height)

            # draw dividers and items
            y = 0
            for i, pair in enumerate(self._items):
                w, item = pair

                if (i > 0) and self._divider:
                    p.drawHorizontal(0, y, p.width, self._divider)
                    y += 1

                p.pushArea(0, y, p.width, dist[i])
                item.render(p)
                p.popArea()

                y += dist[i]

        else:
            # get distribution
            dist = self._lengthDistribution(p.width)

            # draw dividers and items
            x = 0
            for i, pair in enumerate(self._items):
                w, item = pair

                if (i > 0) and self._divider:
                    p.drawVertical(x, 0, p.height, self._divider)
                    x += 1

                p.pushArea(x, 0, dist[i], p.height)
                item.render(p)
                p.popArea()

                x += dist[i]

        # pop to border and boxify
        if self._border:
            p.popArea()
            p.boxify()

    def _lengthDistribution(self, length):
        '''Distributes length across items.'''
        # count dividers
        dividers = (len(self._items) - 1) * (self._divider is not None)
        # total fixed length
        fixed_length = sum([w for w, i in self._items if w > 1.0])
        # total weight
        total_weight = sum([w for w, i in self._items if w <= 1.0])
        # total distributable length is drawable area - dividers - fixed length
        total_length = length - dividers - fixed_length
        # generate length list
        lengths = []
        for weight, item in self._items:
            if weight > 1.0:
                lengths.append(int(weight))
            else:
                lengths.append(int((weight / total_weight) * total_length))
        # compensate for fractional error
        if sum(lengths) < total_length:
            lengths[-1] += 1
        # return list
        return lengths


if __name__ == '__main__':
    p = Painter(60, 21)
    # Layout(direction, border, divider)
    panel0 = Layout('v', 2, 1)
    panel1 = Layout('h', 0, 1)
    panel2 = Layout('v', 2, 1)
    panel0.addItem(Item())
    panel0.addItem(panel1)
    panel1.addItem(Item())
    panel1.addItem(panel2)
    panel2.addItem(Item())
    panel2.addItem(Item())
    panel0.render(p)
    p.print(False)
