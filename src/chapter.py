from typing import List

from . import Paragraph
from .utils import _build_corpus, _build_lsi_model, nlp



class Chapter:
    def __init__(self, text: str):
        self.text = text.strip()
        self.paragraphs = self._get_paragraphs()

        # build a gensim dictionary of words
        dictionary, corpus = _build_corpus(self.paragraphs)
        self.dictionary = dictionary
        self.corpus = corpus
        # build the lsi model
        if len(dictionary) > 0:
            self.model = _build_lsi_model(dictionary, corpus, num_topics)
        else:
            self.model = None

        """ Split chapter into paragraphs

        """
        split_text = [t.strip().replace("\n", " ") for t in self.text.split("\n\n")]
        self.chapter_header = split_text[0]
        paragraphs = [
            Paragraph(p) for p in nlp.pipe(split_text[1:], disable=["tagger", "parser"])
        ]
        return paragraphs

    def get_topics(self, num_words: int = 10) -> List:
        """ Extract the chapter topics generated from Latent Semantic Indexing

        :param int num_words: Number of words to include in each topic
        """
        if self.model is None:
            return []
        return self.model.show_topics(num_words=num_words, formatted=False)
