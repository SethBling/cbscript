from pymclevel import fromFile
from templevel import TempLevel

__author__ = 'Rio'

def test_command_block():
    level = TempLevel("AnvilWorld").level

    cmdblock = fromFile("testfiles/Commandblock.schematic")

    point = level.bounds.origin + [p/2 for p in level.bounds.size]
    level.copyBlocksFrom(cmdblock, cmdblock.bounds, point)

    te = level.tileEntityAt(*point)
    command = te['Command'].value
    words = command.split(' ')
    x, y, z = words[2:5]
    assert x == str(point[0])
    assert y == str(point[1] + 10)
    assert z == str(point[2])
