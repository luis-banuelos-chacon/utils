from array import array
import math
import sys


class Painter(object):

    def __init__(self, width, height):
        self._width = width
        self._height = height
        self._buffer = [[None for x in range(self._width)] for y in range(self._height)]
        self._area = [0, 0, width, height]
        self._area_stack = []

    @property
    def width(self):
        return self._area[2]

    @property
    def height(self):
        return self._area[3]

    @property
    def size(self):
        return [self._area[2], self._area[3]]

    def pushArea(self, x, y, w, h):
        self._area_stack.append(self._area)
        self._area = [self._area[0] + x, self._area[1] + y, w, h]

    def popArea(self):
        self._area = self._area_stack.pop()

    def resetArea(self):
        self._area = [0, 0, self._width, self._height]

    def draw(self, x, y, v):
        x0, y0, w, h = self._area
        self._buffer[y0 + y][x0 + x] = v

    def clear(self):
        x0, y0, w, h = self._area
        for y in range(y0, y0+h):
            for x in range(x0, x0+w):
                self._buffer[y][x] = None

    def drawText(self, x, y, text):
        for i, c in enumerate(text):
            self.draw(x+i, y, c)

    def drawHorizontal(self, x, y, l, v):
        for ix in range(x + l):
            self.draw(x+ix, y, v)

    def drawVertical(self, x, y, l, v):
        for iy in range(y + l):
            self.draw(x, y+iy, v)

    def drawRectangle(self, x, y, w, h, v):
        '''Draw rectangle with value.'''
        for ix in range(x + w):
            self.draw(ix, y, v)
            self.draw(ix, y+h-1, v)

        for iy in range(y + h):
            self.draw(x, iy, v)
            self.draw(x+w-1, iy, v)

    def insert(self, ox, oy, m):
        '''Insert m into buffer at (x, y)'''
        for y, rows in enumerate(m):
            for x, data in enumerate(rows):
                self.draw(x+ox, y+oy, data)

    def print(self):
        for row in self._buffer:
            for c in row:
                if c is None:
                    sys.stdout.write(' ')
                else:
                    sys.stdout.write(c)
            sys.stdout.write('\n')


class Item(object):

    def render(self, p):
        p.drawRectangle(0, 0, p.width, p.height, '.')
        p.drawText(1, 1, 'This is me.')


class Layout(object):

    def __init__(self, direction='v', border=True, margin=0, marker='1'):
        self._direction = direction
        self._margin = margin
        self._border = border
        self._marker = marker
        self._items = []

    def addItem(self, item, weight=1):
        self._items.append((weight, item))

    def render(self, p):
        if self._direction == 'h':
            dim_a = p.width
            dim_b = p.height
        else:
            dim_b = p.width
            dim_a = p.height

        # calculate dividers
        divs = len(self._items) - 1
        div_length = (self._margin * 2) + 1

        # add border
        if self._border:
            p.drawRectangle(0, 0, p.width, p.height, self._marker)
            border = 1
        else:
            border = 0

        # indentify size distribution
        fixed_length = 0
        total_weight = 0.0
        for weight, item in self._items:
            if weight > 1.0:
                fixed_length += int(weight)
            else:
                total_weight += weight

        # total length to be distributed to content
        total_length = dim_a - (border * 2) - (self._margin * 2) - (div_length * divs) - fixed_length
        # container draw length
        draw_length = dim_b - (border * 2) - (self._margin * 2)

        # draw items
        i = self._margin + border
        for num, pair in enumerate(self._items):
            weight, item = pair
            if weight > 1.0:
                length = weight
            else:
                length = math.floor((weight / total_weight) * total_length)

            # draw
            if self._direction == 'h':
                if num != 0:
                    p.drawVertical(i-self._margin-1, 0, dim_b, self._marker)
                p.pushArea(i, self._margin + border, length, draw_length)
            else:
                if num != 0:
                    p.drawHorizontal(0, i-self._margin-1, dim_b, self._marker)
                p.pushArea(self._margin + border, i, draw_length, length)
            item.render(p)
            p.popArea()

            i += div_length + length


class Table(Item):

    def __init__(self, header, data):
        self.header = header
        self.data = data




if __name__ == '__main__':
    p = Painter(81, 21)
    panel0 = Layout(direction='v', margin=0, marker='1')
    panel1 = Layout(direction='h', margin=0, border=False, marker='2')
    panel2 = Layout(direction='v', margin=0, border=False, marker='3')
    panel0.addItem(Item())
    panel0.addItem(panel1)
    panel1.addItem(Item())
    panel1.addItem(panel2)
    panel2.addItem(Item())
    panel2.addItem(Item())
    panel0.render(p)
    p.print()
