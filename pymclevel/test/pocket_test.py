import unittest
import numpy
from templevel import TempLevel

__author__ = 'Rio'

class TestPocket(unittest.TestCase):
    def setUp(self):
        # self.alphaLevel = TempLevel("Dojo_64_64_128.dat")
        self.level = TempLevel("PocketWorld")
        self.alphalevel = TempLevel("AnvilWorld")

    def testPocket(self):
        level = self.level.level
#        alphalevel = self.alphalevel.level
        print "Chunk count", len(level.allChunks)
        chunk = level.getChunk(1, 5)
        a = numpy.array(chunk.SkyLight)
        chunk.dirty = True
        chunk.needsLighting = True
        level.generateLights()
        level.saveInPlace()
        assert (a == chunk.SkyLight).all()

#        level.copyBlocksFrom(alphalevel, BoundingBox((0, 0, 0), (64, 64, 64,)), (0, 0, 0))
        # assert((level.Blocks[0:64, 0:64, 0:64] == alphalevel.Blocks[0:64, 0:64, 0:64]).all())
