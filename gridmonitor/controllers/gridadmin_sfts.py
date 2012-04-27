# -*- coding: utf-8 -*-
import logging
from datetime import datetime
from sqlalchemy import desc
from sqlalchemy import and_

from pylons import tmpl_context as c
from pylons import session
from pylons import request
from pylons.templating import render_mako as render

from gridadmin import GridadminController

from sft.utils import helpers 
from sft.db.user_handler import UserPool

log = logging.getLogger(__name__)

class GridadminSftsController(GridadminController):

    def __init__(self):

        GridadminController.__init__(self)
        c.form_error = None
        c.user_client_dn = None
        c.user_slcs_dn = None

        if session.has_key('user_client_dn'):
            c.user_client_dn = session['user_client_dn']
        if session.has_key('user_slcs_obj'):
            slcs_obj = session['user_slcs_obj']
            c.user_slcs_dn = slcs_obj.get_dn()

    def index(self):
        c.title = "Monitoring System: VO/Grid Site Functional Tests"
        c.menu_active = "SFTs"
        c.heading = "Site Functional Tests"
        
        summary = dict() # cluster_name: dict(sft_name, dict(status), sub_time)
       
        for job in helpers.get_all_jobs():
            if not job.cluster_name:
                continue

            cl_name = job.cluster_name
            sf_name = job.sft_test_name
            stat_ = job.status.lower() # XXX PF. changes to be tested...
            if stat_ in ['failed', 'fetched_failed']:
                stat = 'FAILED'
            elif stat_ in ['fetched','success']:
                stat = 'OK'
            elif 'deleted' in stat_:
                stat = "DELETED"
            elif 'lrms' in stat_:
                stat = 'INLRMS'
            else:
                stat = 'OTHER'
            t_sub = job.submissiontime
       
            if not summary.has_key(cl_name):
                summary[cl_name] = dict()
            if not summary[cl_name].has_key(sf_name):   
                summary[cl_name][sf_name] = dict(
                        status=dict(),
                        sub_time = datetime.utcfromtimestamp(0))
        
            if not summary[cl_name][sf_name]['status'].has_key(stat):
                summary[cl_name][sf_name]['status'][stat] = 0

            summary[cl_name][sf_name]['status'][stat] += 1
           
            if t_sub > summary[cl_name][sf_name]['sub_time']:
                summary[cl_name][sf_name]['sub_time'] = t_sub

        c.sft_jobs_summary = summary 
        c.ordered_cluster_names  = summary.keys()
        c.ordered_cluster_names.sort()

        return render('/derived/gridadmin/sfts/index.html')


    def show(self, name, cluster_name = None): 
        if cluster_name:
            c.title = "Site Functional Test %s of cluster %s " % (name, cluster_name)
            c.heading = "Site Functional Test %s of cluster %s " % (name, cluster_name)
        else:
            c.title = "Site Functional Test %s" % name
            c.heading = "Site Functional Test %s" % name
        c.menu_active = name
        c.sft_name = name 
        c.sft_jobs = helpers.get_all_sft_jobs(name, cluster_name = cluster_name)

        return render('/derived/gridadmin/sfts/results.html')
    
    def show_details(self, name): 

        c.title = "Site Functional Test %s Details" % name
        c.menu_active = name + '_detail'  # little hack..
        c.heading = "Details of %s Site Functional test." % name
        c.sft = None 
        c.sft_vo_group = None
        c.sft_cluster_group = None
        c.sft_test_suit = None
        c.sft = helpers.get_job(name) 
        if not c.sft:
            log.warn("SFT test '%s' does not exist anymore." % name)
        else:
            c.sft_vo_group = helpers.get_sft_vo_group(c.sft.vo_group)
            if not c.sft_vo_group:
                log.warn("SFT test '%s' has no VOs specified." % name)

            c.sft_cluster_group = helpers.get_sft_cluster_group(c.sft.cluster_group)
            if not c.sft_cluster_group:
                log.warn("SFT test '%s' has no clusters specified." % name)

            c.sft_test_suit = helpers.get_sft_suit(c.sft.test_suit)
            if not c.sft_test_suit:
                log.warn("SFT test '%s' has no tests specified." % name)

        return render('/derived/gridadmin/sfts/show_details.html')


    def user_mgnt(self):
        c.title = "Store the password of your  MyProxy certificate."
        c.menu_active = "SFTs User"
        c.heading = "Store the password of your MyProxy certificate."

        return render('/derived/gridadmin/sfts/form.html')
    
    def submit(self):
        # XXX add an alias/displayname to add_user()
        c.title = "Storing the password of your  MyProxy certificate."
        c.menu_active = "-- none --"
        c.heading = "Storing the password of your MyProxy certificate."
        c.slcs_msg = None 
        c.browser_msg = None 

        up = UserPool()
        
        if request.params.has_key('CB_browser_dn'):
            browser_dn = request.params['CB_browser_dn']
            browser_pwd = request.params['browser_dn_pwd']
            browser_pwd2 = request.params['browser_dn_pwd2']
            if not browser_pwd:
                c.form_error = "You must enter a password for your '%s' certificate" % browser_dn
                return render('/derived/gridadmin/sfts/form.html')
                
            if browser_pwd != browser_pwd2:
                c.form_error =  "Your passwords for your '%s' certificate are not identical." % browser_dn
                return render('/derived/gridadmin/sfts/form.html')
        
            #db_browser_user =  sft_meta.Session.query(sft_schema.User).filter_by(DN=browser_dn).first()
            db_browser_user =  helpers.get_sft_user(browser_dn)
            if db_browser_user:
                up.reset_user_passwd(browser_dn, browser_pwd)
                c.browser_msg =  "Password for '%s' has been changed successfully" % browser_dn
            else:
                up.add_user(browser_dn, None, browser_pwd)
                c.browser_msg =  "'%s' has been added successfully" % browser_dn
        
        if request.params.has_key('CB_slcs_dn'):
            slcs_dn = request.params['CB_slcs_dn']
            slcs_pwd = request.params['slcs_dn_pwd']
            slcs_pwd2 = request.params['slcs_dn_pwd2']

            if not slcs_pwd:
                c.form_error = "Your must enter a password for your '%s' certificate" % slcs_dn
                return render('/derived/gridadmin/sfts/form.html')
            if slcs_pwd != slcs_pwd2:
                c.form_error = "Your passwords for your '%s' certificate are not identical." % slcs_dn
                return render('/derived/gridadmin/sfts/form.html')
            
            #db_slcs_user =  sft_meta.Session.query(sft_schema.User).filter_by(DN = slcs_dn).first()
            db_slcs_user =  helpers.get_sft_user(slcs_dn)

            if db_slcs_user:
                up.reset_user_passwd(slcs_dn, slcs_pwd)
                c.slcs_msg =  "Password for '%s' has been changed successfully" % slcs_dn
            else:
                up.add_user(slcs_dn, None,  slcs_pwd)
                c.slcs_msg =  "'%s' has been added successfully" % slcs_dn
 
        if not c.slcs_msg and not c.browser_msg: 
            return render('/derived/gridadmin/sfts/nochange.html')

        return render('/derived/gridadmin/sfts/change.html')


