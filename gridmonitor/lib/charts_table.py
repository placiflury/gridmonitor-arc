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
        Adds a single data sample.

        values = (list) of values. If formating strings  are passed, the list must
                consist of tuples or list, where tuple[0] == value, tuple[1] == formating string.

        XXX input check for valid value types  is missing
        XXX conversion of python date and datetime values -> valid json date, datetime

        """
        _row = []
        _pos = 0 
        for val in values:
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
    
