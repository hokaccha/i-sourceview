import os
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from isourceview.app import App
import logging
logging.getLogger().setLevel(logging.DEBUG)

class MainPage(webapp.RequestHandler):
    def get(self):
        url = self.request.get('url')
        if not url:
            render(self.response, 'index.html')
            return

        app = App(url = url)
        app.process()
        if app.error:
            self.response.set_status(500)
            render(self.response, 'error.html', {'error': app.error})
        else:
            render(self.response, 'code.html', {
                'formatted_html': App.spanize(app.formatted_html),
                'line_number':    App.spanize(app.line_number),
            })
    def post(self):
        html = self.request.get('html')
        app = App(html = html)
        app.process()
        if app.error:
            self.response.set_status(500)
            render(self.response, 'error.html', {'error': app.error})
        else:
            render(self.response, 'code.html', {
                'formatted_html': App.spanize(app.formatted_html),
                'line_number':    App.spanize(app.line_number),
            })

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
    run_wsgi_app(application)

        
if __name__ == "__main__":
    main()
