#!/usr/bin/env python
from paste.deploy import loadapp
from paste.script.util.logging_config import fileConfig
fileConfig('/opt/smscg/monitor/deploy.ini')

from paste.deploy import loadapp
application = loadapp('config:/opt/smscg/monitor/deploy.ini')
