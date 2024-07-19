from __future__ import annotations

__all__ = ["Pack2d", "Packed2dItem"]


# emath
from emath import UVector2

# python
from typing import Mapping
from typing import Sequence


class Pack2d:
    def __init__(
        self,
        bin_size: UVector2,
        *,
        max_bins: int | None = None,
    ):
        if not isinstance(bin_size, UVector2):
            raise TypeError("bin size must be UVector2")
        self._bin_size = bin_size
        self._max_bins = max_bins
        self._items: list[UVector2] = []
        self._unpacked_indexes: set[int] = set()
        self._bins: list[_Bin] = []
        self._map: dict[int, Packed2dItem] = {}

    def add(self, size: UVector2) -> int:
        if not isinstance(size, UVector2):
            raise TypeError("size must be UVector2")
        id = len(self._items)
        self._items.append(size)
        self._unpacked_indexes.add(id)
        return id

    def pack(self) -> None:
        unpacked = [(i, self._items[i]) for i in self._unpacked_indexes]
        unpacked.sort(key=lambda s: (-s[1][1], -s[1][0]))
        for i, unit in unpacked:
            for bin_index, bin in enumerate(self._bins):
                position = bin.add(unit)
                if position is not None:
                    break
            else:
                if self._max_bins is not None:
                    if len(self._bins) == self._max_bins:
                        raise RuntimeError("no space for item")
                    assert len(self._bins) < self._max_bins
                bin_index = len(self._bins)
                bin = _Bin(self._bin_size)
                self._bins.append(bin)
                position = bin.add(unit)
                if position is None:
                    raise RuntimeError("item is too large to pack")
            self._map[i] = Packed2dItem(bin_index, position)
        self._unpacked_indexes = set()

    def repack(self) -> None:
        self._unpacked_indexes = set(range(len(self._items)))
        self._map = {}
        self._bins = []
        self.pack()

    @property
    def map(self) -> Mapping[int, Packed2dItem]:
        return self._map

    @property
    def bins(self) -> Sequence[UVector2]:
        return tuple(b.size for b in self._bins)


class Packed2dItem:
    def __init__(self, bin: int, position: UVector2):
        self._bin = bin
        self._position = position

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Packed2dItem):
            return NotImplemented
        return self._bin == other._bin and self._position == other._position

    @property
    def bin(self) -> int:
        return self._bin

    @property
    def position(self) -> UVector2:
        return self._position

    def __repr__(self) -> str:
        return f"<Pack2dItem bin={self._bin} position={tuple(self._position)}>"


class _Bin:
    def __init__(self, max_size: UVector2):
        self._max_size = max_size
        self._lines: list[UVector2] = []

    def add(self, size: UVector2) -> UVector2 | None:
        # early out for things that are larger than the max bin size
        if size.x > self._max_size.x or size.y > self._max_size.y:
            return None
        bottom = 0
        for i, (line_width, line_height) in enumerate(self._lines):
            bottom += line_height
            # lines may not exceed the width of the max width of the bin
            if line_width + size.x > self._max_size.x:
                continue
            # only the last line can have its height expanded
            if (i + 1) < len(self._lines) and size.y > line_height:
                continue
            position = UVector2(line_width, bottom - line_height)
            self._lines[i] = UVector2(line_width + size.x, max(line_height, size.y))
            return position
        # thing is too vertically large to fit in a new line
        if bottom + size.y > self._max_size.y:
            return None
        self._lines.append(size)
        return UVector2(0, bottom)

    @property
    def size(self) -> UVector2:
        return UVector2(max(l.x for l in self._lines), sum(l.y for l in self._lines))
