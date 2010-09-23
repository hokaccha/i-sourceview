import os
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from isourceview.app import App
import logging
logging.getLogger().setLevel(logging.DEBUG)

class MainPage(webapp.RequestHandler):
    def get(self):
        render(self.response, 'index.html')

class View(webapp.RequestHandler):
    def __init__(self):
        self.app = App()

    def get(self):
        url = self.request.get('url')
        self.app.process(url = url)
        if self.app.error:
            self.response.set_status(500)
            render(self.response, 'error.html', {'error': self.app.error})
        else:
            render(self.response, 'view.html', {
                'formatted_html': App.spanize(self.app.formatted_html),
                'line_number':    App.spanize(self.app.line_number),
            })
    def post(self):
        html = self.request.get('html')
        self.app.process(html = html)
        if self.app.error:
            self.response.set_status(500)
            render(self.response, 'error.html', {'error': self.app.error})
        else:
            render(self.response, 'view.html', {
                'formatted_html': App.spanize(self.app.formatted_html),
                'line_number':    App.spanize(self.app.line_number),
            })

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
