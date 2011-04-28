import logging
import urllib
from pylons import tmpl_context as c
from pylons.templating import render_mako as render

from user import UserController

log = logging.getLogger(__name__)

class UserJobDetailsController(BaseController):

    def index(self,dn,jobid):
        # XXX avoid expensive re-collection of records of user jobs

        jobid = urllib.unquote_plus(jobid)
        
        c.title ="Details of job: %s" % jobid

        dn = urllib.unquote_plus(dn)
        jobs=g.get_user_jobs(dn)
            
        c.job = None
        for job in jobs:
            if job.get_globalid() == jobid:
                c.job = job
                break

        return render('/derived/user/jobs/details.html')
