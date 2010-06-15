#from paste.script.util.logging_config import fileConfig
#fileConfig('/opt/GridMonitor/logging.ini')

from paste.deploy import loadapp
app = loadapp('config:/opt/monitor/deploy.ini')
