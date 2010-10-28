#from paste.script.util.logging_config import fileConfig
#fileConfig('/opt/monitor/deploy.ini')
# or if you want to keep it separate
#fileConfig('/opt/monitor/logging.ini')

from paste.deploy import loadapp
application = loadapp('config:/opt/monitor/deploy.ini')
