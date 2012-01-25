import json 

class DataTableError(Exception):
    """
    Generic Exception for DataTable errors. 
    Attributes:
        expression -- input expression in which error occurred
        message -- explanation of error 
    """
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message
        Exception.__init__(self)

    def __str__(self):
        return self.message

class DataTableTypeError(DataTableError):
    """ Raised for data type errors """
    pass

class DataTableInsertError(DataTableError):
    """ Raised for insertion errors, typically 
        for mismatch of number of cells to enter
        and schema.
    """
    pass


class DataTable(object):


    def __init__(self, schema, col_order):
        """
        schema -- description on data structure; it's a dictionary
                    with  key: (label, type)
        col_order -- order of the columns. Denoted by column id.

        XXX : check whether type check is still necessary, despite json
        """
        _cols = []
        self.date_t_pos = [] # keeping track of potential date type

        if type(schema) != dict:
            raise DatTableTypeError("Type Error","Column schema must be a python dictionary.")
       
        if type(col_order) != list:
            raise DatTableTypeError("Type Error","Column order must be a list.")

        _pos = 0
        for _id  in col_order:
            if not schema.has_key(_id):
                raise DataTableError("ID mismatch","Schema and column order key mismatch.")
            
            _label = schema[_id][0]
            _type = schema[_id][1]
            if _type == 'date':
                self.date_t_pos.append(_pos)

            _cols.append(dict(id = _id, 
                            label = _label,
                            type = _type))
            _pos +=1

        self.data = dict(cols = _cols, rows = list())
 

    def __check_valid_type(self, _type):
        # maybe json is already dealing with it...
        pass
        


    def add_row(self, *values):
        """ 
        Adds a single row, which consists of 'cell_object's. 

        row = {cell_object} ',' | [{cell_object} ',']
        cell_object = None | "value" | "(value, format)" | "(value, format, property)"

        Notice, at the moment the 'property' is ignored (XXX)

        XXX input check for valid value types  is missing
        XXX conversion of python date and datetime values -> valid json date, datetime

        """
        if not values:
            return  

        if type(values[0]) == list: # row 
            _values = values[0]
        else:
            _values = values


        # rudimentary  sanity checks
        # 1. number of values == number of cells of row
        if len(_values) != len(self.data['cols']):
            raise DataTableInsertError('Insert Error','The number of cells to insert does not fit schema')
        # XXX 2. type match
         
            
        _row = []
        _pos = 0 
        if values:
            for val in _values:
                if type(val) == tuple or type(val) == list:
                    _f = None
                    _v = val[0]
                    if _v and len(val) > 1:
                        _f = val[1]
                    if not _v:
                        _v = None
                    
                    if _pos in self.date_t_pos: # create javascript Date object
                        _v = 'new Date(%f)' % _v

                    if _v and _f:
                        _row.append(dict(v = _v, f = _f))
                    else:
                        _row.append(dict(v = _v))

                else: 
                    if val:
                        if _pos in self.date_t_pos: # create javascript Date object
                            val = 'new Date(%f)' % val
                        
                        _row.append(dict(v = val))
                    else:
                        _row.append(dict(v = None))
                _pos += 1

        self.data['rows'].append(dict(c = _row))
        

    def get_json(self):
        """
        Returns DataTable as json string. Can be 
        passed to the google charts DataTable constructor
        """
        #return json.dumps(self.data, indent=1)
        return json.dumps(self.data)
   
    def get_raw(self):
        """ returns 'raw' table which shall be json.dumped 
            by requesting application.
        """
        return self.data 

if __name__ == '__main__':
    # some basic tests
    key_order = ['gridrun', 'run','cpus']
    description = { 'gridrun': ('Grid Running', 'number'),
                    'run': ('Running','number'),
                    'cpus': ('Avail. Cores', 'number')}

    dt = DataTable(description, key_order)
    
    print 'created DataTable'

    dt.add_row(1,2,3)
    print "inserted row with values 1,2,3')"
    dt.add_row(2,None,4)
    print 'dt.add_row(2,None,4)'
    dt.add_row(3,(5,6,'fifi'),5)
    print "dt.add_row(3,(5,6,'fifi'),5)"
    dt.add_row([22,33,44])
    dt.add_row([111,(222,'fifi'),777])
    try:
        dt.add_row([111,(222,'fifi'),777,99])
    except DataTableInsertError:
        print 'caught expected exception' 

    print '-'  * 25
    print dt.get_raw()













