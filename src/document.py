import logging
import re
from collections import Counter
from typing import Dict, List, Tuple

from gensim import similarities

from . import Chapter, Paragraph, RequestHandler
from .connections.store import LocationStore
from .connections.models import Location
from .utils import _build_corpus, _build_lsi_model, nlp

ALLOWED_METADATA = ["title", "author", "release date", "last updated", "language"]

logger = logging.getLogger(__name__)


class Document:
    def __init__(self, text: str, db_uri: str, num_topics: int = 100):
        self._get_metadata(text)
        self.chapters = self._get_chapters(text)

        # build a gensim dictionary of words
        dictionary, corpus = _build_corpus(self.paragraphs)
        self._dictionary = dictionary
        self._corpus = corpus
        # build the lsi model
        self._model = _build_lsi_model(dictionary, corpus, num_topics)

        # connect to db
        self._store = LocationStore(db_uri=db_uri)
        self._rq = RequestHandler()

    def _get_metadata(self, text: str) -> None:
        """ Extract relevant metadata fields

        """
        logger.debug("Extracting metadata")
        metadata = re.findall("(.*): (.*)\n", text)
        for match in metadata:
            if match[0].lower() in ALLOWED_METADATA:
                setattr(self, match[0].replace(" ", "_").lower(), match[1])

    def _get_chapters(self, text: str) -> List[Chapter]:
        """ Split prose into chapters

        """
        logger.debug("Splitting chapters")

        # remove end
        prose = re.split("End of Project Gutenberg", text)
        # split up chapters
        chapters = re.split(r"chapter \w+.?", prose[0], flags=re.IGNORECASE)
        chapters = [Chapter(chapter) for chapter in chapters[1:]]
        logger.debug("Extracted %s chapters" % len(chapters))

        return chapters

    @property
    def text(self) -> str:
        return "\n\n".join(c.text for c in self.chapters)

    @property
    def paragraphs(self) -> List[Paragraph]:
        paragraphs = [p for c in self.chapters for p in c.paragraphs]
        return paragraphs

    def _get_coords(self, name: str) -> Tuple[float, float, str, str]:
        """ Get coords of a specified location

        - check in db
        - ping openstreetmap API

        :param str name: location name to get
        :return numeric, numeric, str, str: lon, lat, location_class, location_type
        """
        if name in self._store.get_locations():
            location = self._store.get_location(name)
        elif name not in self._store.get_unknown_locations():
            # ping open street api
            lon, lat, location_class, location_type = self._rq.get_location_info(name)
            # add information to db
            self._store.add_location(name, lon, lat, location_class, location_type)
            location = Location(
                name=name,
                lon=lon,
                lat=lat,
                location_class=location_class,
                location_type=location_type,
            )
        else:
            raise ValueError(f"{name} could not be found")
        return location

    def get_locations(self) -> List[Dict]:
        """ Get all locations mentioned in the document

        :return list(dict):
        """
        locations = [
            (loc, para.mentions_fogg)
            for para in self.paragraphs
            for loc in para.locations
        ]

        location_info = []
        for loc, count in Counter(locations).items():
            try:
                location = self._get_coords(loc[0])
            except IndexError:
                self._store.add_unknown_location(loc[0])
                logger.warning(
                    "%s could not be found. Added to unknown locations." % loc[0]
                )
                continue
            except ValueError as err:
                logger.error(str(err))
                continue
            location_info.append(
                {
                    "location": location.name,
                    "count": count,
                    "lon": location.lon,
                    "lat": location.lat,
                    "class": location.location_class,
                    "type": location.location_type,
                    "has_fogg": loc[1],
                }
            )
        # remove uncommon or unwanted locations
        filter_locations = self._store.get_filter_locations()
        return [l for l in location_info if l["location"] in filter_locations]

    def search_paragraphs(self, phrase: str) -> Tuple[str, float]:
        """ Query the document to pull out the most similar paragraph to some input text

        :param str phrase: Text to query paragraphs against
        """
        phrase = [
            w.lemma_
            for w in nlp(phrase)
            if not (w.is_space or w.is_punct or w.is_digit or w.is_stop)
        ]

        # convert the query to LSI space
        vec_bow = self._dictionary.doc2bow(phrase)
        vec_lsi = self._model[vec_bow]
        # index against the corpus for comparison
        index = similarities.MatrixSimilarity(self._model[self._corpus])
        # perform a similarity query against the corpus
        sims = index[vec_lsi]
        sims = sorted(enumerate(sims), key=lambda item: -item[1])
        if sims[0][1] < 0.01:
            return "", 0
        else:
            return self.paragraphs[sims[0][0]].text.text, sims[0][1]
