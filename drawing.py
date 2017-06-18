import json
import math
import sys


SINGLE = 1
DOUBLE = 2
DASHED = 3


class Painter(object):

    cmap = {
        # key definition
        # (up, down, left)

        # SINGLES
        # straights
        (0, 0, 1, 1): '─', (1, 1, 0, 0): '│', (0, 0, 0, 0): '│',
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

        # DASHED (progress bar only)
        # straights
        (0, 0, 3, 3): '╌', (0, 0, 1, 3): '╌', (0, 0, 3, 1): '╌',
        # transition
        (1, 1, 0, 3): '├', (1, 1, 3, 0): '┤',
        (2, 2, 0, 3): '╟', (2, 2, 3, 0): '╢',
        # ends
        (0, 0, 3, 0): '┤', (0, 0, 0, 3): '├',


        # INTERSECTION TRANSITION
        (0, 1, 0, 2): '╒', (0, 2, 0, 1): '╓', (0, 1, 2, 0): '╕', (0, 2, 1, 0): '╖', (1, 0, 0, 2): '╘',
        (2, 0, 0, 1): '╙', (1, 0, 2, 0): '╛', (2, 0, 1, 0): '╜',

        (1, 1, 0, 2): '╞', (2, 2, 0, 1): '╟', (1, 1, 2, 0): '╡', (2, 2, 1, 0): '╢', (0, 1, 2, 2): '╤',
        (0, 2, 1, 1): '╥', (1, 0, 2, 2): '╧', (2, 0, 1, 1): '╨',

        (1, 1, 2, 2): '╪', (2, 2, 1, 1): '╫',
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
        x, y = int(x), int(y)
        x0, y0, w, h = self._area
        if (0 <= x < w) and (0 <= y < h):
            self._buffer[y0 + y][x0 + x] = v

    def get(self, x, y):
        x, y = int(x), int(y)
        x0, y0, w, h = self._area
        if (0 <= x < w) and (0 <= y < h):
            return self._buffer[y0 + y][x0 + x]

    def drawText(self, x, y, text, anchor='<'):
        # spacers
        for c in text:
            pass
        if anchor == '>':
            x = x - len(text)
        if anchor == '^':
            x = x - (len(text) / 2)

        for i, c in enumerate(text):
            if c != '\0':
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
        out = json.loads(json.dumps(self._buffer))  # faster than deepcopy
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

    def __init__(self, border=None, margin=None, min_width=None, min_height=None):
        '''Base drawable item
        Arguments:
            - border: symbol to draw borders
            - margin: margin size
        '''
        self.border = border
        self.margin = margin
        # text in borders
        self.tl = None
        self.tc = None
        self.tr = None
        self.bl = None
        self.bc = None
        self.br = None

    def preRender(self, p):
        if self.border:
            p.drawRectangle(0, 0, p.width, p.height, self.border)
            if self.tl:
                p.drawText(2, 0, self.tl, '<')
            if self.tc:
                p.drawText(p.width/2, 0, self.tc, '^')
            if self.tr:
                p.drawText(p.width-2, 0, self.tr, '>')
            if self.bl:
                p.drawText(2, p.height-1, self.bl, '<')
            if self.bc:
                p.drawText(p.width/2, p.height-1, self.bc, '^')
            if self.br:
                p.drawText(p.width-2, p.height-1, self.br, '>')
            p.pushArea(1, 1, p.width-2, p.height-2)

        if self.margin:
            p.pushArea(self.margin, self.margin, p.width-(self.margin*2), p.height-(self.margin*2))

    def postRender(self, p):
        if self.margin:
            p.popArea()

        if self.border:
            p.popArea()
            p.boxify()

    def render(self, p):
        self.preRender(p)
        self.postRender(p)


class Formatter(Item):

    def __init__(self, data=None, ha='<', va='', pad='', prec=3, *args, **kwargs):
        '''Text formatting
        Arguments:
            - ha: horizontal alignemnt (<, ^, >)
            - va: vertical alignment (_, -, ^)
        '''
        super().__init__(*args, **kwargs)
        self.data = data
        self.prec = prec
        self.pad = pad
        self.ha = ha
        self.va = va

    def render(self, p):
        self.preRender(p)
        # vertical alignment
        if self.va == '-':
            y = int(p.height / 2)
        elif self.va == '_':
            y = p.height - 1
        else:
            y = 0

        if isinstance(self.data, str):
            if len(self.data) > p.width:
                chunks = [self.data[i:i+p.width] for i in range(0, len(self.data), p.width)]
                if self.va == '_':
                    y -= len(chunks) - 1
                for chunk in chunks:
                    p.drawText(0, y, '{:{pad}{align}{width}}'.format(chunk, pad=self.pad, align=self.ha, width=p.width))
                    y += 1
            else:
                p.drawText(0, y, '{:{pad}{align}{width}}'.format(self.data, pad=self.pad, align=self.ha, width=p.width))

        elif isinstance(self.data, list):
            if self.va == '_':
                y -= len(self.data) - 1
            for item in self.data:
                p.drawText(0, y, '{:{pad}{align}{width}}'.format(item, pad=self.pad, align=self.ha, width=p.width))
                y += 1

        elif isinstance(self.data, int):
            p.drawText(0, y, '{:{pad}{align}{width}}'.format(self.data, pad=self.pad, align=self.ha, width=p.width))

        elif isinstance(self.data, float):
            if self.prec is None:
                self.prec = p.width
            p.drawText(0, y, '{:{pad}{align}{width}.{prec}f}'.format(self.data, pad=self.pad, align=self.ha, width=p.width, prec=self.prec))

        self.postRender(p)


class ProgressBar(Item):

    def __init__(self, progress=0.0, total=1.0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.progress = progress
        self.total = total

    def render(self, p):
        self.preRender(p)
        prog_x = int(p.width * (self.progress / self.total))
        for x in range(p.width):
            if x > prog_x:
                p.set(x, 0, DASHED)
            else:
                p.set(x, 0, SINGLE)
        p.boxify()
        self.postRender(p)


class Layout(Item):

    def __init__(self, direction='v', divider=1, border=1, *args, **kwargs):
        '''Layout multiple items
        Arguments:
            - direction: which direction to layout items
            - divider: symbol to draw dividers
        '''
        super().__init__(border=border, *args, **kwargs)
        self.direction = direction      # layout direction
        self.divider = divider          # divider marker
        self.items = []                 # item list

    def addItem(self, item, weight=1):
        self.items.append((weight, item))

    def render(self, p):
        self.preRender(p)

        if self.direction == 'v':
            # get distribution
            dist = self._lengthDistribution(p.height)

            # draw dividers and items
            y = 0
            for i, pair in enumerate(self.items):
                w, item = pair

                if (i > 0) and self.divider:
                    p.drawHorizontal(0, y, p.width, self.divider)
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
            for i, pair in enumerate(self.items):
                w, item = pair

                if (i > 0) and self.divider:
                    p.drawVertical(x, 0, p.height, self.divider)
                    x += 1

                p.pushArea(x, 0, dist[i], p.height)
                item.render(p)
                p.popArea()

                x += dist[i]

        self.postRender(p)

    def _lengthDistribution(self, length):
        '''Distributes length across items.'''
        # count dividers
        dividers = (len(self.items) - 1) * (self.divider is not None)
        # total fixed length
        fixed_length = sum([math.floor(w) for w, i in self.items if w > 1.0])
        # total weight
        total_weight = sum([w for w, i in self.items if w <= 1.0])
        # total distributable length is drawable area - dividers - fixed length
        total_length = length - dividers - fixed_length
        # generate length list
        lengths = []
        for weight, item in self.items:
            if weight > 1.0:
                lengths.append(int(weight))
            else:
                lengths.append(int((weight / total_weight) * total_length))
        # compensate for fractional error
        if sum(lengths) < total_length:
            lengths[-1] += 1
        # return list
        return lengths


class Table(Layout):

    def __init__(self, headers=[], data=[[]], weights=None, ha=None, da=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.headers = headers
        self.weights = weights
        self.data = data
        self.ha = ha            # header alignment
        self.da = da            # data alignment

    def render(self, p):
        # reset items
        self.items = []

        # headers
        header = Layout(direction='h', divider=None, border=None, margin=None)
        for i, data in enumerate(self.headers):
            #
            if self.ha:
                if isinstance(self.ha, str):
                    item = self.asItem(data, self.ha)
                elif isinstance(self.ha, list) or isinstance(self.ha, tuple):
                    item = self.asItem(data, self.ha[i])
            else:
                item = self.asItem(data)

            if self.weights:
                header.addItem(item, self.weights[i])
            else:
                header.addItem(item)

        self.addItem(header, 1.1)

        # data
        rows = Layout(direction='v', divider=None, border=None, margin=None)
        for data_row in self.data:
            row = Layout(direction='h', divider=None, border=None, margin=None)
            for i, data in enumerate(data_row):
                if self.da:
                    if isinstance(self.da, str):
                        item = self.asItem(data, self.da)
                    elif isinstance(self.da, list) or isinstance(self.da, tuple):
                        item = self.asItem(data, self.da[i])
                else:
                    item = self.asItem(data)

                if self.weights:
                    row.addItem(item, self.weights[i])
                else:
                    row.addItem(item)

            rows.addItem(row, 1.1)
        self.addItem(rows)

        super().render(p)

    def asItem(self, data, ha='<'):
        '''Returns item and weight.'''
        if issubclass(data.__class__, Item):
            return data
        else:
            return Formatter(data, ha)
