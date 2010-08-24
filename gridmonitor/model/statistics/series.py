#!/usr/bin/env python
import logging

log = logging.getLogger(__name__)


class Series(object):
    """
    Container to store the time series of a variable. 
    The containere provides means to get:

    - min sample value
    - max sample value
    - number of samples

    to compute:

    - average values from start time to end time of series
    - average values from existing samples 
    - sample mean -> median
    - upper and lower quartile
    - box-plot parameters

    additional fct:

    - merging with other time series container.
    
    Notice/Warning: sample values with same time will be summed up.

    """ 

    def __init__(self, name, start_t, end_t, resolution=1):
        """
        name: name of time series (variable)
        start_t: time series starting time in epoch
        end_t: time series ending time in epoch 
        resolution: in seconds (default 1 second)
        """
        self.name = name
        self.start_t = start_t
        self.end_t = end_t
        self.resolution = resolution 
        self.series = dict()

        self.stats_ready = False  # flag
        self.sum = 0
        self.min = None
        self.max = None
        self.time_avg = None
        self.avg = None
        self.median = None

    def get_name(self):
        return self.name

    def add_sample(self, t, value):
        """
        t: sample epoch time
        value: sample value
        Notice/Warning: sample values with same time will be summed up.
        """
        if (t < self.start_t) or (t > self.end_t):
            log.warn("Could not add sample to series '%s'. Not whithin time interval." % self.name)
            return
                
        if self.series.has_key(t):
            self.series[t] += value
        else:
            self.series[t] = value

        self.sum += value
        new_sample = self.series[t]
        
        if not self.max or self.max < new_sample:
            self.max = new_sample
        
        self.stats_ready = False


    def __refresh_stats(self):
        """ triggers (re-)computation of  statistics. """

        if not self.series:
            return

        n_samples = len(self.series.keys())

        values = self.series.values()
        values.sort()
        self.min = values[0]
    
        max_samples = int((self.end_t - self.start_t)/ self.resolution)

        self.time_avg = self.sum/float(max_samples)
        self.avg = self.sum/float(n_samples)
        self.median = self.get_percentile(50)
            

    def get_min(self):
        """ return minimal sample value."""
        if not self.stats_ready:
            self.__refresh_stats()
        return self.min

    def get_max(self):
        """ get maximum sample value. """
        return self.max

    def get_sum(self):
        return self.sum

    def get_average_bytime(self):
        """ returns average based on the time interval of time series. """
        return self.time_avg
        

    def get_average(self):
        """ returns average based on number of samples  of time series. """
        if not self.stats_ready:
            self.__refresh_stats()
        return self.avg

    def get_percentile(self, p):
        """ returns percentile of series. 
            Using method recommended by NIST (seek wikipedia) """

        # n = p/100 (N-1) + 1
        # v_p = v_1 for n =1
        # v_p = v_N for n = N
        # v_p = v_k + d(v_k + 1 - v_k)  for 1<n<N

        values = self.series.values()
        values.sort()
        
        N = len(self.series.keys())

        n = p/100.0 * (N-1) + 1
        if n == 1:
            return values[0]
        if n >= N:
            return values[N-1]
       
        pos = int(n) - 1
        d = (n%1)
 
        val = values[pos] + d * (values[pos+1] - values[pos])
        return val        
        


    def get_median(self):
        """ returns median (aka sample mean) """
        if not self.stats_ready:
            self.__refresh_stats()
        return self.median

    def get_series(self):
        """ return dictionary of {time: sample_value} """
        return self.series

    def get_box_plot(self):
        """ returns box-plot parmeters as a dictionary, with keys:
            - median: median
            - lqartile: lower quartile
            - uquartile: upper quartile
            - lnot_outliner: lowest non-outliner sample
            - unot_outliner: upper non-outliner sample
            - l_outliners: lower outliners
            - u_outliners: upper outliners
        """
        res = dict()
            
        res['median'] = self.get_median()
        res['lquartile'] = self.get_percentile(25)
        res['uquartile'] = self.get_percentile(75)
        
        iqr = res['uquartile'] - res['lquartile']
        lower_outliner_thresh = res['lquartile'] - 1.5 *iqr
        upper_outliner_thresh = res['uquartile'] + 1.5 *iqr
        
        lnot_outliner = self.median
        unot_outliner = self.median
        l_outliners = list()
        u_outliners = list()

        for val in self.series.values():
            if val >= res['lquartile'] and val <= res['uquartile']:
                continue
            if val < lower_outliner_thresh:
                l_outliners.append(val)
                continue
            if val > upper_outliner_thresh:
                u_outliners.append(val)
                continue
            if val < res['lquartile'] and val < lnot_outliner:
                lnot_outliner = val
                continue 
            if val > res['uquartile'] and val < unot_outliner:
                unot_outliner = val
        
        res['lnot_outliner'] = lnot_outliner     
        res['unot_outliner'] = unot_outliner     
        res['l_outliners'] = l_outliners
        res['u_outliners'] = u_outliners
                
        return res
 
    def merge(self, n_series):
        """ merges series with this one, if names are identical). 
            The starting and endtime of original series will be kept.
            Only series of same names can be merged
        """

        if n_series.get_name() != self.name:
            log.error("Cannot merge series of different names. %s != %s " % \
                 (self.name, n_series.get_name()))

        for t, v in n_series.get_series().items():
            self.add_sample(t, v)
        

"""
if __name__ == '__main__':

    ser = Series("test", 123, 234)
    ser.add_sample(124, 1)
    ser.add_sample(124, 1)
    ser.add_sample(125, 5)
    ser.add_sample(128, 7)
    ser.add_sample(129, 13)
    ser.add_sample(132, 17)
    ser.add_sample(232, 90)
    ser.add_sample(328, 18)
    
    ser2 = Series("test", 119, 230)
    ser2.add_sample(119, -2)
    ser2.add_sample(123, -3)
    ser2.add_sample(125, 5)
    ser2.add_sample(128, 7)
    
    ser.merge(ser2)


    print 'series', ser.get_series().values()    
    print 'min',  ser.get_min()
    print 'max', ser.get_max()
    print 'median', ser.get_median()
    print '20 percentile', ser.get_percentile(20)
    print '0 percentile', ser.get_percentile(0)
    print '100 percentile', ser.get_percentile(100)
    print '75 percentile', ser.get_percentile(75)
    print 'time avg', ser.get_average_bytime()
    print 'avg', ser.get_average()
    print 'box-plot data', ser.get_box_plot()


"""    




