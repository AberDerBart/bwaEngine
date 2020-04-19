import unittest
from junebugEngine import dialog
import pygame

class ParseMap(unittest.TestCase):
    def runTest(self):
        dia = dialog.parse('data/dialog.json')
        self.assertIn("Alice",dia.persons)
        self.assertIn("Bob", dia.persons)
        self.assertEqual(dia.persons["Alice"].name, "Alice")
        self.assertIsInstance(dia.persons["Alice"].portrait, pygame.surface.Surface)
        self.assertEqual(dia.persons["Alice"].color, pygame.color.Color(255,0,0))
        self.assertEqual(dia.persons["Bob"].name, "Bob")
        self.assertIsInstance(dia.persons["Bob"].portrait, pygame.surface.Surface)
        self.assertEqual(dia.persons["Bob"].color, pygame.color.Color(0,255,0))
        self.assertEqual(len(dia.sentences), 3)
        self.assertEqual(dia.sentences[0].speaker, dia.persons['Alice'])
        self.assertEqual(dia.sentences[0].text, "Hi, how are you?")
        self.assertEqual(dia.sentences[1].speaker, dia.persons['Bob'])
        self.assertEqual(dia.sentences[1].text, "I am fine, thanks for asking!")
        self.assertEqual(dia.sentences[2].speaker, dia.persons['Alice'])
        self.assertEqual(dia.sentences[2].text, "Cool! Nice talking to you!")