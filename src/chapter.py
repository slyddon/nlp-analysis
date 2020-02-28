from typing import List

import spacy
from spacy.pipeline import EntityRuler
import gensim.corpora as corpora
import gensim.models as models

from . import Paragraph

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


class Chapter:
    def __init__(self, text: str):
        self.text = text.strip()
        self.paragraphs = self._get_paragraphs()

    def _get_paragraphs(self) -> List[Paragraph]:
        """ Split chapter into paragraphs

        """
        split_text = [t.strip().replace("\n", " ") for t in self.text.split("\n\n")]
        self.chapter_header = split_text[0]
        paragraphs = [
            Paragraph(p) for p in nlp.pipe(split_text[1:], disable=["tagger", "parser"])
        ]
        return paragraphs

    def get_topics(self, num_topics: int = 10, num_words: int = 10) -> List:
        """ Extract the chapter topics using Latent Semantic Indexing

        - Perform a Singular Value Decomposition on the chapter corpus

        """
        # build a gensim dictionary of words
        dictionary = corpora.Dictionary([p.extract_lemma() for p in self.paragraphs])
        # filter out common and infrequent words
        dictionary.filter_extremes(no_below=len(self.paragraphs) // 10)
        # convert the corpus to a bag of words model
        corpus = [
            dictionary.doc2bow(p) for p in [p.extract_lemma() for p in self.paragraphs]
        ]
        # weight the corpus according to Term Frequency / Inverse Document Frequency
        tfidf = models.TfidfModel(corpus)
        tfidf_corpus = tfidf[corpus]
        # Latent Semantic Index Transformation
        lsi = models.LsiModel(tfidf_corpus, id2word=dictionary, num_topics=num_topics)
        return lsi.show_topics(num_words=num_words, formatted=False)
