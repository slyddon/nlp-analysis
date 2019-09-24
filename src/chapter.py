# Author: Sam Lyddon
# Date: 19/08/2019

from . import Paragraph


class Chapter:
    def __init__(self, text):
        self.text = text.strip()
        self.paragraphs = self._get_paragraphs()

    def _get_paragraphs(self):
        """ Split chapter into paragraphs

        """
        paragraphs = [Paragraph(paragraph) for paragraph in self.text.split("\n\n")]
        self.chapter_header = paragraphs[0].text
        return paragraphs[1:]

