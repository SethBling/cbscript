import unittest
from pymclevel.minecraft_server import MCServerChunkGenerator
from templevel import TempLevel
from pymclevel.box import BoundingBox

__author__ = 'Rio'

class TestServerGen(unittest.TestCase):
    def setUp(self):
        # self.alphaLevel = TempLevel("Dojo_64_64_128.dat")
        self.alphalevel = TempLevel("AnvilWorld")

    def testCreate(self):
        gen = MCServerChunkGenerator()
        print "Version: ", gen.serverVersion

        def _testCreate(filename):
            gen.createLevel(filename, BoundingBox((-128, 0, -128), (128, 128, 128)))

        TempLevel("ServerCreate", createFunc=_testCreate)

    def testServerGen(self):
        gen = MCServerChunkGenerator()
        print "Version: ", gen.serverVersion

        level = self.alphalevel.level

        gen.generateChunkInLevel(level, 50, 50)
        gen.generateChunksInLevel(level, [(120, 50), (121, 50), (122, 50), (123, 50), (244, 244), (244, 245), (244, 246)])
        c = level.getChunk(50, 50)
        assert c.Blocks.any()
