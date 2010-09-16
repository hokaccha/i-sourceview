import os, sys, urllib2, time
from urlparse import urlparse
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.api import memcache

class MainPage(webapp.RequestHandler):
    REQUEST_INTERVAL = 3

    def get(self):
        url = self.request.get('url')
        params = {}
        if url:
            params = self.__get_params(url) or {}
            tpl = 'code.html' if 'formatted_html' in params else 'error.html'
        else:
            tpl = 'index.html'

        render(self.response, tpl, params)

    def __get_params(self, url):
        try:
            response = self.__request(url)
            html = self.__encode(response.read())
            formatted_html = self.__format_html(html)
            line_number = self.__line_number(html)
        except:
            return { 'error':  sys.exc_info()[1] }

        return {
            'formatted_html': formatted_html,
            'line_number': line_number
        }

    def __request(self, url):
        domain = self.__get_domain(url)
        if not domain:
            raise RequestError('"%s" is invalid URI' % url)

        now = int(time.time())
        cached_time = memcache.get(domain)
        if cached_time:
            if now - cached_time > self.REQUEST_INTERVAL:
                memcache.set(domain, now)
            else:
                raise RequestError('Too many request same domain.')
        else:
            memcache.set(domain, now)

        response = urllib2.urlopen(url)

        return response

    @staticmethod
    def __encode(res_body):
        for charset in ['utf-8', 'shift_jis', 'euc-jp', 'iso2022-jp']:
            try: return res_body.decode(charset)
            except: pass

        raise 'Encoding failed.'

    @staticmethod
    def __format_html(html):
        f = lambda line: '<span>' + line + '</span>'
        lexer = get_lexer_by_name('html')
        format = HtmlFormatter(nowrap = True)
        lines = highlight(html, lexer, format).split('\n')[:-1]

        return '\n'.join( map(f, lines) )

    @staticmethod
    def __line_number(html):
        f = lambda num: '<span>' + str(num + 1) +'</span>';
        nums = range( len(html.split('\n')) )

        return '\n'.join( map(f, nums) )

    @staticmethod
    def __get_domain(url):
        return urlparse(url).netloc

class Bookmarklet(webapp.RequestHandler):
    def get(self):
        render(self.response, 'bm.html')

class About(webapp.RequestHandler):
    def get(self):
        render(self.response, 'about.html')

class RequestError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return str(self.value)

def render(response, tpl, params={}):
    template.register_template_library('setvar')
    tpl_path = os.path.join(os.path.dirname(__file__), 'templates', tpl)
    html = template.render(tpl_path, params)
    response.out.write(html)

application = webapp.WSGIApplication([
    ('/',      MainPage),
    ('/bm',    Bookmarklet),
    ('/about', About),
])

def main():
    run_wsgi_app(application)

        
if __name__ == "__main__":
    main()
