import os
import sys
import urllib2
import time
from urlparse import urlparse
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from google.appengine.api import memcache

class App:
    REQUEST_INTERVAL = 3

    def __init__(self, url):
        self.url = url
        self.error = ''

    def process(self):
        try:
            response = self.request()
            self.row_html = response.read()
            self.encoded_html = self.__encode(self.row_html)

            lexer = get_lexer_by_name('html')
            format = HtmlFormatter(nowrap = True)
            self.formatted_html = highlight(self.encoded_html, lexer, format)
            lines = len(self.formatted_html.split('\n')) + 1
            self.line_number = '\n'.join([str(n) for n in range(1, lines)])
        except:
            self.error = sys.exc_info()[1]

    def request(self):
        domain = self.__get_domain(self.url)
        if not domain:
            raise RequestError('"%s" is invalid URI' % self.url)

        now = int(time.time())
        cached_time = memcache.get(domain)
        if cached_time and not self.__is_dev_server():
            if now - cached_time > self.REQUEST_INTERVAL:
                memcache.set(domain, now)
            else:
                raise RequestError('Too many request same domain.')
        else:
            memcache.set(domain, now)

        response = urllib2.urlopen(self.url)

        return response

    @staticmethod
    def spanize(text):
        res = []
        for line in text.split('\n'):
            res.append('<span>' + line + '</span>')

        return '\n'.join(res)

    @staticmethod
    def __encode(data):
        for charset in ['utf-8', 'shift_jis', 'euc-jp', 'iso2022-jp']:
            try: return data.decode(charset)
            except: pass

        raise 'Encoding failed.'

    @staticmethod
    def __get_domain(url):
        return urlparse(url).netloc

    @staticmethod
    def __is_dev_server():
        return os.environ.get('SERVER_SOFTWARE')[:11] == 'Development'

class RequestError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return str(self.value)
