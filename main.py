import os
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
import isourceview
import logging
logging.getLogger().setLevel(logging.DEBUG)

class MainPage(webapp.RequestHandler):
    def get(self):
        render(self.response, 'index.html')

class View(webapp.RequestHandler):
    def get(self):
        url = self.request.get('url')
        try:
            html = isourceview.request(url)
            html = isourceview.convert_html(html)
            self.__view(html)
        except isourceview.RequestError, message:
            self.__error(message, 400)
        except:
            self.__error('Internal server error', 500)

    def post(self):
        html = self.request.get('html')
        try:
            html = isourceview.convert_html(html)
            self.__view(html) 
        except:
            self.__error('Internal server error', 500)

    def __view(self, html):
        line_number = isourceview.get_line_number(html)
        render(self.response, 'view.html', {
            'formatted_html': html,
            'line_number':    line_number,
        })

    def __error(self, message, code):
        self.response.set_status(code)
        render(self.response, 'error.html', {'error': message})

class BmJS(webapp.RequestHandler):
    def get(self):
        render(self.response, 'bm_js.html')

class BmServer(webapp.RequestHandler):
    def get(self):
        render(self.response, 'bm_server.html')

def render(response, tpl, params={}):
    template.register_template_library('setvar')
    tpl_path = os.path.join(os.path.dirname(__file__), 'templates', tpl)
    html = template.render(tpl_path, params)
    response.out.write(html)

application = webapp.WSGIApplication([
    ('/',          MainPage),
    ('/view',      View),
    ('/bm_js',     BmJS),
    ('/bm_server', BmServer),
])

def main():
    run_wsgi_app(application)

        
if __name__ == "__main__":
    main()
