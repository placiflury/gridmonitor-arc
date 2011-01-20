import cgi
import os.path

from paste.urlparser import StaticURLParser
from pylons.middleware import error_document_template, media_path

from gridmonitor.lib.base import *

class ErrorController(BaseController):
    """Generates error documents as and when they are required.

    The ErrorDocuments middleware forwards to ErrorController when error
    related status codes are returned from the application.

    This behaviour can be altered by changing the parameters to the
    ErrorDocuments middleware in your config/middleware.py file.
    
    """
    def document(self):
        """Render the error document"""
        my_template="""
        <html>
        <head><title>GridMonitor Error %(code)s</title></head>
        <body>
        <h1>Error %(code)s</h1>
        <p>%(message)s</p>
        </body>
        </html>
        """ 
        c.title = "GridMonitor Error Page"
        c.heading = "An Error Occured"
        c.prefix =request.environ.get('SCRIPT_NAME', '')
        c.code=cgi.escape(request.params.get('code', ''))
        c.message=cgi.escape(request.params.get('message', ''))
        
        return render('/base/error.html')

    def org_document(self):
        """Render the error document"""
        page = error_document_template % \
            dict(prefix=request.environ.get('SCRIPT_NAME', ''),
                 code=cgi.escape(request.params.get('code', '')),
                 message=cgi.escape(request.params.get('message', '')))
        return page

    def img(self, id):
        """Serve Pylons' stock images"""
        return self._serve_file(os.path.join(media_path, 'img'), id)

    def style(self, id):
        """Serve Pylons' stock stylesheets"""
        return self._serve_file(os.path.join(media_path, 'style'), id)

    def _serve_file(self, root, path):
        """Call Paste's FileApp (a WSGI application) to serve the file
        at the specified path
        """
        static = StaticURLParser(root)
        request.environ['PATH_INFO'] = '/%s' % path
        return static(request.environ, self.start_response)
