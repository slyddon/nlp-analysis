import json
import re
from collections import Counter
from typing import Dict, List, Tuple

import pandas as pd
from gensim import similarities

from . import Chapter, DatabaseConnection, Paragraph, RequestHandler
from .utils import _build_corpus, _build_lsi_model, nlp

HOST = "db"
ALLOWED_METADATA = ["title", "author", "release date", "last updated", "language"]


class Document:
    def __init__(self, text):
        self.text = text
        self._get_metadata()
        self.chapters = self._get_chapters()
        self.paragraphs = self._get_paragraphs()

        # build a gensim dictionary of words
        dictionary, corpus = _build_corpus(self.paragraphs)
        self.dictionary = dictionary
        self.corpus = corpus
        # build the lsi model
        self.model = _build_lsi_model(dictionary, corpus, num_topics)
        self.db = DatabaseConnection(host=HOST)

    def _get_metadata(self):
        """ Extract relevant metadata fields

        """
        metadata = re.findall("(.*): (.*)\n", self.text)
        for match in metadata:
            if match[0].lower() in ALLOWED_METADATA:
                setattr(self, match[0].replace(" ", "_").lower(), match[1])

    def _get_chapters(self) -> List[Chapter]:
        """ Split prose into chapters

        """
        # remove end
        prose = re.split("End of Project Gutenberg", self.text)
        # split up chapters
        chapters = re.split(r"Chapter \w+", prose[0])
        chapters = [Chapter(chapter) for chapter in chapters[1:]]
        return chapters

    def _get_paragraphs(self) -> List[Paragraph]:
        """ Split paragraphs in chapters

        """
        paragraphs = [p for c in self.chapters for p in c.paragraphs]
        return paragraphs

    def _get_coords(self, location) -> Tuple[float, float, str, str]:
        """ Get coords of a specified location

        - check in db
        - ping openstreetmap API

        :param str location: location to get
        :return numeric, numeric, str, str: lon, lat, location_class, location_type
        """
        if location in self.db.get_locations():
            lon, lat, location_class, location_type = self.db.get_location(location)[1:]
        elif location not in self.db.get_unknown_locations():
            # ping open street api
            rq = RequestHandler()
            lon, lat, location_class, location_type = rq.get_location_info(location)
            # add information to db
            self.db.add_location((location, lon, lat, location_class, location_type))
        else:
            raise ValueError(f"WARNING: {location} could not be found")
        return float(lon), float(lat), location_class, location_type

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
                lon, lat, location_class, location_type = self._get_coords(loc[0])
            except IndexError:
                self.db.add_unknown_location(loc[0])
                print(
                    f"WARNING: {loc[0]} could not be found. Added to unknown locations."
                )
                continue
            except ValueError as err:
                print(str(err))
                continue
            location_info.append(
                {
                    "location": loc[0],
                    "count": count,
                    "lon": lon,
                    "lat": lat,
                    "class": location_class,
                    "type": location_type,
                    "has_fogg": loc[1],
                }
            )
        # remove uncommon or unwanted locations
        filter_locations = self.db.get_filter_locations()
        return [l for l in location_info if l["location"] in filter_locations]
