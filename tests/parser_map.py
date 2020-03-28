import unittest
import junebugEngine
import pygame

class ParseMap(unittest.TestCase):
    def runTest(self):
        pygame.init()
        screen = pygame.display.set_mode((640,480))
        map_ = junebugEngine.MapParser.parse('data/testmap.json')
        self.assertEqual(map_.player, None)
        self.assertSetEqual(set(map_.layerDict.keys()), set(['entities', 'tiles', 'backgroundEntities']))
        self.assertEqual(map_.tilesH, 10)
        self.assertEqual(map_.tilesV, 10)