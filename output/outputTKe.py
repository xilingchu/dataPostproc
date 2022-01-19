from outputh5.utils import _defTKEName
from outputh5.output.outputBase import varDict

#----------------------------------------#
#--------- The Sub Class Of Tke ---------#
#----------------------------------------#
class outputData_tke(varDict):
    '''
    outputData_tke_real: A class to output the turbulent kinetic energy.
    The class is a sub class of output.
    This class store all the variables in the HDF5 file.
    -- Input:
        - _fn(must):   The filename of the hdf5 file.
        - _dire(must): The direction to be normalized.
        - _var(must):  The kinetic term in the HDF5.
        - _blockx(optional): The section in the x direction. Start, Stride, Block, Count
        - _blocky(optional): The section in the y direction. Start, Stride, Block, Count
        - _blockz(optional): The section in the z direction. Start, Stride, Block, Count
    -- Function:
        normalize(_fn): _fn is the filename include the variable u.
    '''
    def __init__(self, **kwargs):
        if '_var' not in kwargs.keys():
            raise ValueError('In this function you have to add var.')
        else:
            _var          = kwargs['_var']
            self._vardict = _defTKEName(_var)
            self._var     = kwargs.pop('_var')
            kwargs['_list'] = list(self._vardict.keys())
        super().__init__(**kwargs)
        for _key, _value in self._vardict.items():
            self[_value] = self.pop(_key)
        
    def normalize(self, _fn=None):
        # For safe
        self.utau = self._getutau(_fn)

        # Reorder the dict
        self._order_list = list(self.keys())
        self._order_list.insert(1, '{}plus'.format(self.__dire__[0]))
        _temp = self[self.__dire__]

        # Normalize the variable
        _nor = self.nu/self.utau**4
        for _key in self.keys():
            if _key[0] in ['x', 'y', 'z']:
                self[_key] = self[_key]*self.utau/self.nu
            else:
                self[_key] *= _nor

        self['{}plus'.format(self.__dire__[0])] = self[self.__dire__]
        self[self.__dire__] = _temp

    def outputTke_all(self):
        self.tkeall = self
        # Default value of tkeall
        self.tkeall['prod'] = 0
        self.tkeall['turb'] = 0
        self.tkeall['visc_trans'] = 0
        self.tkeall['visc_diss'] = 0
        self.tkeall['press_strain'] = 0
        self.tkeall['press_trans'] = 0
        self.tkeall['balance'] = 0
        for _key, _value in self._vardict.items():
            val = self.pop(_value)
            if _key[0:4] == 'prod':
                self.tkeall['prod']    += val
                self.tkeall['balance'] += val
            if _key[0:4] == 'turb':
                self.tkeall['turb']    += val
                self.tkeall['balance'] += val
            if _key[0:10] == 'visc_trans':
                self.tkeall['visc_trans'] += val
                self.tkeall['balance']    += val
            if _key[0:9] == 'visc_diss':
                self.tkeall['visc_diss'] += val
                self.tkeall['balance']   += val
            if _key[0:12] == 'press_strain':
                self.tkeall['press_strain'] += val
                self.tkeall['balance']      += val
            if _key[0:11] == 'press_trans':
                self.tkeall['press_trans'] += val
                self.tkeall['balance']     += val
        return self.tkeall

if __name__ == '__main__':
    filename = '~/DATA/temp_avg/TKE_uu.h5'
    a = outputData_tke(_fn=filename, _dire='z', _var='uu').outputTke_all()
