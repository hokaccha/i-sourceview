import os, sys, urllib2, logging
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

class MainPage(webapp.RequestHandler):
    def get(self):
        params = self.__get_params()
        if 'source' in 'params':
            tpl = 'code.html'
        elif 'error' in params:
            tpl = 'error.html'
        else:
            tpl = 'index.html'
        path = os.path.join(os.path.dirname(__file__), tpl)
        self.response.out.write(template.render(path, params))

    def __get_params(self):
        params = dict()

        # get url from query
        url = params['url'] = self.request.get('url')
        if not url: return params

        # http request
        try:
            res = urllib2.urlopen(url)
        except:
            params['error'] = sys.exc_info()[1]
            return params

        # encodeing
        html = ''
        res_body = res.read()
        for charset in ['shift_jis', 'euc-jp', 'utf-8']:
            try:
                html = res_body.decode(charset)
                break
            except:
                pass
        if not html:
            params['error'] = sys.exc_info()[1]
            return params

        # set highlight
        lexer = get_lexer_by_name('html')
        format = HtmlFormatter(nowrap = True)
        source = map(
            lambda line: '<span>' + line + '</span>',
            highlight(html, lexer, format).split('\n')[:-1]
        )
        line_number = map(
            lambda line: '<span>' + str(line) +'</span>',
            range(1, len(source) + 1)
        )
        params = {
            'source': '\n'.join(source),
            'line_number': '\n'.join(line_number),
        }

        return params

class Bookmarklet(webapp.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'bm.html')
        self.response.out.write(template.render(path, {}))

class About(webapp.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'about.html')
        self.response.out.write(template.render(path, {}))
        
application = webapp.WSGIApplication([
    ('/', MainPage),
    ('/bm', Bookmarklet),
    ('/about', About),
])

def main():
    logging.getLogger().setLevel(logging.DEBUG)
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
