from .types import Dialog, Sentence, Person
from typing import Dict, List
import json
import pygame

def _parse_person(name: str, data: Dict) -> Person:
    portrait_path = data["portrait"]
    color = pygame.color.Color(data["color"])

    portrait = pygame.image.load(portrait_path)
    return Person(name, portrait, color)

def _parse_sentence(data: Dict, persons: Dict[str, Person]) -> Sentence:
    if len(data) != 1:
        raise KeyError("Sentence data must contain the name of the person as the only key")
    name, text = list(data.items())[0]
    person = persons[name]

    return Sentence(person, text)

def parse_dialog(filename: str) -> Dialog:
    """parses a dialog"""
    with open(filename) as dialog_file:
        data = json.load(dialog_file)

        persons: Dict[str, Person] = {}
        sentences: List[Sentence] = []

        for name, person_data in  data["persons"].items():
            person = _parse_person(name, person_data)
            persons[person.name] = person

        for sentence_data in data["sentences"]:
            sentences.append(_parse_sentence(sentence_data, persons))

        return Dialog(persons, sentences)
