import logging
import json
import calendar
import time

from pylons import request
from pylons import session

from sgasaggregator.utils import helpers

from gridmonitor.lib.base import BaseController
from gridmonitor.lib.charts_table import DataTable
from gridmonitor.model.statistics.series import Series


log = logging.getLogger(__name__)

class StatisticsController(BaseController):
    
    VALID_RESOLUTIONS = {'day': 86400, 
                        'week': 604800, 
                        'month': 2419200}
    NO_VO_NAME = 'NO_VO'
    
    SCALING_FACTOR = 1/3600.0 # 1/60 minutes, 1/3600 hours 
    

    def _get_json_params(self):
        """ extracts json parameters from 
            request (used to get params sent
            by ajax)
        """

        md = request.params  # UnicodeMultiDict
        # convert to simple dict
        params = {}
        for k in md.keys():
            if k[-2:] == '[]': # got list 
                params[k[:-2]] = md.getall(k)
            else:
                params[k] = md.get(k)

        log.debug("Got following json params: >%s<" % params)
        return params


    def get_vos_stats(self, start_t = None, end_t = None, 
            resolution = None, vo_list = None):
        """
        Getting VO usage statistics for entire grid for 
        given vo_list starting from '_start_t' and ending '_end_t', at
        resoution {day | week| month}.
        Notice: 
        - the _start_t, _end_t times may be adjusted
        to neatly fit 'resolution'.
        - if no vo_list specified, all VOs will be queried.
        - valid resolution values are 'day', 'week','month'
        
        returns a json object with the following entries
            eff_start_time : start_time_epoch
            eff_end_time : end_time_epoch
            vos_series[vo_name]['n_job_series']
            vos_series[vo_name]['n_job_tot']
            vos_series[vo_name]['wall_duration_series']
            vos_series[vo_name]['wall_duration_tot']
        """
        if  not start_t:
            args = self._get_json_params()
            start_t = calendar.timegm(time.strptime(args['start_t'],'%d.%m.%Y'))
            end_t = calendar.timegm(time.strptime(args['end_t'],'%d.%m.%Y'))

            try:
                resolution = args['resolution']
            except: 
                resolution = 'day'
            try:
                vo_list = args['vo_list']
            except:
                vo_list = None


        if resolution not in StatisticsController.VALID_RESOLUTIONS.keys():
            log.warn("Invalid  resolution '%s', changing to '%s'" % \
                (resolution, StatisticsController.VALID_RESOLUTIONS.keys(0) ))
            resolution = StatisticsController.VALID_RESOLUTIONS.keys(0)

        if not vo_list:
            _vo_list = helpers.get_vo_names()
        else:
            _vo_list = vo_list

        _secs_res = StatisticsController.VALID_RESOLUTIONS[resolution]

        start_t, end_t = helpers.get_sampling_interval(start_t, end_t, _secs_res)
        
        container = dict() 
        for vo in _vo_list:
            if not vo:
                vo_name = StatisticsController.NO_VO_NAME
            else:
                vo_name = vo
            
            nj = Series('n_jobs', start_t, end_t, _secs_res)
            wd = Series('wall_duration', start_t, end_t, _secs_res)
            container[vo_name] = dict()
             
            for rec in helpers.get_vo_acrecords(vo, start_t, end_t, _secs_res):
                nj.add_sample(rec.t_epoch, rec.n_jobs)
                wd.add_sample(rec.t_epoch, rec.wall_duration)
       
            container[vo_name]['n_job_series'] = nj.get_series()
            container[vo_name]['wall_duration_series'] = wd.get_series()
            container[vo_name]['n_job_tot'] = nj.get_sum()
            container[vo_name]['wall_duration_tot'] = wd.get_sum()
        
        ret = {'eff_start_time': time.strftime("%d.%m.%Y", time.gmtime(start_t)),
                'eff_end_time': time.strftime("%d.%m.%Y", time.gmtime(end_t)),
                'vos_series': container}
        
        return json.dumps(ret) 

    def gc_user_cluster_stats(self):
        """
        Getting cluster usage statistics for entire grid
        from '_start_t' and ending '_end_t', at
        resoution {day | week| month} (passed by HTTP POST).
        Notice: 
        - the _start_t, _end_t times may be adjusted
        to neatly fit 'resolution'.
        - valid resolution values are 'day', 'week','month'
        
        returns a json object with the following entries
            eff_start_time : start_time_epoch
            eff_end_time : end_time_epoch
            ....
        """
        # get user DNs
        dns = []
        if session.has_key('user_slcs_obj'):
            user_slcs_obj = session['user_slcs_obj']
            dns.append(user_slcs_obj.get_dn())
        if session.has_key('user_client_dn'):
            dns.append(session['user_client_dn'])
        
        # get HTTP POST parameters
        args = self._get_json_params()
        start_t = calendar.timegm(time.strptime(args['start_t'],'%d.%m.%Y'))
        end_t = calendar.timegm(time.strptime(args['end_t'],'%d.%m.%Y'))
        try:
            resolution = args['resolution']
            if resolution not in StatisticsController.VALID_RESOLUTIONS.keys():
                log.warn("Invalid  resolution '%s', changing to 'day'" % resolution)
                resolution = 'day'
        except: 
            resolution = 'day'

        _cluster_list = helpers.get_cluster_names()

        # convert resolution to equivalent in seconds
        _secs_res = StatisticsController.VALID_RESOLUTIONS[resolution]
        start_t, end_t = helpers.get_sampling_interval(start_t, end_t, _secs_res)

        # json containers for time series plots and pie chart plots
        
        _key_order = []
        _descr = {}

        for cname in _cluster_list:
            _key_order.append(cname) 
            _descr[cname] = (cname,'number')

        _key_order.sort()
        _key_order.reverse() # for alphabetical order in google charts
        key_order = ['_date'] + _key_order
        
        descr = _descr.copy()
        descr ['_date'] =  ('Date','string')
        log.debug("descr: %r, \n order: %r" % (descr, key_order))
        
        ts_n_jobs = DataTable(descr, key_order)
        ts_wall_duration = DataTable(descr, key_order)
        
        pkey_order = ['cluster_name','sum']
        pdescr = {'cluster_name': ('cluster', 'string'),
                    'sum': ('Sum','number')}

        pie_n_jobs = DataTable(pdescr, pkey_order)
        pie_wall_duration = DataTable(pdescr, pkey_order)

        # create date series (shifted to fit 23:59:59 as stored in DB), still given in epoch time
        ref_start_t = start_t + _secs_res  - 1
        ref_end_t = end_t + _secs_res - 1
        ref_dates = range(ref_start_t, ref_end_t, _secs_res)


        container = {}
        for cname in _cluster_list:
            
            nj = Series('n_jobs', start_t, end_t, _secs_res)
            wd =  Series('wall_duration', start_t, end_t, _secs_res)
            wd.set_scaling_factor(StatisticsController.SCALING_FACTOR)

            container[cname] = dict()
            container[cname]['n_job_tot'] = 0
            container[cname]['wall_duration_tot'] = 0
            for dn in dns: 
                for rec in helpers.get_cluster_user_acrecords(cname, dn, start_t, end_t, _secs_res):
                    nj.add_sample(rec.t_epoch, rec.n_jobs)
                    wd.add_sample(rec.t_epoch, rec.wall_duration)
      
            container[cname]['n_job_series'] = nj.get_padded_series(ref_dates)
            container[cname]['wall_duration_series'] = wd.get_padded_series(ref_dates)
            container[cname]['n_job_tot'] += nj.get_sum()
            container[cname]['wall_duration_tot'] += wd.get_sum()
        
        # populate json container
        date_pos  = 0
        for t_epoch in xrange(start_t, end_t, _secs_res):
            date_str = time.strftime("%d.%m.%Y", time.gmtime(t_epoch))
            
            _jobs_row = [date_str]
            _wall_row = [date_str]
            for cname in _key_order:
                _jobs_row.append(container[cname]['n_job_series'][date_pos])
                _wall_row.append(container[cname]['wall_duration_series'][date_pos])
                
            ts_n_jobs.add_row(_jobs_row)
            ts_wall_duration.add_row(_wall_row)
            date_pos += 1 

        # pie-charts 
        for cname in _key_order:
            pie_n_jobs.add_row(cname, round(container[cname]['n_job_tot'], 2))
            pie_wall_duration.add_row(cname, round(container[cname]['wall_duration_tot'], 2))
            

        ret = {'eff_start_time': time.strftime("%d.%m.%Y", time.gmtime(start_t)),
                'eff_end_time': time.strftime("%d.%m.%Y", time.gmtime(end_t)),
                'time_series_n_jobs': ts_n_jobs.get_json(),
                'time_series_wall_duration': ts_wall_duration.get_json(),
                'pie_n_jobs' : pie_n_jobs.get_json(),
                'pie_wall_duration': pie_wall_duration.get_json()}
        
        return json.dumps(ret) 
    

    
    def gc_vos_stats(self):
        """
        Getting VO usage statistics for entire grid for 
        given vo_list starting from '_start_t' and ending '_end_t', at
        resoution {day | week| month} (passed by HTTP POST).
        Notice: 
        - the _start_t, _end_t times may be adjusted
        to neatly fit 'resolution'.
        - if no vo_list specified, all VOs will be queried.
        - valid resolution values are 'day', 'week','month'
        
        returns a json object with the following entries
            eff_start_time : start_time_epoch
            eff_end_time : end_time_epoch
            ....
        """
        # get HTTP POST parameters
        args = self._get_json_params()
        start_t = calendar.timegm(time.strptime(args['start_t'],'%d.%m.%Y'))
        end_t = calendar.timegm(time.strptime(args['end_t'],'%d.%m.%Y'))
        try:
            resolution = args['resolution']
            if resolution not in StatisticsController.VALID_RESOLUTIONS.keys():
                log.warn("Invalid  resolution '%s', changing to 'day'" % resolution)
                resolution = 'day'
        except: 
            resolution = 'day'
        try:
            vo_list = args['vo_list']
        except:
            vo_list = None

        # if no VO list given, use all known
        if not vo_list:
            _vo_list = helpers.get_vo_names()
        else:
            _vo_list = vo_list

        # convert resolution to equivalent in seconds
        _secs_res = StatisticsController.VALID_RESOLUTIONS[resolution]

        start_t, end_t = helpers.get_sampling_interval(start_t, end_t, _secs_res)

        # json containers for time series plots and pie chart plots
        _key_order = []
        _descr = {}

        for vo in _vo_list:
            if not vo:
                vo_name = StatisticsController.NO_VO_NAME
            else:
                vo_name = vo
            _key_order.append(vo_name) 
            _descr[vo_name] = (vo_name,'number')

        _key_order.sort()
        _key_order.reverse() # for alphabetical order in google charts
        key_order = ['_date'] + _key_order
        
        descr = _descr.copy()
        descr ['_date'] =  ('Date','string')
        log.debug("descr: %r, \n order: %r" % (descr, key_order))
        
        ts_n_jobs = DataTable(descr, key_order)
        ts_wall_duration = DataTable(descr, key_order)
        
        pkey_order = ['vo_name','sum']
        pdescr = {'vo_name': ('VO', 'string'),
                    'sum': ('Sum','number')}

        pie_n_jobs = DataTable(pdescr, pkey_order)
        pie_wall_duration = DataTable(pdescr, pkey_order)

        # create date series (shifted to fit 23:59:59 as stored in DB), still given in epoch time
        ref_start_t = start_t + _secs_res  - 1
        ref_end_t = end_t + _secs_res - 1
        ref_dates = range(ref_start_t, ref_end_t, _secs_res)

        container = {}
        for vo in _vo_list:
            if not vo:
                vo_name = StatisticsController.NO_VO_NAME
            else:
                vo_name = vo
            
            nj = Series('n_jobs', start_t, end_t, _secs_res)
            wd =  Series('wall_duration', start_t, end_t, _secs_res)
            wd.set_scaling_factor(StatisticsController.SCALING_FACTOR)

            container[vo_name] = dict()
            container[vo_name]['n_job_tot'] = 0
            container[vo_name]['wall_duration_tot'] = 0
           
            for rec in helpers.get_vo_acrecords(vo, start_t, end_t, _secs_res):
                nj.add_sample(rec.t_epoch, rec.n_jobs)
                wd.add_sample(rec.t_epoch, rec.wall_duration)
      
            container[vo_name]['n_job_series'] = nj.get_padded_series(ref_dates)
            container[vo_name]['wall_duration_series'] = wd.get_padded_series(ref_dates)
            container[vo_name]['n_job_tot'] += nj.get_sum()
            container[vo_name]['wall_duration_tot'] += wd.get_sum()
        
        # populate json container
        date_pos  = 0
        for t_epoch in xrange(start_t, end_t, _secs_res):
            date_str = time.strftime("%d.%m.%Y", time.gmtime(t_epoch))
            
            _jobs_row = [date_str]
            _wall_row = [date_str]
            for _vo in _key_order:
                _jobs_row.append(container[_vo]['n_job_series'][date_pos])
                _wall_row.append(container[_vo]['wall_duration_series'][date_pos])
                
            ts_n_jobs.add_row(_jobs_row)
            ts_wall_duration.add_row(_wall_row)
            date_pos += 1 

        # pie-charts
        for _vo in _key_order:
            pie_n_jobs.add_row(_vo, round(container[_vo]['n_job_tot'], 2))
            pie_wall_duration.add_row(_vo, round(container[_vo]['wall_duration_tot'], 2))
            

        ret = {'eff_start_time': time.strftime("%d.%m.%Y", time.gmtime(start_t)),
                'eff_end_time': time.strftime("%d.%m.%Y", time.gmtime(end_t)),
                'time_series_n_jobs': ts_n_jobs.get_json(),
                'time_series_wall_duration': ts_wall_duration.get_json(),
                'pie_n_jobs' : pie_n_jobs.get_json(),
                'pie_wall_duration': pie_wall_duration.get_json()}
        
        return json.dumps(ret) 
    
    def gc_cluster_stats(self):
        """
        Getting cluster usage statistics for entire grid
        from '_start_t' and ending '_end_t', at
        resoution {day | week| month} (passed by HTTP POST).
        Notice: 
        - the _start_t, _end_t times may be adjusted
        to neatly fit 'resolution'.
        - valid resolution values are 'day', 'week','month'
        
        returns a json object with the following entries
            eff_start_time : start_time_epoch
            eff_end_time : end_time_epoch
            ....
        """
        # get HTTP POST parameters
        args = self._get_json_params()
        start_t = calendar.timegm(time.strptime(args['start_t'],'%d.%m.%Y'))
        end_t = calendar.timegm(time.strptime(args['end_t'],'%d.%m.%Y'))
        try:
            resolution = args['resolution']
            if resolution not in StatisticsController.VALID_RESOLUTIONS.keys():
                log.warn("Invalid  resolution '%s', changing to 'day'" % resolution)
                resolution = 'day'
        except: 
            resolution = 'day'

        _cluster_list = helpers.get_cluster_names()

        # convert resolution to equivalent in seconds
        _secs_res = StatisticsController.VALID_RESOLUTIONS[resolution]
        start_t, end_t = helpers.get_sampling_interval(start_t, end_t, _secs_res)

        # json containers for time series plots and pie chart plots
        
        _key_order = []
        _descr = {}

        for cname in _cluster_list:
            _key_order.append(cname) 
            _descr[cname] = (cname,'number')

        _key_order.sort()
        _key_order.reverse() # for alphabetical order in google charts
        key_order = ['_date'] + _key_order
        
        descr = _descr.copy()
        # pdescr = _descr.copy()
        descr ['_date'] =  ('Date','string')
        log.debug("descr: %r, \n order: %r" % (descr, key_order))
        
        ts_n_jobs = DataTable(descr, key_order)
        ts_wall_duration = DataTable(descr, key_order)
        
        pkey_order = ['cluster_name','sum']
        pdescr = {'cluster_name': ('cluster', 'string'),
                    'sum': ('Sum','number')}

        pie_n_jobs = DataTable(pdescr, pkey_order)
        pie_wall_duration = DataTable(pdescr, pkey_order)

        # create date series (shifted to fit 23:59:59 as stored in DB), still given in epoch time
        ref_start_t = start_t + _secs_res  - 1
        ref_end_t = end_t + _secs_res - 1
        ref_dates = range(ref_start_t, ref_end_t, _secs_res)

        container = {}
        for cname in _cluster_list:
            
            nj = Series('n_jobs', start_t, end_t, _secs_res)
            wd =  Series('wall_duration', start_t, end_t, _secs_res)
            wd.set_scaling_factor(StatisticsController.SCALING_FACTOR)

            container[cname] = dict()
            container[cname]['n_job_tot'] = 0
            container[cname]['wall_duration_tot'] = 0
           
            for rec in helpers.get_cluster_acrecords(cname, start_t, end_t, _secs_res):
                nj.add_sample(rec.t_epoch, rec.n_jobs)
                wd.add_sample(rec.t_epoch, rec.wall_duration)
      
            container[cname]['n_job_series'] = nj.get_padded_series(ref_dates)
            container[cname]['wall_duration_series'] = wd.get_padded_series(ref_dates)
            container[cname]['n_job_tot'] += nj.get_sum()
            container[cname]['wall_duration_tot'] += wd.get_sum()
        
        # populate json container
        date_pos  = 0
        for t_epoch in xrange(start_t, end_t, _secs_res):
            date_str = time.strftime("%d.%m.%Y", time.gmtime(t_epoch))
            
            _jobs_row = [date_str]
            _wall_row = [date_str]
            for cname in _key_order:
                _jobs_row.append(container[cname]['n_job_series'][date_pos])
                _wall_row.append(container[cname]['wall_duration_series'][date_pos])
                
            ts_n_jobs.add_row(_jobs_row)
            ts_wall_duration.add_row(_wall_row)
            date_pos += 1 

        # pie-charts 
        for cname in _key_order:
            pie_n_jobs.add_row(cname, round(container[cname]['n_job_tot'], 2))
            pie_wall_duration.add_row(cname, round(container[cname]['wall_duration_tot'], 2))
            

        ret = {'eff_start_time': time.strftime("%d.%m.%Y", time.gmtime(start_t)),
                'eff_end_time': time.strftime("%d.%m.%Y", time.gmtime(end_t)),
                'time_series_n_jobs': ts_n_jobs.get_json(),
                'time_series_wall_duration': ts_wall_duration.get_json(),
                'pie_n_jobs' : pie_n_jobs.get_json(),
                'pie_wall_duration': pie_wall_duration.get_json()}
        
        return json.dumps(ret) 


    def _gc_cluster_vos_stats(self, cluster_name, vo_list,  resolution, start_t, end_t):
        """
        Returns dictionary with usage statistics for given cluster 
        for all VOs, starting from start_t (epoch) to end_t (epoch)
        at given resolution.
        params:  cluster_name - name of cluster
                vo_list - list of vos to consider
                resolution - resolution must be of defined by 
                        VALID_RESOLUTIONS (eg. 'day', 'week', 'month'
                start_t - start time of time series, in epoch time
                end_t   - end time of time series, in epoch time
        """
        _key_order = []
        _descr = {}

        for vo in vo_list:
            if not vo:
                vo_name = StatisticsController.NO_VO_NAME
            else:
                vo_name = vo
            _key_order.append(vo_name) 
            _descr[vo_name] = (vo_name,'number')

        _key_order.sort()
        _key_order.reverse() # for alphabetical order in google charts
        key_order = ['_date'] + _key_order
        
        descr = _descr.copy()
        descr ['_date'] =  ('Date','string')
        log.debug("descr: %r, \n order: %r" % (descr, key_order))
        
        ts_n_jobs = DataTable(descr, key_order)
        ts_wall_duration = DataTable(descr, key_order)
        
        pkey_order = ['cluster_name','sum']
        pdescr = {'cluster_name': ('VO', 'string'),
                    'sum': ('Sum','number')}

        pie_n_jobs = DataTable(pdescr, pkey_order)
        pie_wall_duration = DataTable(pdescr, pkey_order)

        _secs_res = StatisticsController.VALID_RESOLUTIONS[resolution]
        start_t, end_t = helpers.get_sampling_interval(start_t, end_t, _secs_res)

        nj = Series('n_jobs', start_t, end_t, _secs_res)
        wd =  Series('wall_duration', start_t, end_t, _secs_res)
        
        # create date series (shifted to fit 23:59:59 as stored in DB), still given in epoch time
        ref_start_t = start_t + _secs_res  - 1
        ref_end_t = end_t + _secs_res - 1
        ref_dates = range(ref_start_t, ref_end_t, _secs_res)
        
        container = {}
        for vo in vo_list:
            if not vo:
                vo_name = StatisticsController.NO_VO_NAME
            else:
                vo_name = vo
            
            nj = Series('n_jobs', start_t, end_t, _secs_res)
            wd =  Series('wall_duration', start_t, end_t, _secs_res)
            wd.set_scaling_factor(StatisticsController.SCALING_FACTOR)

            container[vo_name] = dict()
            container[vo_name]['n_job_tot'] = 0
            container[vo_name]['wall_duration_tot'] = 0

            for rec in helpers.get_cluster_vo_acrecords(cluster_name, vo, start_t, end_t, _secs_res): 
                nj.add_sample(rec.t_epoch, rec.n_jobs)
                wd.add_sample(rec.t_epoch, rec.wall_duration)
      
            container[vo_name]['n_job_series'] = nj.get_padded_series(ref_dates)
            container[vo_name]['wall_duration_series'] = wd.get_padded_series(ref_dates)
            container[vo_name]['n_job_tot'] += nj.get_sum()
            container[vo_name]['wall_duration_tot'] += wd.get_sum()
        
        # populate json container
        date_pos  = 0
        for t_epoch in xrange(start_t, end_t, _secs_res):
            date_str = time.strftime("%d.%m.%Y", time.gmtime(t_epoch))
            
            _jobs_row = [date_str]
            _wall_row = [date_str]
            for _vo in _key_order:
                _jobs_row.append(container[_vo]['n_job_series'][date_pos])
                _wall_row.append(container[_vo]['wall_duration_series'][date_pos])
                
            ts_n_jobs.add_row(_jobs_row)
            ts_wall_duration.add_row(_wall_row)
            date_pos += 1 

        # pie-charts
        for _vo in _key_order:
            pie_n_jobs.add_row(_vo, round(container[_vo]['n_job_tot'], 2))
            pie_wall_duration.add_row(_vo, round(container[_vo]['wall_duration_tot'], 2))
            

        ret = { 'time_series_n_jobs': ts_n_jobs.get_json(),
                'time_series_wall_duration': ts_wall_duration.get_json(),
                'pie_n_jobs' : pie_n_jobs.get_json(),
                'pie_wall_duration': pie_wall_duration.get_json()}
        
        return ret 
    
    def gc_clusters_vos_stats(self):
        """
        Getting vo per cluster usage statistics for entire grid
        from '_start_t' and ending '_end_t', at
        resoution {day | week| month} (passed by HTTP POST).
        Notice: 
        - the _start_t, _end_t times may be adjusted
        to neatly fit 'resolution'.
        - valid resolution values are 'day', 'week','month'
        
        returns a json object with the following entries
            eff_start_time : start_time_epoch
            eff_end_time : end_time_epoch
            ....
        """
        # get HTTP POST parameters
        args = self._get_json_params()
        start_t = calendar.timegm(time.strptime(args['start_t'],'%d.%m.%Y'))
        end_t = calendar.timegm(time.strptime(args['end_t'],'%d.%m.%Y'))
        try:
            resolution = args['resolution']
            if resolution not in StatisticsController.VALID_RESOLUTIONS.keys():
                log.warn("Invalid  resolution '%s', changing to 'day'" % resolution)
                resolution = 'day'
        except: 
            resolution = 'day'

        if args.has_key('cluster_list'): # list passed as 'u"['cluster1','cluster2',...]" string
            raw = args['cluster_list'].encode('utf-8').strip('[]').split(',')
            cluster_list = map(lambda x: x.strip('\' '), raw)
        else:
            cluster_list = helpers.get_cluster_names()
        cluster_list.sort()

        vo_list = helpers.get_vo_names()
        vo_list.sort()

        cluster_container = {}

        for cluster_name in cluster_list:
            cname = cluster_name.replace('.','_')
            cluster_container[cname] = self._gc_cluster_vos_stats(cluster_name, vo_list,  resolution, start_t, end_t)

        ret = {'eff_start_time': time.strftime("%d.%m.%Y", time.gmtime(start_t)),
                'eff_end_time': time.strftime("%d.%m.%Y", time.gmtime(end_t)),
                'cluster_container': cluster_container,
                'clusters': cluster_list}
        return json.dumps(ret) 
