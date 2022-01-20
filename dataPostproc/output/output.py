from dataPostproc.utils import _readHDF
from .outputBase import varDict

#----------------------------------------#
#--------- The Main Output Code ---------#
#----------------------------------------#
class outputData(varDict):
    '''
    outputData: A class to output data in different direction.
    The class is a sub class of output.
    This class store all the variables in a class.
    -- Input:
        - _fn(must): The filename of the hdf5 file.
        - _dire(must): The direction to be normalized.
        - _list(must): The variables you want to normalize.
        - _blockx(optional): The section in the x direction. Start, Stride, Block, Count
        - _blocky(optional): The section in the y direction. Start, Stride, Block, Count
        - _blockz(optional): The section in the z direction. Start, Stride, Block, Count
    -- Function:
        normalize(_fn): _fn is the filename include the variable u.
    '''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.nu = _readHDF(_fn=self.__fn__, _var='nu')

    def normalize(self, _fn=None):
        # For safe
        self.utau = self._getutau(_fn)

        # Reorder the dict
        self._order_list = list(self.keys())
        self._order_list.insert(1, '{}plus'.format(self.__dire__[0]))
        _temp = self[self.__dire__]

        # Normalize the variable
        _nor = self.nu/self.utau
        _tau = 1/self.utau/self.utau
        for _key in self.keys():
            if _key[0] in ['x', 'y', 'z']:
                self[_key] = self[_key]*self.utau/self.nu
            else:
                for _str in _key:
                    if _str in ['u', 'v', 'w']:
                        self[_key] /= self.utau
                    elif _str in ['p']:
                        self[_key] *= _tau
                    elif _str in ['x', 'y', 'z']:
                        self[_key] *= _nor

        self['{}plus'.format(self.__dire__[0])] = self[self.__dire__]
        self[self.__dire__] = _temp

if __name__ == '__main__':
    a = outputData(_fn='/home/xlc/DATA/temp_avg/avg_per.h5', _dire='x', _list=['uu', 'uz'], _blockz = [0,1,1,1])
    a.normalize()
    a._output('a.dat', a._order_list)
    print(a.uz)
