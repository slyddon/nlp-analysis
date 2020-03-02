from typing import List, Tuple

import gensim.corpora as corpora
import gensim.models as models
import spacy
from spacy.pipeline import EntityRuler

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


def _build_corpus(
    paragraphs: List[Paragraph]
) -> Tuple[corpora.Dictionary, models.TfidfModel]:
    """ Build the corpus and dictionary for the chapter

    - Use a bag-of-words model for the corpus
    - Weight the corpus by Term Frequency / Inverse Document Frequency

    :param List[Paragraph] paragraphs: Paragraphs in document
    """
    # build a gensim dictionary of words
    dictionary = corpora.Dictionary([p.extract_lemma() for p in paragraphs])
    # filter out common and infrequent words
    dictionary.filter_extremes()
    # convert the corpus to a bag of words model
    corpus = [dictionary.doc2bow(p) for p in [p.extract_lemma() for p in paragraphs]]
    # weight the corpus
    tfidf = models.TfidfModel(corpus)
    tfidf_corpus = tfidf[corpus]
    return dictionary, tfidf_corpus


def _build_lsi_model(
    dictionary: corpora.Dictionary, corpus: models.TfidfModel, num_topics: int
) -> models.LsiModel:
    """ Build an LSI model

    - Perform a Singular Value Decomposition on the chapter corpus
        - Create a matrix of word counts per document
        - Group both documents that contain similar words and words that occur in a similar set of documents
        - Reduce the number of rows while preserving the similarity structure among columns
    
    :param corpora.Dictionary dictionary: Dictionary of words
    :param models.TfidfModel corpus: Corpus of text
    """
    model = models.LsiModel(corpus, id2word=dictionary, num_topics=num_topics)
    return model
