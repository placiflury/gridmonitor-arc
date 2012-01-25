import logging
import json
import calendar
import time

from pylons import request

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
            log.warn("Invalid  resolution '%s', changing to '%d'" % \
                (resolution, StatisticsController.VALID_RESOLUTIONS.keys(0) ))
            _resolution = StatisticsController.VALID_RESOLUTIONS.keys(0)
        else:
            _resolution = resolution

        if not vo_list:
            _vo_list = helpers.get_vo_names()
        else:
            _vo_list = vo_list

        _secs_res = StatisticsController.VALID_RESOLUTIONS[_resolution]


        start_t, end_t = helpers.get_sampling_interval(start_t, end_t, _secs_res)
        
        container = dict() 
        for vo in _vo_list:
            if not vo:
                vo_name = StatisticsController.NO_VO_NAME
            else:
                vo_name = vo
            
            nj = Series('n_jobs', start_t, end_t, _secs_res)
            wd= Series('wall_duration', start_t, end_t, _secs_res)
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
        key_order = ['_date']
        description = {'_date': ('Date','string')}
        pkey_order = []
        pdescription = {}

        for vo in _vo_list:
            if not vo:
                vo_name = StatisticsController.NO_VO_NAME
            else:
                vo_name = vo
            key_order.append(vo_name) 
            pkey_order.append(vo_name) 
            description[vo_name] = (vo_name,'number')
            pdescription[vo_name] = (vo_name,'number')

        log.debug("descr: %r, \n order: %r" % (description, key_order))
        ts_n_jobs = DataTable(description, key_order)
        ts_wall_duration = DataTable(description, key_order)
        pie_n_jobs = DataTable(pdescription, pkey_order)
        pie_wall_duration = DataTable(pdescription, pkey_order)

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
            wd= Series('wall_duration', start_t, end_t, _secs_res)
            container[vo_name] = dict()
           
            for rec in helpers.get_vo_acrecords(vo, start_t, end_t, _secs_res):
                nj.add_sample(rec.t_epoch, rec.n_jobs)
                wd.add_sample(rec.t_epoch, rec.wall_duration)
      
            container[vo_name]['n_job_series'] = nj.get_padded_series(ref_dates)
            container[vo_name]['wall_duration_series'] = wd.get_padded_series(ref_dates)
            # XXX pie-chart
            """
            container[vo_name]['n_job_tot'] += nj.get_sum()
            container[vo_name]['wall_duration_tot'] += wd.get_sum()
            """
        
        # populate json container
        date_pos  = 0
        for t_epoch in xrange(start_t, end_t, _secs_res):
            date_str = time.strftime("%d.%m.%Y", time.gmtime(t_epoch))
            
            _jobs_row = [date_str]
            _wall_row = [date_str]
            for _vo in key_order[1:]:
                _jobs_row.append(container[_vo]['n_job_series'][date_pos])
                _wall_row.append(container[_vo]['wall_duration_series'][date_pos])
                
            ts_n_jobs.add_row(_jobs_row)
            ts_wall_duration.add_row(_wall_row)
            date_pos += 1 
        log.info("XXX row: %r" % _jobs_row) 

        # XXX pie-charts missing

        ret = {'eff_start_time': time.strftime("%d.%m.%Y", time.gmtime(start_t)),
                'eff_end_time': time.strftime("%d.%m.%Y", time.gmtime(end_t)),
                'time_series_n_jobs': ts_n_jobs.get_json(),
                'time_series_wall_duration': ts_wall_duration.get_raw()}
        
        return json.dumps(ret) 

        
        

    """
    def get_vo_machine_stats(self, _start_t, _end_t, resolution,
            accumulated = False):

        cluster_list -- list of clusters to consider. If not list
                        passed, clusters of entire grid will be considered.
        _start_t -- starting date, may be 'shifted' in order        
                to match sampling rate (resolution)
        _end_t -- end date, may be 'shifted' in order to 
                match the sampling rate (resolution)

        resolution -- it's basically the sampling rate of the
                data. Valid values are: 86400 (day), 7 * 86400, 28 * 86400
        
        accumulated -- sum up values per VO 

        returns a json (dictionary) object
        start_t, end_t = helpers.get_sampling_interval(_start_t,_end_t, resolution)

        # get VO list
        _vos = helpers.get_vo_names()

        # get VO aggregates
        for rec in get_vo_acrecords(vo_name, start_t_epoch, end_t_epoch, resolution):
            pass        
        


        return json.dumps(get_nagios_summary(core_hosts, dates2utc = True))

    """
