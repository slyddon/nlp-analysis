from typing import Dict, List


class Paragraph:
    def __init__(self, text: str):
        self.text = text
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

    def extract_lemma(self, word_len: int = 3) -> List[str]:
        """ Extract the lemmatized words in the paragraph

        :param int word_len: Length of words to limit
        :return:
        """
        return [
            w.lemma_
            for w in self.text
            if not (
                w.is_space
                or w.is_punct
                or w.is_digit
                or w.is_stop
                or len(w.lemma_) < word_len
            )
        ]
