from pymclevel import BoundingBox
from pymclevel.schematic import MCSchematic
from pymclevel import MCInfdevOldLevel
from templevel import TempLevel

__author__ = 'Rio'

def test_schematic_extended_ids():
    s = MCSchematic(shape=(1, 1, 5))
    s.Blocks[0,0,0] = 2048
    temp = TempLevel("schematic", createFunc=s.saveToFile)
    s = temp.level
    assert s.Blocks[0,0,0] == 2048

def alpha_test_level():
    temp = TempLevel("alpha", createFunc=lambda f: MCInfdevOldLevel(f, create=True))
    level = temp.level
    level.createChunk(0, 0)

    for x in range(0, 10):
        level.setBlockAt(x, 2, 5, 2048)

    level.saveInPlace()
    level.close()

    level = MCInfdevOldLevel(filename=level.filename)
    return level

def testExport():
    level = alpha_test_level()

    for size in [(16, 16, 16),
                 (15, 16, 16),
                 (15, 16, 15),
                 (15, 15, 15),
                 ]:
        schem = level.extractSchematic(BoundingBox((0, 0, 0), size))
        schem = TempLevel("schem", createFunc=lambda f: schem.saveToFile(f)).level
        assert (schem.Blocks > 255).any()

def testAlphaIDs():
    level = alpha_test_level()
    assert level.blockAt(0,2,5) == 2048

