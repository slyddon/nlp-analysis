# Author: Sam Lyddon
# Date: 19/08/2019

import spacy

nlp = spacy.load("en")


class Paragraph:
    def __init__(self, text):
        self.text = text.strip().replace("\n", " ")
        self._get_ents()

    def _get_ents(self):
        """ Get entities

        - GPE: Geo-political entity
        - LOC: Location
        - PERSON
        """
        doc = nlp(self.text)
        ents = doc.ents
        self.locations = [item.text for item in ents if item.label_ in ["GPE", "LOC"]]
        self.people = [item.text for item in ents if item.label_ in ["PERSON"]]
