#!/usr/bin/env python
import logging
from decimal import Decimal, getcontext

log = logging.getLogger(__name__)

getcontext.prec=4

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
        if start_t < end_t:
            self.start_t = start_t
            self.end_t = end_t
        else:
            log.warn("Series starting time > ending time. Swapping both!")
            self.start_t = end_t
            self.end_t = start_t
        if resolution < 1:
            log.warn("Resolution was < 1 second. Re-setting it to 1 (minimal)")
            self.resolution = 1
        else:
            self.resolution = resolution 
        self.series = dict()

        self.stats_ready = False  # flag
        self.sum = Decimal(0)
        self.min = None
        self.max = None
        self.time_avg = None
        self.avg = None
        self.median = None
        self.scale_factor = Decimal(1) # 

    def set_scaling_factor(self, f):
        """ Sets a scale factor, which get's 
            multiplied with statistical values 
            of series (like min, max etc.). The
            original data of the series is kept unchanged.
            
            input: f, either str or Decimal 
        """
        if type(f) is Decimal:
            self.scale_factor= f
        elif type(f) is str:
            self.scale_factor = Decimal(f)

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
        
        if value == None:
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
            return None

        n_samples = len(self.series.keys())

        values = self.series.values()
        values.sort()
        self.min = values[0]
    
        max_samples = int((self.end_t - self.start_t)/ self.resolution)

        self.time_avg = self.sum/max_samples  # expecting self.sum to be of type Decimal or float
        self.avg = self.sum/n_samples
            

    def get_min(self):
        """ return minimal sample value."""
        if not self.stats_ready:
            self.__refresh_stats()
        if self.min == None: # don't use if not self.min as '0' will also match!!!
            return None
        return self.min * self.scale_factor

    def get_max(self):
        """ get maximum sample value. """
        if self.max == None:
            return None
        return self.max * self.scale_factor

    def get_sum(self): 
        return self.sum * self.scale_factor

    def get_average_bytime(self):
        """ returns average based on the time interval of time series. """
        if self.time_avg == None:
            return None
        return self.time_avg * self.scale_factor
        

    def get_average(self):
        """ returns average based on number of samples  of time series. """
        if not self.stats_ready:
            self.__refresh_stats()
        if self.avg == None:
            return None
        return self.avg * self.scale_factor

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
        if N == 0:
            return  None

        n = p/100.0 * (N-1) + 1
        if n == 1:
            return values[0] * self.scale_factor
        if n >= N:
            return values[N-1] * self.scale_factor
       
        pos = int(n) - 1
        #d = (n%1)
        d = Decimal(str(n%1))  #  
        val = values[pos] + d * (values[pos+1] - values[pos])
        return val * self.scale_factor       
        


    def get_median(self):
        """ returns median (aka sample mean) """
        return self.get_percentile(50)

    def get_series(self):
        """ return dictionary of {time: sample_value} """
        if self.scale_factor == 1:
            return self.series
        #   return map(lambda x: self.scale_factor * x, self.series)
        ndict = dict()
        for k, v in self.series.items():
            ndict[k] = v * self.scale_factor
        return ndict

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
        
        if not self.series:
            return None

        res = dict()
        res['median'] = self.get_median()
        res['lquartile'] = self.get_percentile(25)
        res['uquartile'] = self.get_percentile(75)
            
        iqr = res['uquartile'] - res['lquartile']
        lower_outliner_thresh = res['lquartile'] - Decimal('1.5') *iqr
        upper_outliner_thresh = res['uquartile'] + Decimal('1.5') *iqr
        
        lnot_outliner = res['lquartile']
        unot_outliner = res['uquartile']
        l_outliners = list()
        u_outliners = list()
        

        for val in self.get_series().values():
            if val >= res['lquartile'] and val <= res['uquartile']:
                continue
            if val < lower_outliner_thresh:
                l_outliners.append(val)
                continue
            if val > upper_outliner_thresh:
                u_outliners.append(val)
                continue
            if val < res['lquartile'] and val > lower_outliner_thresh:
                lnot_outliner = val
                continue 
            if val > res['uquartile'] and val < upper_outliner_thresh:
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

    def get_series2str(self, ref_dates=None):
        """ 
            returns a ',' (collon) delimited string of the values of the 
            series.
            For each date in 'ref)dates', which hasn't a corresponding value
            in the time series a ',_' (collon and underscore) characters will
            be entered instead.
            If ref_dates = None or empty, dates will be ignored.
            Notice, that only dates in ref_dates will be printed if ref_dates
            is given.
        """  
        str  = None

        series_dates = self.get_series().keys()
        series = self.get_series()

        if not ref_dates:
            series_dates.sort()
            for k in series_dates:
                if str:
                    str += ',%0.2f' % series[k]
                else:
                    str = '%0.2f' % series[k]

        else:
            ref_dates.sort()
            for k in ref_dates:
                if series.has_key(k):
                    val = '%0.2f' % series[k]
                else:
                    val = '_'
                if str:
                    str += ',%s' % val
                else:
                    str = '%s' % val
                        
        return str
            
        
        
