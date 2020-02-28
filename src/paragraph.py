from typing import Dict, List

import spacy
from spacy.pipeline import EntityRuler

nlp = spacy.load("en")
ruler = EntityRuler(nlp, overwrite_ents=True)
patterns = [
    {
        "label": "PERSON",
        "pattern": [{"TEXT": {"REGEX": r"Phileas|Mr\.?"}}, {"LOWER": "fogg"}],
    },
    {"label": "PERSON", "pattern": "Fogg"},
    {"label": "PERSON", "pattern": "Passepartout"},
    {"label": "PERSON", "pattern": "Fix"},
    {"label": "GPE", "pattern": "Calcutta"},
]
ruler.add_patterns(patterns)
nlp.add_pipe(ruler)


class Paragraph:
    def __init__(self, text):
        self.text = nlp(text.strip().replace("\n", " "), disable=["tagger", "parser"])
        self._get_ents()

    def _get_ents(self):
        """ Get entities

        - GPE: Geo-political entity
        - LOC: Location
        - PERSON
        """
        ents = self.text.ents
        self.locations = [item.text for item in ents if item.label_ in ["GPE", "LOC"]]
        self.people = [item.text for item in ents if item.label_ in ["PERSON"]]
        self.mentions_fogg = any(["Fogg" in p for p in self.people])
