import cgi

from paste.urlparser import PkgResourcesParser
from pylons import request
from pylons import tmpl_context as c
from pylons.templating import render_mako as render
from pylons.controllers.util import forward
from pylons.middleware import error_document_template
from webhelpers.html.builder import literal

from gridmonitor.lib.base import BaseController

class ErrorController(BaseController):

    """Generates error documents as and when they are required.

    The ErrorDocuments middleware forwards to ErrorController when error
    related status codes are returned from the application.

    This behaviour can be altered by changing the parameters to the
    ErrorDocuments middleware in your config/middleware.py file.

    """

    def document(self):
        """Render the error document"""
        my_template = """
        <html>
        <head><title>GridMonitor Error %(code)s</title></head>
        <body>
        <h1>Error %(code)s</h1>
        <p>%(message)s</p>
        </body>
        </html>
        """ 

        resp = request.environ.get('pylons.original_response')
        content = literal(resp.body) or cgi.escape(request.GET.get('message', ''))

        c.title = "GridMonitor Error Page"
        c.heading = "An Error Occurred"
        c.prefix = request.environ.get('SCRIPT_NAME', '')
        c.code = cgi.escape(request.params.get('code', str(resp.status_int)))
        c.message = content
        
        return render('/base/error.html')


    def org_document(self):
        """Render the error document"""
        resp = request.environ.get('pylons.original_response')
        content = literal(resp.body) or cgi.escape(request.GET.get('message', ''))
        page = error_document_template % \
            dict(prefix=request.environ.get('SCRIPT_NAME', ''),
                 code=cgi.escape(request.GET.get('code', str(resp.status_int))),
                 message=content)
        return page

    def img(self, id):
        """Serve Pylons' stock images"""
        return self._serve_file('/'.join(['media/img', id]))

    def style(self, id):
        """Serve Pylons' stock stylesheets"""
        return self._serve_file('/'.join(['media/style', id]))

    def _serve_file(self, path):
        """Call Paste's FileApp (a WSGI application) to serve the file
        at the specified path
        """
        request.environ['PATH_INFO'] = '/%s' % path
        return forward(PkgResourcesParser('pylons', 'pylons'))

