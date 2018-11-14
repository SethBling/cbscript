from pymclevel.infiniteworld import SessionLockLost, MCInfdevOldLevel
from templevel import TempLevel
import unittest

class SessionLockTest(unittest.TestCase):
    def test_session_lock(self):
        temp = TempLevel("AnvilWorld")
        level = temp.level
        level2 = MCInfdevOldLevel(level.filename)
        def touch():
            level.saveInPlace()
        self.assertRaises(SessionLockLost, touch)

