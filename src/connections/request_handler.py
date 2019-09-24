# Author: Sam Lyddon
# Date: 19/08/2019
# Request handler class for communicating with APIs

import json
import urllib.request
from bs4 import BeautifulSoup as Soup


class RequestHandler(object):
    def call(self, url, method, data_dict=None):
        """ Perform HTTP request

        :param str url: url to call
        :param str method: request method
        :param dict data_dict:
        :raises urllib.error.HTTPError:
        :return http.client.HTTPResponse:
        """
        try:
            kwargs = {}

            if data_dict is not None:
                data_json = json.dumps(data_dict)
                kwargs["data"] = bytes(data_json, "utf-8")
                kwargs["headers"] = {"Content-Type": "application/json"}

            request = urllib.request.Request(url, method=method, **kwargs)
            response = urllib.request.urlopen(request)

            return response
        except urllib.error.HTTPError as err:
            raise err

    def _clean_text(self, web_page):
        """ Extract relevant text from web page

        :param str web_page: html to parse
        :return str: text from web page
        """
        soup = Soup(web_page, features="html.parser")
        text = soup.get_text().replace("\r", "")
        return text

    def scrape_text(self, url):
        """ Scrape text from web page

        :param str url: page to scrape
        :return str: text from web page
        """
        response = self.call(url, "GET")
        web_page = response.read()
        text = self._clean_text(web_page)
        return text

