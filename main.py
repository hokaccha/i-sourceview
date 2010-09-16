import os, sys, urllib2, logging
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

class MainPage(webapp.RequestHandler):
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

    @staticmethod
    def __request(url):
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

    def __get_domain():
        pass

class Bookmarklet(webapp.RequestHandler):
    def get(self):
        render(self.response, 'bm.html')

class About(webapp.RequestHandler):
    def get(self):
        render(self.response, 'about.html')

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
    logging.getLogger().setLevel(logging.DEBUG)
    run_wsgi_app(application)

        
if __name__ == "__main__":
    main()
