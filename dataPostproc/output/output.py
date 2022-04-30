from dataPostproc.utils import _readHDF
from dataPostproc.output.outputBase import varDict

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

    def normalize(self):
        # Reorder the dict
        self._order_list = list(self.keys())
        self._order_list.insert(1, '{}plus'.format(self._dire))
        _temp = self[self._dire]

        # Normalize the variable
        # utau may be a list.
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

        self['{}plus'.format(self._dire[0])] = self[self._dire]
        self[self._dire] = _temp

if __name__ =='__main__':
    a = outputData(_fn='~/DATA/temp_avg/avg_dire.h5', _list=['uu', 'vv'], _dire='z')
    a.normalize()
    a._output('test.dat')
