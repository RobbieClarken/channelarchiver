# -*- coding: utf-8 -*-

class Codes(object):
    def __init__(self, **kws):
        self._reverse_dict = {}
        for k, v in kws.items():
            self.__setattr__(k, v)
            
    def str_value(self, value):
        return self._reverse_dict[value]
    
    def __setattr__(self, name, value):
        super(Codes, self).__setattr__(name, value)
        if not name.startswith('_'):
            self._reverse_dict[value] = name
        
    def __repr__(self):
        constants_str = ', '.join('{0}={1!r}'.format(v, k) for k, v
                                  in sorted(self._reverse_dict.items()))
        return 'Codes({0})'.format(constants_str)
