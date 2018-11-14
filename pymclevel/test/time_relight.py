from pymclevel.infiniteworld import MCInfdevOldLevel
from pymclevel import mclevel
from timeit import timeit

import templevel

#import logging
#logging.basicConfig(level=logging.INFO)

def natural_relight():
    world = mclevel.fromFile("testfiles/AnvilWorld")
    t = timeit(lambda: world.generateLights(world.allChunks), number=1)
    print "Relight natural terrain: %d chunks in %.02f seconds (%.02fms per chunk)" % (world.chunkCount, t, t / world.chunkCount * 1000)


def manmade_relight():
    t = templevel.TempLevel("TimeRelight", createFunc=lambda f:MCInfdevOldLevel(f, create=True))

    world = t.level
    station = mclevel.fromFile("testfiles/station.schematic")

    times = 2

    for x in range(times):
        for z in range(times):
            world.copyBlocksFrom(station, station.bounds, (x * station.Width, 63, z * station.Length), create=True)

    t = timeit(lambda: world.generateLights(world.allChunks), number=1)
    print "Relight manmade building: %d chunks in %.02f seconds (%.02fms per chunk)" % (world.chunkCount, t, t / world.chunkCount * 1000)

if __name__ == '__main__':
    natural_relight()
    manmade_relight()



