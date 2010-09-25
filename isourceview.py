import os
import urllib2
import time
from urlparse import urlparse
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from google.appengine.api import memcache

REQUEST_INTERVAL = 3

def request(url):
    domain = urlparse(url).netloc
    if not domain:
        raise RequestError('"%s" is invalid URI' % url)

    now = int(time.time())
    cached_time = memcache.get(domain)
    if cached_time and not is_dev_server():
        if now - cached_time > REQUEST_INTERVAL:
            memcache.set(domain, now)
        else:
            raise RequestError('Too many request same domain.')
    else:
        memcache.set(domain, now)

    response = urllib2.urlopen(url)
    raw_html = response.read()

    return encode(raw_html)

def convert_html(html):
    lexer = get_lexer_by_name('html')
    format = HtmlFormatter(nowrap = True)
    html = highlight(html, lexer, format)

    return spanize(html)

def get_line_number(html):
    lines = len(html.split('\n')) + 1
    lines = '\n'.join([str(n) for n in range(1, lines)])

    return spanize(lines)

def spanize(text):
    res = []
    for line in text.split('\n'):
        res.append('<span>' + line + '</span>')

    return '\n'.join(res)

def encode(data):
    for charset in ['utf-8', 'shift_jis', 'euc-jp', 'iso2022-jp']:
        try: return data.decode(charset)
        except: pass

    raise EncodeError('Encoding failed.')

def is_dev_server():
    return os.environ.get('SERVER_SOFTWARE')[:11] == 'Development'

class RequestError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class EncodeError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)
