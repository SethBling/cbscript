import itertools
import os
import shutil
import unittest
import numpy

from pymclevel import mclevel
from pymclevel.infiniteworld import MCInfdevOldLevel
from pymclevel import nbt
from pymclevel.schematic import MCSchematic
from pymclevel.box import BoundingBox
from pymclevel import block_copy
from templevel import mktemp, TempLevel

__author__ = 'Rio'

class TestAnvilLevelCreate(unittest.TestCase):
    def testCreate(self):
        temppath = mktemp("AnvilCreate")
        self.anvilLevel = MCInfdevOldLevel(filename=temppath, create=True)
        self.anvilLevel.close()
        shutil.rmtree(temppath)


class TestAnvilLevel(unittest.TestCase):
    def setUp(self):
        self.indevLevel = TempLevel("hell.mclevel")
        self.anvilLevel = TempLevel("AnvilWorld")

    def testUnsetProperties(self):
        level = self.anvilLevel.level
        del level.root_tag['Data']['LastPlayed']
        import time
        assert 0 != level.LastPlayed
        level.LastPlayed = time.time() * 1000 - 1000000

    def testGetEntities(self):
        level = self.anvilLevel.level
        print len(level.getEntitiesInBox(level.bounds))

    def testCreateChunks(self):
        level = self.anvilLevel.level

        for ch in list(level.allChunks):
            level.deleteChunk(*ch)
        level.createChunksInBox(BoundingBox((0, 0, 0), (32, 0, 32)))

    def testCopyChunks(self):
        level = self.anvilLevel.level
        temppath = mktemp("AnvilCreate")
        newLevel = MCInfdevOldLevel(filename=temppath, create=True)
        for cx, cz in level.allChunks:
            newLevel.copyChunkFrom(level, cx, cz)

        newLevel.close()
        shutil.rmtree(temppath)

    def testCopyConvertBlocks(self):
        indevlevel = self.indevLevel.level
        level = self.anvilLevel.level
        x, y, z = level.bounds.origin
        x += level.bounds.size[0]/2 & ~15
        z += level.bounds.size[2]/2 & ~15
        x -= indevlevel.Width / 2
        z -= indevlevel.Height / 2

        middle = (x, y, z)

        oldEntityCount = len(level.getEntitiesInBox(BoundingBox(middle, indevlevel.bounds.size)))
        level.copyBlocksFrom(indevlevel, indevlevel.bounds, middle)

        convertedSourceBlocks, convertedSourceData = block_copy.convertBlocks(indevlevel, level, indevlevel.Blocks[0:16, 0:16, 0:indevlevel.Height], indevlevel.Data[0:16, 0:16, 0:indevlevel.Height])

        assert ((level.getChunk(x >> 4, z >> 4).Blocks[0:16, 0:16, 0:indevlevel.Height]
                == convertedSourceBlocks).all())

        assert (oldEntityCount + len(indevlevel.getEntitiesInBox(indevlevel.bounds))
                == len(level.getEntitiesInBox(BoundingBox(middle, indevlevel.bounds.size))))

    def testImportSchematic(self):
        level = self.anvilLevel.level
        cx, cz = level.allChunks.next()

        schem = mclevel.fromFile("schematics/CreativeInABox.schematic")
        box = BoundingBox((cx * 16, 64, cz * 16), schem.bounds.size)
        level.copyBlocksFrom(schem, schem.bounds, (0, 64, 0))
        schem = MCSchematic(shape=schem.bounds.size)
        schem.copyBlocksFrom(level, box, (0, 0, 0))
        convertedSourceBlocks, convertedSourceData = block_copy.convertBlocks(schem, level, schem.Blocks, schem.Data)
        assert (level.getChunk(cx, cz).Blocks[0:1, 0:3, 64:65] == convertedSourceBlocks).all()

    def testRecreateChunks(self):
        level = self.anvilLevel.level

        for x, z in itertools.product(xrange(-1, 3), xrange(-1, 2)):
            level.deleteChunk(x, z)
            assert not level.containsChunk(x, z)
            level.createChunk(x, z)

    def testFill(self):
        level = self.anvilLevel.level
        cx, cz = level.allChunks.next()
        box = BoundingBox((cx * 16, 0, cz * 16), (32, level.Height, 32))
        level.fillBlocks(box, level.materials.WoodPlanks)
        level.fillBlocks(box, level.materials.WoodPlanks, [level.materials.Stone])
        level.saveInPlace()
        c = level.getChunk(cx, cz)

        assert (c.Blocks == 5).all()

    def testReplace(self):
        level = self.anvilLevel.level

        level.fillBlocks(BoundingBox((-11, 0, -7), (38, level.Height, 25)), level.materials.WoodPlanks, [level.materials.Dirt, level.materials.Grass])

    def testSaveRelight(self):
        indevlevel = self.indevLevel.level
        level = self.anvilLevel.level

        cx, cz = -3, -1

        level.deleteChunk(cx, cz)

        level.createChunk(cx, cz)
        level.copyBlocksFrom(indevlevel, BoundingBox((0, 0, 0), (32, 64, 32,)), level.bounds.origin)

        level.generateLights()
        level.saveInPlace()

    def testRecompress(self):
        level = self.anvilLevel.level
        cx, cz = level.allChunks.next()

        ch = level.getChunk(cx, cz)
        ch.dirty = True
        ch.Blocks[:] = 6
        ch.Data[:] = 13
        d = {}
        keys = 'Blocks Data SkyLight BlockLight'.split()
        for key in keys:
            d[key] = numpy.array(getattr(ch, key))

        for i in range(5):
            level.saveInPlace()
            ch = level.getChunk(cx, cz)
            ch.dirty = True
            assert (ch.Data == 13).all()
            for key in keys:
                assert (d[key] == getattr(ch, key)).all()

    def testPlayerSpawn(self):
        level = self.anvilLevel.level

        level.setPlayerSpawnPosition((0, 64, 0), "Player")
        level.getPlayerPosition()
        assert len(level.players) != 0

    def testBigEndianIntHeightMap(self):
        """ Test modifying, saving, and loading the new TAG_Int_Array heightmap
        added with the Anvil format.
        """
        chunk = nbt.load("testfiles/AnvilChunk.dat")

        hm = chunk["Level"]["HeightMap"]
        hm.value[2] = 500
        oldhm = numpy.array(hm.value)

        filename = mktemp("ChangedChunk")
        chunk.save(filename)
        changedChunk = nbt.load(filename)
        os.unlink(filename)

        eq = (changedChunk["Level"]["HeightMap"].value == oldhm)
        assert eq.all()
