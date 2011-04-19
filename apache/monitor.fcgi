#!/usr/bin/env python
from paste.deploy import loadapp
from paste.script.util.logging_config import fileConfig

config_file ='/opt/smscg/monitor/deploy.ini'

# Load the WSGI application from the config file
wsgi_app = loadapp('config:'+config_file)
fileConfig(config_file)

# Deploy it using FastCGI
if __name__ == '__main__':
    from flup.server.fcgi import WSGIServer
    WSGIServer(wsgi_app).run()

