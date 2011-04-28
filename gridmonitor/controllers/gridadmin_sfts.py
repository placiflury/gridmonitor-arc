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


from sft.db import sft_meta
from sft.db import sft_schema
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
        
        for job in sft_meta.Session.query(sft_schema.SFTJob).all():

            if not job.cluster_name:
                continue

            cl_name = job.cluster_name
            sf_name = job.sft_test_name
            stat_ = job.status.lower()
            if 'failed' in stat_:
                stat = 'FAILED'
            elif 'fetched' in stat_:
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

        if cluster_name: 
            c.sft_jobs= sft_meta.Session.query(sft_schema.SFTJob).\
                filter(and_(sft_schema.SFTJob.sft_test_name == name, 
                 sft_schema.SFTJob.cluster_name == cluster_name)).order_by(desc(sft_schema.SFTJob.submissiontime))
        else: 
            c.sft_jobs= sft_meta.Session.query(sft_schema.SFTJob).\
                filter_by(sft_test_name = name).order_by(desc(sft_schema.SFTJob.submissiontime))

 
        return render('/derived/gridadmin/sfts/results.html')
    
    def show_details(self, name): 

        c.title = "Site Functional Test %s Details" % name
        c.menu_active = name + '_detail'  # little hack..
        c.heading = "Details of %s Site Functional test." % name
        c.sft = None 
        c.sft_vo_group= None
        c.sft_cluster_group = None
        c.sft_test_suit = None
        
        c.sft = sft_meta.Session.query(sft_schema.SFTTest).\
            filter_by(name = name).first()
        if not  c.sft:
            log.warn("SFT test '%s' does not exist anymore." % name)
        else:
            c.sft_vo_group = sft_meta.Session.query(sft_schema.VOGroup).\
                filter_by(name=c.sft.vo_group).first()
            if not c.sft_vo_group:
                log.warn("SFT test '%s' has no VOs specified." % name)

            c.sft_cluster_group = sft_meta.Session.query(sft_schema.ClusterGroup).\
                filter_by(name=c.sft.cluster_group).first()
            if not c.sft_cluster_group:
                log.warn("SFT test '%s' has no clusters specified." % name)

            c.sft_test_suit = sft_meta.Session.query(sft_schema.TestSuit).\
                filter_by(name=c.sft.test_suit).first()
            if not c.sft_test_suit:
                log.warn("SFT test '%s' has no tests specified." % name)


        return render('/derived/gridadmin/sfts/show_details.html')


    def user_mgnt(self):
        c.title = "Store the password of your  MyProxy certificate."
        c.menu_active = "SFTs User"
        c.heading = "Store the password of your MyProxy certificate."

        return render('/derived/gridadmin/sfts/form.html')
    
    def submit(self):
        c.title = "Storing the password of your  MyProxy certificate."
        c.menu_active = "-- none --"
        c.heading = "Storing the password of your MyProxy certificate."
        c 

        up = UserPool()
        
        if request.params.has_key('CB_browser_dn'):
            browser_dn = request.params['CB_browser_dn'].encode('utf-8')
            browser_pwd = request.params['browser_dn_pwd'].encode('utf-8')
            browser_pwd2 = request.params['browser_dn_pwd2'].encode('utf-8')
            if not browser_pwd:
                c.form_error= "You must enter a password for your '%s' certificate" % browser_dn
                return render('/derived/gridadmin/sfts/form.html')
                
            if browser_pwd != browser_pwd2:
                c.form_error =  "Your passwords for your '%s' certificate are not identical." % browser_dn
                return render('/derived/gridadmin/sfts/form.html')
        
            db_browser_user =  sft_meta.Session.query(sft_schema.User).filter_by(DN=browser_dn).first()
            if db_browser_user:
                up.reset_user_passwd(browser_dn,browser_pwd)
                c.browser_msg =  "Password for '%s' has been changed successfully" % browser_dn
            else:
                up.add_user(browser_dn, browser_pwd)
                c.browser_msg =  "'%s' has been added successfully" % browser_dn
        
        if request.params.has_key('CB_slcs_dn'):
            slcs_dn = request.params['CB_slcs_dn'].encode('utf-8')
            slcs_pwd =request.params['slcs_dn_pwd'].encode('utf-8')
            slcs_pwd2 = request.params['slcs_dn_pwd2'].encode('utf-8')

            if not slcs_pwd:
                c.form_error = "Your must enter a password for your '%s' certificate" % slcs_dn
                return render('/derived/gridadmin/sfts/form.html')
            if slcs_pwd != slcs_pwd2:
                c.form_error = "Your passwords for your '%s' certificate are not identical." % slcs_dn
                return render('/derived/gridadmin/sfts/form.html')
            
            db_slcs_user =  sft_meta.Session.query(sft_schema.User).filter_by(DN=slcs_dn).first()
            if db_slcs_user:
                up.reset_user_passwd(slcs_dn,slcs_pwd)
                c.slcs_msg =  "Password for '%s' has been changed successfully" % slcs_dn
            else:
                up.add_user(slcs_dn, slcs_pwd)
                c.slcs_msg =  "'%s' has been added successfully" % slcs_dn
 
        if not c.slcs_msg and not c.browser_msg: 
            return render('/derived/gridadmin/sfts/nochange.html')

        return render('/derived/gridadmin/sfts/change.html')