if __name__ == '__main__':

    LOG_FILENAME = 'example.log'
    logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)


    ser = Series("test", 123, Decimal('234'))
    ser.add_sample(123, Decimal('0'))
    ser.add_sample(126, Decimal('0'))
    ser.add_sample(127, Decimal('0'))
    ser.add_sample(124, Decimal('0'))
    ser.add_sample(133, Decimal('0'))
    """ 
    ser.add_sample(124, Decimal('4'))
    ser.add_sample(125, Decimal('12'))
    ser.add_sample(128, Decimal('11'))
    ser.add_sample(129, Decimal('2'))
    ser.add_sample(132, Decimal('8'))
    ser.add_sample(232, Decimal('577'))
    ser.add_sample(149, Decimal('40'))
    ser.add_sample(151, Decimal('12'))
    ser.add_sample(152, Decimal('20'))
    ser.add_sample(153, Decimal('10'))
    ser.add_sample(154, Decimal('5'))
    ser2 = Series("test", 119, 230)
    ser2.add_sample(119, Decimal('-2'))
    ser2.add_sample(123, Decimal('-3'))
    ser2.add_sample(125, Decimal(5))
    ser2.add_sample(128, Decimal(7))
    
    ser.merge(ser2)
    """
    print 'min',  ser.get_min()
    print 'max', ser.get_max()
    print 'median', ser.get_median()
    print '20 percentile', ser.get_percentile(20)
    print '0 percentile', ser.get_percentile(0)
    print '100 percentile', ser.get_percentile(100)
    print '75 percentile', ser.get_percentile(75)
    if ser.get_average_bytime():
        print 'time avg %0.2f' %  ser.get_average_bytime()
    print 'avg', ser.get_average()
    print 'box-plot data', ser.get_box_plot()
    print ser.get_series2str()
    ser.set_scaling_factor(Decimal(1)/Decimal(60))
    print ser.get_series2str()
    
    """
    dates = range(120,234,1)
    ser.set_scaling_factor('0.5')
    print 'min',  ser.get_min()
    print 'max', ser.get_max()
    print 'median', ser.get_median()
    print '20 percentile', ser.get_percentile(20)
    print '0 percentile', ser.get_percentile(0)
    print '100 percentile', ser.get_percentile(100)
    print '75 percentile', ser.get_percentile(75)
    if ser.get_average_bytime():
        print 'time avg %0.2f' %  ser.get_average_bytime()
        print 'avg', ser.get_average()
    print 'box-plot data', ser.get_box_plot()
    print ser.get_series2str(dates)
    ser.set_scaling_factor('0.5')
    print ser.get_series()
    print ser.get_series2str(dates)
   """
