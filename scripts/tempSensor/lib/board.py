# -*- coding: utf-8-*- # Encoding cookie added by Mu Editor

"""Board -- an n-dimensional board with support for iteration, containership and slicing

Boards can have any number of dimensions, any of which can be infinite. Boards
can be sliced [:1, :2], returning a linked-copy, or copied (.copy), returning a
snapshot copy.

Boards can be iterated over for coordinates or data (.iterdata). There are also
convenience functions to determine neighbours across all dimensions (.neighbours),
the bounding box of occupied data (.occupied), all the coordinates in a space
in n-dimensions (.itercoords) and others.
"""

# testing
#
# The semantics of 3.x range are broadly equivalent
# to xrange in 2.7
#
try:
    range = xrange
except NameError:
    pass
try:
    long
except NameError:
    long = int

import os, sys
import functools
import itertools
import io

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    Image = None

class _Infinity(int):

    def __new__(meta):
        return sys.maxsize

    def __str__(self):
        return "Infinity"

    def __repr__(self):
        return "<Infinity>"

    def __eq__(self, other):
        return other == self.size

    def __lt__(self, other):
        return False

    def __gt__(self, other):
        return True

Infinity = _Infinity()

class _Empty(object):

    def __repr__(self):
        return "<Empty>"

    def __bool__(self):
        return False
    __nonzero__ = __bool__

Empty = _Empty()

class BaseDimension(object):

    def __repr__(self):
        return "<{}>".format(self.__class__.__name__)

class Dimension(BaseDimension):

    is_finite = True
    is_infinite = False

    def __init__(self, size):
        self._size = size
        self._range = range(size)

    def __iter__(self):
        return iter(self._range)

    def __eq__(self, other):
        return isinstance(self, type(other)) and self._size == other._size

    def __repr__(self):
        return "<{}: {}>".format(self.__class__.__name__, self._size)

    def __len__(self):
        return self._size

    def __contains__(self, item):
        return item in self._range

    def __getitem__(self, item):
        if isinstance(item, (int, long)):
            return self._range[item]
        elif isinstance(item, slice):
            return self._range[item.start, item.stop, item.step]
        else:
            raise TypeError("{} can only be indexed by int or slice".format(self.__class__.__name__))

class _InfiniteDimension(BaseDimension):

    chunk_size = 10
    is_finite = False
    is_infinite = True

    def __iter__(self):
        return itertools.count()

    def __repr__(self):
        return "<Infinite Dimension>"

    def __eq__(self, other):
        #
        # Ensure that any infinite dimension is equal to any other
        #
        return isinstance(other, self.__class__)

    def __contains__(self, item):
        #
        # An infinite dimension includes any non-negative coordinate
        #
        if item < 0:
            return False
        return True

    def __len__(self):
        return Infinity

    def __getitem__(self, item):
        if isinstance(item, (int, long)):
            if item == 0:
                return 0
            elif item == -1:
                return Infinity
            else:
                raise IndexError("Infinite dimensions can only return first & last items")

        elif isinstance(item, slice):
            #
            # If the request is for an open-ended slice,
            # just return the same infinite dimension.
            #
            if item.stop is None:
                return self
            else:
                return range(*item.indices(item.stop))

        else:
            raise TypeError("{} can only be indexed by int or slice".format(self.__class__.__name__))

InfiniteDimension = _InfiniteDimension()

def _centred_coord(outer_size, inner_size):
    """Given an outer and an inner size, calculate the top-left coordinates
    which the inner image should position at to be centred within the outer
    image
    """
    outer_w, outer_h = outer_size
    inner_w, inner_h = inner_size
    return round((outer_w - inner_w) / 2), round((outer_h - inner_h) / 2)


