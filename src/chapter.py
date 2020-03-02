from typing import List, Tuple

from . import Paragraph
from .utils import _build_corpus, _build_lsi_model, nlp


class Chapter:
    def __init__(self, text: str, num_topics: int = 10):
        self.paragraphs = self._get_paragraphs(text)

        # build a gensim dictionary of words
        dictionary, corpus = _build_corpus(self.paragraphs)
        self.dictionary = dictionary
        self.corpus = corpus
        # build the lsi model
        if len(dictionary) > 0:
            self.model = _build_lsi_model(dictionary, corpus, num_topics)
        else:
            self.model = None

    @property
    def text(self) -> str:
        return (
            self.chapter_header
            + "\n\n"
            + "\n\n".join(p.text.text for p in self.paragraphs)
        )

    def _get_paragraphs(self, text) -> List[Paragraph]:
        """ Split chapter into paragraphs

        """
        split_text = [t.strip().replace("\n", " ") for t in text.strip().split("\n\n")]
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
