# Author: Sam Lyddon
# Date: 19/08/2019

import re
from collections import Counter
import json
import pandas as pd

from . import RequestHandler, DatabaseConnection, Chapter

HOST = "db"
ALLOWED_METADATA = ["title", "author", "release date", "last updated", "language"]
OPEN_STREET_URL = "https://nominatim.openstreetmap.org"


class Document:
    def __init__(self, text):
        self.text = text
        self._get_metadata()
        self.chapters = self._get_chapters()
        self.paragraphs = self._get_paragraphs()

        self.db = DatabaseConnection(host=HOST)

    def _get_metadata(self):
        """ Extract relevant metadata fields

        """
        metadata = re.findall("(.*): (.*)\n", self.text)
        for match in metadata:
            if match[0].lower() in ALLOWED_METADATA:
                setattr(self, match[0].replace(" ", "_").lower(), match[1])

    def _get_chapters(self):
        """ Split prose into chapters

        """
        # remove end
        prose = re.split("End of Project Gutenberg", self.text)
        # split up chapters
        chapters = re.split("Chapter \w+", prose[0])
        chapters = [Chapter(chapter) for chapter in chapters[1:]]
        return chapters

    def _get_paragraphs(self):
        """ Split paragraphs in chapters

        """
        paragraphs = []
        for chapter in self.chapters:
            paragraphs += chapter.paragraphs
        return paragraphs

    def _get_coords(self, location):
        """ Get coords of a specified location

        - check in db
        - ping openstreetmap API

        :param str location: location to get
        :return numeric, numeric: lon, lat
        """
        if location in self.db.get_all_locations():
            lon, lat = self.db.get_location(location)[1:3]
        else:
            # ping open street api
            url = "{}/search?q='{}'&format=json".format(
                OPEN_STREET_URL, location.replace(" ", "-")
            )
            rq = RequestHandler()
            response = rq.call(url, "GET")
            response_dict = json.loads(response.read().decode("utf-8"))
            # get first location returned
            lon, lat = response_dict[0]["lon"], response_dict[0]["lat"]
            self.db.add_location((location, lon, lat))
        return lon, lat

    def get_locations(self):
        """ Get all locations mentioned in the document

        :return list(dict):
        """
        locations = [
            (loc, "Fogg" in para.people)
            for para in self.paragraphs
            for loc in para.locations
        ]

        location_info = []
        for loc, count in Counter(locations).items():
            try:
                lon, lat = self._get_coords(loc[0])
            except IndexError as err:
                print("WARNING: {} could not be found.".format(loc[0]))
                continue
            location_info.append(
                {
                    "location": loc[0],
                    "count": count,
                    "lon": lon,
                    "lat": lat,
                    "has_fogg": loc[1],
                }
            )

        return location_info
