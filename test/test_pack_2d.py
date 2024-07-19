# epack
from epack import Pack2d
from epack import Packed2dItem

# emath
from emath import UVector2

# pytest
import pytest

# python
from itertools import permutations


def test_init():
    pack = Pack2d(UVector2(1, 1))
    assert pack.map == {}


def test_pack_nothing():
    pack = Pack2d(UVector2(1, 1))
    pack.pack()
    assert pack.map == {}


@pytest.mark.parametrize("bin_width", [0, 1, 10, 100])
def test_pack_too_wide(bin_width):
    pack = Pack2d(UVector2(bin_width, 100))
    pack.add(UVector2(bin_width + 1, 1))
    with pytest.raises(RuntimeError) as excinfo:
        pack.pack()
    assert str(excinfo.value) == "item is too large to pack"


@pytest.mark.parametrize("bin_height", [0, 1, 10, 100])
def test_pack_too_tall(bin_height):
    pack = Pack2d(UVector2(100, bin_height))
    pack.add(UVector2(1, bin_height + 1))
    with pytest.raises(RuntimeError) as excinfo:
        pack.pack()
    assert str(excinfo.value) == "item is too large to pack"


@pytest.mark.parametrize("bins", [0, 1, 10])
def test_out_of_bins(bins):
    pack = Pack2d(UVector2(100, 100), max_bins=bins)
    for i in range(bins + 1):
        pack.add(UVector2(100, 100))
    with pytest.raises(RuntimeError) as excinfo:
        pack.pack()
    assert str(excinfo.value) == "no space for item"


@pytest.mark.parametrize("width", [1, 10, 100])
@pytest.mark.parametrize("height", [1, 10, 100])
def test_pack_exact_size(width, height):
    pack = Pack2d(UVector2(width, height))
    pack.add(UVector2(width, height))
    pack.pack()
    assert pack.map == {0: Packed2dItem(0, UVector2(0, 0))}


def test_packed():
    pack = Pack2d(UVector2(1, 1))
    pack.add(UVector2(1, 1))
    pack.pack()
    packed = pack.map[0]
    assert packed.bin == 0
    assert packed.position == UVector2(0, 0)
    assert repr(packed) == "<Pack2dItem bin=0 position=(0, 0)>"


@pytest.mark.parametrize("width", [1, 10, 100])
@pytest.mark.parametrize("height", [1, 10, 100])
def test_pack_tight(width, height):
    pack = Pack2d(UVector2(width, height))
    for i in range(width * height):
        pack.add(UVector2(1, 1))
    pack.pack()
    assert pack.map == {
        i: Packed2dItem(0, UVector2(w, h))
        for i, (w, h) in enumerate(((w, h) for h in range(height) for w in range(width)))
    }


@pytest.mark.parametrize(
    "items",
    permutations(
        [
            UVector2(51, 51),
            UVector2(50, 51),
            UVector2(49, 51),
        ]
    ),
)
def test_backfill(items):
    pack = Pack2d(UVector2(100, 100))
    for item in items:
        pack.add(item)
    pack.pack()
    assert pack.map == {
        items.index(UVector2(51, 51)): Packed2dItem(0, UVector2(0, 0)),
        items.index(UVector2(50, 51)): Packed2dItem(1, UVector2(0, 0)),
        items.index(UVector2(49, 51)): Packed2dItem(0, UVector2(51, 0)),
    }


@pytest.mark.parametrize(
    "items",
    permutations(
        [
            UVector2(51, 50),
            UVector2(50, 50),
            UVector2(49, 50),
        ]
    ),
)
def test_newline(items):
    pack = Pack2d(UVector2(100, 100))
    for item in items:
        pack.add(item)
    pack.pack()
    assert pack.map == {
        items.index(UVector2(51, 50)): Packed2dItem(0, UVector2(0, 0)),
        items.index(UVector2(50, 50)): Packed2dItem(0, UVector2(0, 50)),
        items.index(UVector2(49, 50)): Packed2dItem(0, UVector2(51, 0)),
    }


@pytest.mark.parametrize(
    "items",
    permutations(
        [
            UVector2(52, 30),
            UVector2(51, 20),
            UVector2(50, 10),
        ]
    ),
)
def test_last_line_expansion(items):
    pack = Pack2d(UVector2(100, 100))
    for item in items:
        pack.add(item)
    pack.pack()
    pack.add(UVector2(10, 40))
    pack.add(UVector2(50, 1))
    pack.pack()
    assert pack.map == {
        items.index(UVector2(52, 30)): Packed2dItem(0, UVector2(0, 0)),
        items.index(UVector2(51, 20)): Packed2dItem(0, UVector2(0, 30)),
        items.index(UVector2(50, 10)): Packed2dItem(0, UVector2(0, 50)),
        3: Packed2dItem(0, UVector2(50, 50)),
        4: Packed2dItem(0, UVector2(0, 90)),
    }


@pytest.mark.parametrize(
    "items",
    permutations(
        [
            UVector2(10, 40),
            UVector2(52, 30),
            UVector2(51, 20),
            UVector2(50, 10),
            UVector2(50, 1),
        ]
    ),
)
def test_repack(items):
    pack = Pack2d(UVector2(100, 100))
    for item in items:
        pack.add(item)
        pack.pack()
    pack.repack()
    assert pack.map == {
        items.index(UVector2(10, 40)): Packed2dItem(0, UVector2(0, 0)),
        items.index(UVector2(52, 30)): Packed2dItem(0, UVector2(10, 0)),
        items.index(UVector2(51, 20)): Packed2dItem(0, UVector2(0, 40)),
        items.index(UVector2(50, 10)): Packed2dItem(0, UVector2(0, 60)),
        items.index(UVector2(50, 1)): Packed2dItem(0, UVector2(50, 60)),
    }
