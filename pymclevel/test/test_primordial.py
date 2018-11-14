from templevel import TempLevel

def testPrimordialDesert():
    templevel = TempLevel("PrimordialDesert")
    level = templevel.level
    for chunk in level.allChunks:
        level.getChunk(*chunk)
