import itertools
import os
import unittest
from pymclevel import mclevel
from templevel import TempLevel, mktemp
from pymclevel.schematic import MCSchematic
from pymclevel.box import BoundingBox

__author__ = 'Rio'

class TestSchematics(unittest.TestCase):
    def setUp(self):
        # self.alphaLevel = TempLevel("Dojo_64_64_128.dat")
        self.indevLevel = TempLevel("hell.mclevel")
        self.anvilLevel = TempLevel("AnvilWorld")

    def testCreate(self):
        # log.info("Schematic from indev")

        size = (64, 64, 64)
        temp = mktemp("testcreate.schematic")
        schematic = MCSchematic(shape=size, filename=temp, mats='Classic')
        level = self.indevLevel.level

        schematic.copyBlocksFrom(level, BoundingBox((0, 0, 0), (64, 64, 64,)), (0, 0, 0))
        assert((schematic.Blocks[0:64, 0:64, 0:64] == level.Blocks[0:64, 0:64, 0:64]).all())

        schematic.copyBlocksFrom(level, BoundingBox((0, 0, 0), (64, 64, 64,)), (-32, -32, -32))
        assert((schematic.Blocks[0:32, 0:32, 0:32] == level.Blocks[32:64, 32:64, 32:64]).all())

        schematic.saveInPlace()

        schem = mclevel.fromFile("schematics/CreativeInABox.schematic")
        tempSchematic = MCSchematic(shape=(1, 1, 3))
        tempSchematic.copyBlocksFrom(schem, BoundingBox((0, 0, 0), (1, 1, 3)), (0, 0, 0))

        level = self.anvilLevel.level
        for cx, cz in itertools.product(xrange(0, 4), xrange(0, 4)):
            try:
                level.createChunk(cx, cz)
            except ValueError:
                pass
        schematic.copyBlocksFrom(level, BoundingBox((0, 0, 0), (64, 64, 64,)), (0, 0, 0))
        schematic.close()
        os.remove(temp)

    def testRotate(self):
        level = self.anvilLevel.level
        schematic = level.extractSchematic(BoundingBox((0, 0, 0), (21, 11, 8)))
        schematic.rotateLeft()

        level.copyBlocksFrom(schematic, schematic.bounds, level.bounds.origin, biomes=True, create=True)

        schematic.flipEastWest()
        level.copyBlocksFrom(schematic, schematic.bounds, level.bounds.origin, biomes=True, create=True)

        schematic.flipVertical()
        level.copyBlocksFrom(schematic, schematic.bounds, level.bounds.origin, biomes=True, create=True)

    def testZipSchematic(self):
        level = self.anvilLevel.level

        x, y, z = level.bounds.origin
        x += level.bounds.size[0]/2 & ~15
        z += level.bounds.size[2]/2 & ~15

        box = BoundingBox((x, y, z), (64, 64, 64,))
        zs = level.extractZipSchematic(box)
        assert(box.chunkCount == zs.chunkCount)
        zs.close()
        os.remove(zs.filename)

    def testINVEditChests(self):
        invFile = mclevel.fromFile("schematics/Chests/TinkerersBox.inv")
        assert invFile.Blocks.any()
        assert not invFile.Data.any()
        assert len(invFile.Entities) == 0
        assert len(invFile.TileEntities) == 1
        # raise SystemExit
