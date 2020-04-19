"""types for dialogs"""
from dataclasses import dataclass
from typing import List, Dict
import pygame


@dataclass
class Person:
    """the representation of a person in a dialog"""
    name: str
    portrait: pygame.surface.Surface
    color: pygame.color.Color


@dataclass
class Sentence:
    """a sentence spoken in a dialog"""
    speaker: Person
    text: str


@dataclass
class Dialog:
    """a dialog"""
    persons: Dict[str, Person]
    sentences: List[Sentence]