def text_sprite(font_name="arial", colour="#0000ff"):
    """Text sprite generator callback from Board.paint

    Convert the object to text of approximately the right size for
    the cell being painted. Typically this will be used for one or
    two letter objects, but it will work for any object which can
    meaningfully be converted to text
    """

    def _text_sprite(obj, size):
        #
        # Very roughly, one point is three quarters of
        # a pixel. We pick a point size which will fill
        # the smaller edge of the cell (if it's not square)
        #
        point_size = round(min(size) * 0.75)

        #
        # Create a new transparent image to hold the
        # text. Draw the text into it in blue, centred,
        # using the font requested, and return the resulting image
        #
        image = Image.new("RGBA", size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype("%s.ttf" % font_name, point_size)
        text = str(obj)
        draw.text(_centred_coord(size, font.getsize(text)), text, font=font, fill=colour)
        return image

    return _text_sprite

def imagefile_sprite(directory=".", extension=".png"):
    """Image sprite generator callback for Board.paint

    Given the text form of an object, look for an image file in the
    stated directory [default: current] and return it, scaled to size.
    """

    def _imagefile_sprite(obj, size):
        image = Image.open(os.path.join(directory, "%s%s" % (obj, extension)))
        image.thumbnail(size)
        return image

    return _imagefile_sprite

class Board(object):
    """Board - represent a board of n dimensions, each possibly infinite.

    A location on the board is represented as an n-dimensional
    coordinate, matching the dimensionality originally specified.

    The board is addressed by index with a coordinate:

    b = Board((4, 4))
    b[2, 2] = "*"
    b.draw()
    """

    class BoardError(Exception): pass
    class InvalidDimensionsError(BoardError): pass
    class OutOfBoundsError(BoardError): pass

    def __init__(self, dimension_sizes, _global_board=None, _offset_from_global=None):
        """Set up a n-dimensional board
        """
        if not dimension_sizes:
            raise self.InvalidDimensionsError("The board must have at least one dimension")
        try:
            iter(dimension_sizes)
        except TypeError:
            raise self.InvalidDimensionsError("Dimensions must be iterable (eg a tuple), not {}".format(type(dimension_sizes).__name__))
        if any(d <= 0 for d in dimension_sizes):
            raise self.InvalidDimensionsError("Each dimension must be >= 1")
        self.dimensions = [InfiniteDimension if size == Infinity else Dimension(size) for size in dimension_sizes]

        #
        # This can be a sub-board of another board: a slice.
        # If that's the case, the boards share a common data structure
        # and this one is offset from the other.
        # NB this means that if a slice is taken of a slice, the offset must itself be offset!
        #
        self._data = {} if _global_board is None else _global_board
        self._offset_from_global = _offset_from_global or tuple(0 for _ in self.dimensions)
        self._sprite_cache = {}

    def __repr__(self):
        return "<{} ({})>".format(
            self.__class__.__name__,
            ", ".join(("Infinity" if d.is_infinite else str(len(d))) for d in self.dimensions)
        )

    def __eq__(self, other):
        return \
            self.dimensions == other.dimensions and \
            dict(self.iterdata()) == dict(other.iterdata())

    def __len__(self):
        #
        # Return the total number of positions on the board. If any of
        # the dimensions is infinite, the total will be Infinity
        #
        if any(d.is_infinite for d in self.dimensions):
            return Infinity
        else:
            return functools.reduce(lambda a, b: a * b, (len(d) for d in self.dimensions))

    def __bool__(self):
        return any(coord for coord in self._data if self._is_in_bounds(coord))
    __nonzero__ = __bool__

    @property
    def is_offset(self):
        """Is this board offset from a different board?"""
        return any(o for o in self._offset_from_global)

    @property
    def has_finite_dimensions(self):
        """Does this board have at least one finite dimension?"""
        return any(d.is_finite for d in self.dimensions)

    @property
    def has_infinite_dimensions(self):
        """Does this board have at least one infinite dimension?"""
        return any(d.is_infinite for d in self.dimensions)

    def dumped(self):
        is_offset = any(o for o in self._offset_from_global)
        if is_offset:
            offset = " offset by {}".format(self._offset_from_global)
        else:
            offset = ""
        yield repr(self) + offset
        yield "{"
        for coord, value in sorted(self.iterdata()):
            if is_offset:
                global_coord = " => {}".format(self._to_global(coord))
            else:
                global_coord = ""
            data = " [{}]".format(self[coord] if self[coord] is not None else "")
            yield "  {}{}{}".format(coord, global_coord, data)
        yield "}"

    def dump(self, outf=sys.stdout):
        for line in self.dumped():
            outf.write(line + "\n")

    def _is_in_bounds(self, coord):
        """Is a given coordinate within the space of this board?
        """
        if len(coord) != len(self.dimensions):
            raise self.InvalidDimensionsError(
                "Coordinate {} has {} dimensions; the board has {}".format(coord, len(coord), len(self.dimensions)))

        return all(c in d for (c, d) in zip(coord, self.dimensions))

    def _check_in_bounds(self, coord):
        """If a given coordinate is not within the space of this baord, raise
        an OutOfBoundsError
        """
        if not self._is_in_bounds(coord):
            raise self.OutOfBoundsError("{} is out of bounds for {}".format(coord, self))

    def __contains__(self, coord):
        """Implement <coord> in <board>
        """
        return self._is_in_bounds(coord)

    def __iter__(self):
        """Implement for <coord> in <board>

        Iterate over all combinations of coordinates. If you need data,
        use iterdata().
        """
        # If all the dimensions are finite (the simplest and most common
        # situation) just use itertools.product.

        # If any dimension is infinite, we can't use itertools.product
        # directly because it consumes its arguments in order to make
        # up the axes for its Cartesian join. Instead, we chunk through
        # any infinite dimensions, while repeating the finite ones.
        if any(d.is_infinite for d in self.dimensions):
            start, chunk = 0, InfiniteDimension.chunk_size
            while True:
                iterators = [d[start:start+chunk] if d[-1] == Infinity else iter(d) for d in self.dimensions]
                for coord in itertools.product(*iterators):
                    yield coord
                start += chunk
        else:
            for coord in itertools.product(*self.dimensions):
                yield coord

    def _to_global(self, coord):
        return tuple(c + o for (c, o) in zip(coord, self._offset_from_global))

    def _from_global(self, coord):
        return tuple(c - o for (c, o) in zip(coord, self._offset_from_global))

    def iterdata(self):
        """Implement: for (<coord>, <data>) in <board>

        Generate the list of data in local coordinate terms.
        """
        for gcoord, value in self._data.items():
            lcoord = self._from_global(gcoord)
            if self._is_in_bounds(lcoord):
                yield lcoord, value

    def lendata(self):
        """Return the number of data items populated
        """
        return sum(1 for _ in self.iterdata())

    def iterline(self, coord, vector, max_steps=None):
        """Generate coordinates starting at the given one and moving
        in the direction of the vector until the edge of the board is
        reached. The initial coordinate must be on the board. The vector
        must have the same dimensionality as the coordinate.

        NB the vector can specify a "step", eg it could be (1, 2)
        """
        self._check_in_bounds(coord)
        if len(vector) != len(coord):
            raise InvalidDimensionsError()

        n_steps = 0
        while self._is_in_bounds(coord):
            yield coord
            n_steps += 1
            if max_steps is not None and n_steps == max_steps:
                break
            coord = tuple(c + v for (c, v) in zip(coord, vector))

    def iterlinedata(self, coord, vector, max_steps=None):
        """Use .iterline to generate the data starting at the given
        coordinate and moving in the direction of the vector until
        the edge of the board is reached or the maximum number of
        steps has been taken (if specified).

        This could be used, eg, to see whether you have a battleship
        or a word in a word-search
        """
        for coord in self.iterline(coord, vector, max_steps):
            yield self[coord]

    def corners(self):
        dimension_bounds = [(0, len(d) -1 if d.is_finite else Infinity) for d in self.dimensions]
        return list(itertools.product(*dimension_bounds))

    def copy(self, with_data=True):
        """Return a new board with the same dimensionality as the present one.
        If with_data is truthy, populate with the current data.

        NB this creates a copy, not a reference. For linked copy of the board,
        use __getitem__, eg b2 = b1[:, :, :]
        """
        board = self.__class__(tuple(len(d) for d in self.dimensions))
        if with_data:
            for coord, value in self.iterdata():
                board._data[coord] = value
        return board

    def clear(self):
        """Clear the data which belongs to this board, possibly a sub-board
        of a larger board.
        """
        for lcoord, value in list(self.iterdata()):
            del self._data[self._to_global(lcoord)]

    def __getitem__(self, item):
        """The item is either a tuple of numbers, representing a single
        coordinate on the board, or a tuple of slices representing a copy
        of some or all of the board.
        """
        if all(isinstance(i, (int, long)) for i in item):
            coord = self._normalised_coord(item)
            return self._data.get(coord, Empty)
        elif all(isinstance(i, (int, long, slice)) for i in item):
            return self._slice(item)
        else:
            raise TypeError("{} can only be indexed by int or slice".format(self.__class__.__name__))

    def __setitem__(self, coord, value):
        if all(isinstance(c, (int, long)) for c in coord):
            coord = self._normalised_coord(coord)
            self._data[coord] = value
        #~ elif all(isinstance(i, (int, long, slice)) for i in item):
            #~ return self._slice(item)
        else:
            raise TypeError("{} can only be indexed by int or slice".format(self.__class__.__name__))

    def __delitem__(self, coord):
        coord = self._normalised_coord(coord)
        try:
            del self._data[coord]
        except KeyError:
            pass

    def _normalised_coord(self, coord):
        """Given a coordinate, check whether it's the right dimensionality
        for this board and whether it's within bounds. Return the underlying
        global coordinate.

        If a negative number is given, apply the usual subscript maths
        to come up with an index from the end of the dimension.
        """
        if len(coord) != len(self.dimensions):
            raise IndexError("Coordinate {} has {} dimensions; the board has {}".format(coord, len(coord), len(self.dimensions)))

        #
        # Account for negative indices in the usual way, allowing
        # for the fact that you can't use negative indices if the
        # dimension is infinite
        #
        if any(d is InfiniteDimension and c < 0 for (c, d) in zip(coord, self.dimensions)):
            raise IndexError("Cannot use negative index {} on an infinite dimension".format(c))
        normalised_coord = tuple(len(d) + c if c < 0 else c for (c, d) in  zip(coord, self.dimensions))
        self._check_in_bounds(normalised_coord)
        return self._to_global(normalised_coord)

    def _slice(self, slices):
        """Produce a subset of this board linked to the same underlying data.
        """
        if len(slices) != len(self.dimensions):
            raise IndexError("Slices {} have {} dimensions; the board has {}".format(slices, len(slices), len(self.dimensions)))

        #
        # Determine the start/stop/step for all the slices
        #
        slice_indices = [slice.indices(len(dimension)) for (slice, dimension) in zip(slices, self.dimensions)]
        if any(abs(step) != 1 for start, stop, step in slice_indices):
            raise IndexError("At least one of slices {} has a stride other than 1".format(slices))

        #
        # Create the new dimensions: infinite dimensions remain infinite if
        # they're sliced open-ended, eg [1:]. Otherwise they become finite
        # dimensions of the appropriate lengthm eg [1:3] gives a finite dimension
        # of length 2
        #
        # FIXME: perhaps use the Dimension class' built-in slicers
        #
        sizes = tuple(
            Infinity if (d is InfiniteDimension and s.stop is None)
            else (stop - start)
            for s, (start, stop, step), d in zip(slices, slice_indices, self.dimensions)
        )

        #
        # Need to take into account the offset of this board, which might
        # itself be offset from the parent board.
        #
        offset = tuple(o + start for (o, (start, stop, step)) in zip(self._offset_from_global, slice_indices))
        return self.__class__(sizes, self._data, offset)

    def _occupied_dimension(self, n_dimension):
        """Return the min/max along a particular dimension.
        (Intended for internal use, eg when displaying an infinite dimension)
        """
        data_in_use = [coord for coord in self._data if coord in self]
        if not data_in_use:
            return (None, None)
        else:
            return (
                min(c[n_dimension] for c in data_in_use),
                max(c[n_dimension] for c in data_in_use)
            )

    def occupied(self):
        """Return the bounding box of space occupied
        """
        coords_in_use = [coord for coord, _ in self.iterdata()]
        min_coord = tuple(min(coord) for coord in zip(*coords_in_use))
        max_coord = tuple(max(coord) for coord in zip(*coords_in_use))
        return min_coord, max_coord

    def occupied_board(self):
        """Return a sub-board containing only the portion of this board
        which contains data.
        """
        (x0, y0), (x1, y1) = self.occupied()
        return self[x0:x1+1, y0:y1+1]

    def itercoords(self, coord1, coord2):
        """Iterate over the coordinates in between the two coordinates.

        The result is all the coordinates in the rectangular section bounded
        by coord1 and coord2
        """
        for coord in (coord1, coord2):
            self._check_in_bounds(coord)

        for coord in itertools.product(*(range(i1, 1 + i2) for (i1, i2) in zip(*sorted([coord1, coord2])))):
            yield coord

    def neighbours(self, coord, include_diagonals=True):
        """Iterate over all the neighbours of a coordinate

        For a given coordinate, yield each of its nearest neighbours along
        all dimensions, including diagonal neighbours if requested (the default)
        """
        offsets = itertools.product(*[(-1, 0, 1) for d in self.dimensions])
        for offset in offsets:
            if all(o == 0 for o in offsets):
                continue
            #
            # Diagonal offsets have no zero component
            #
            if include_diagonals or any(o == 0 for o in offset):
                neighbour = tuple(c + o for (c, o) in zip(coord, offset))
                if self._is_in_bounds(neighbour):
                    yield neighbour

    def runs_of_n(self, n, ignore_reversals=True):
        """Iterate over all dimensions to yield runs of length n

        Yield each run of n cells as a tuple of coordinates and a tuple
        of data. If ignore_reversals is True (the default) then don't
        yield the same line in the opposite direction.

        This is useful for, eg, noughts and crosses, battleship or connect 4
        where the game engine has to detect a line of somethings in a row.
        """
        all_zeroes = tuple(0 for _ in self.dimensions)
        all_offsets = itertools.product(*[(-1, 0, 1) for d in self.dimensions])
        offsets = [o for o in all_offsets if o != all_zeroes]

        already_seen = set()
        #
        # This is brute force: running for every cell and looking in every
        # direction. We check later whether we've run off the board (as
        # the resulting line will fall short). We might do some kind of
        # pre-check here, but we have to check against every direction
        # of every dimension, which would complicate this code
        #
        for cell in iter(self):
            for direction in offsets:
                line = tuple(self.iterline(cell, direction, n))
                if len(line) == n:
                    if line in already_seen:
                        continue
                    already_seen.add(line)
                    #
                    # Most of the time you don't want the same line twice,
                    # once in each direction.
                    #
                    if ignore_reversals:
                        already_seen.add(line[::-1])

                    yield line, [self[c] for c in line]

    def is_edge(self, coord):
        """Determine whether a position is on any edge of the board.

        Infinite dimensions only have a lower edge (zero); finite dimensions
        have a lower and an upper edge.
        """
        self._check_in_bounds(coord)
        dimension_bounds = ((0, len(d) - 1 if d.is_finite else 0) for d in self.dimensions)
        return any(c in bounds for (c, bounds) in zip(coord, dimension_bounds))

    def is_corner(self, coord):
        """Determine whether a position is on any corner of the board

        Infinite dimensions only have a lower edge (zero); finite dimensions
        have a lower and an upper edge.
        """
        self._check_in_bounds(coord)
        dimension_bounds = ((0, len(d) - 1 if d.is_finite else 0) for d in self.dimensions)
        return all(c in bounds for (c, bounds) in zip(coord, dimension_bounds))

    def populate(self, iterable, coord_iterable=None):
        """Populate all or part of the board from an iterable

        The population iterable can be shorter or longer than the board
        iterable. The two are zipped together so the population will stop
        when the shorter is exhausted.

        If no iterable is supplied for cooordinates, the whole board is
        populated.

        This is a convenience method both to assist testing and also for,
        eg, games like Boggle or word-searches where the board must start
        filled with letters etc. If the data needs to be, eg, a random or
        weighted choice then this should be implemented in the iterator
        supplied.

        With a coordinate iterable this could be used, for example, to combine
        iterline and a list of objects to populate data on a Battleships board.
        """
        if coord_iterable is None:
            board_iter = iter(self)
        else:
            board_iter = iter(coord_iterable)
        for coord, value in zip(board_iter, iter(iterable)):
            self[coord] = value

    def draw(self, callback=str, use_borders=True):
        """Draw the board in a very simple text layout

        By default data items are rendered as strings. If a different callback
        is supplied, it is called with the data item and should return a string.

        The idea is that items can be "hidden" from the board, or rendered
        differently according to some state. Think of Battleships where the
        same object can be hidden, revealed, or sunk.
        """
        for line in self.drawn(callback, use_borders):
            print(line)

    def drawn(self, callback=str, use_borders=True):
        if len(self.dimensions) != 2 or self.has_infinite_dimensions:
            raise self.BoardError("Can only draw a finite 2-dimensional board")

        data = dict((coord, callback(v)) for (coord, v) in self.iterdata())
        if data:
            cell_w = len(max((v for v in data.values()), key=len))
        else:
            cell_w = 1
        if use_borders:
            corner, hedge, vedge = "+", "-", "|"
        else:
            corner = hedge = vedge = ""
        divider = (corner + (hedge * cell_w)) * len(self.dimensions[0]) + corner

        if use_borders: yield divider
        for y in self.dimensions[1]:
            yield vedge + vedge.join(data.get((x, y), "").center(cell_w) for x in self.dimensions[0]) + vedge
            if use_borders: yield divider

    def painted(self, callback, size, background_colour, use_borders):
        if not Image:
            raise NotImplementedError("Painting is not available unless Pillow is installed")
        if len(self.dimensions) != 2 or self.has_infinite_dimensions:
            raise self.BoardError("Can only paint a finite 2-dimensional board")

        #
        # Construct a board of the requested size, containing
        # cells sized equally to fit within the size for each
        # of the two dimensions. Keep the border between them
        # proportional to the overall image size
        #
        n_wide = len(self.dimensions[0])
        n_high = len(self.dimensions[1])
        image = Image.new("RGBA", size)
        if use_borders:
            h_border = image.height / 80
            v_border = image.width / 80
        else:
            h_border = v_border = 0
        draw = ImageDraw.Draw(image)
        drawable_w = image.width - (1 + n_wide) * h_border
        cell_w = round(drawable_w / n_wide)
        drawable_h = image.height - (1 + n_high) * v_border
        cell_h = round(drawable_h / n_high)

        for (x, y) in self:
            obj = self[x, y]
            #
            # If the cell is empty: draw nothing
            # Try to fetch the relevant sprite from the cache
            # If the sprite is not cached, generate and cache it
            # If the sprite is larger than the cell, crop it to the correct
            # size, maintaining its centre
            #
            if obj is Empty:
                sprite = None
            else:
                try:
                    sprite = self._sprite_cache[obj]
                except KeyError:
                    sprite = self._sprite_cache[obj] = callback(obj, (cell_w, cell_h))
                if sprite.width > cell_w or sprite.height > cell_h:
                    box_x = (sprite.width - cell_w) / 2
                    box_y = (sprite.height - cell_h) / 2
                    sprite = sprite.crop((box_x, box_y, cell_w, cell_h))

            #
            # Draw the cell and any sprite within it
            #
            cell_x = round(h_border + ((cell_w + h_border) * x))
            cell_y = round(v_border + ((cell_h + v_border) * y))
            draw.rectangle((cell_x, cell_y, cell_x + cell_w, cell_y + cell_h), fill=background_colour)
            if sprite:
                x_offset, y_offset = _centred_coord((cell_w, cell_h), sprite.size)
                image.alpha_composite(sprite, (cell_x + x_offset, cell_y + y_offset))

        #
        # Return the whole image as PNG-encoded bytes
        #
        f = io.BytesIO()
        image.save(f, "PNG")
        return f.getvalue()

    def paint(self, filepath, callback=text_sprite(), size=(800, 800), background_colour="#ffffcc", use_borders=True):
        with open(filepath, "wb") as f:
            f.write(self.painted(callback, size, background_colour, use_borders))

def cornerposts(dimensions):
    for d in dimensions:
        yield 0
        if d.is_finite:
            yield len(d)

if __name__ == '__main__':
    pass