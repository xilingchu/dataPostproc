# pyright: reportInvalidTypeForm=false, reportAttributeAccessIssue=false, reportIndexIssue=false, reportOperatorIssue=false
# The h5py.File will return Groups/Dataset/Datatype according to the file. Just ignore the diagnostics.

from dataPostproc.utils import _avg, _readHDF, _exist_file
from dataPostproc.abcH5 import abcH5
from pathlib import Path
from functools import cmp_to_key
import numpy as np
import h5py
import math

def sqrt_h0(var):
    try:
        var = math.sqrt(var)
    except(ValueError, TypeError):
        var = 0
    return var

class dimensionError(Exception):
    pass
    
#----- Basic Class -----#
# For build a var dictionary.
class varDict(abcH5, dict):
    '''
    varDict: A object of dictionary.
    -- Input:
        _fn  :    The file name of the hdf5 file.
        _dire: This variable define the direction of the x, y or z
    -- Function:
        gettau: This function can get tau in the x-direction.
        output : Output the data in a text file.
    '''
    def __init__(self, **kwargs):
        # Determine the direction of the array
        super(varDict, self).__init__(**kwargs)
        kwargs.pop('_fn')
        kwargs.pop('_dire')
        kwargs.pop('_list')
        # Get the nu
        # Judge if the input parameters are correct.
        if self._blockx is None:
            self._blockx = [0, 1, self._sx, 1]
        else:
            if len(self._blockx) != 4:
                raise dimensionError('ERROR: The length of blockx should be 4!')
        kwargs.pop('_blockx')

        if self._blocky is None:
            self._blocky = [0, 1, self._sy, 1]
        else:
            if len(self._blocky) != 4:
                raise dimensionError('ERROR: The length of block_y should be 4!')
        kwargs.pop('_blocky')

        if self._blockz is None:
            self._blockz = [0, 1, self._sz, 1]
        else:
            if len(self._blockz) != 4:
                raise dimensionError('ERROR: The length of blockz should be 4!')
        kwargs.pop('_blockz')
        _blockz = self._blockz

        # Get the nu and tau
        self.nu   = _readHDF(_fn=self._fn, _var='nu')
        if '_uout' in kwargs.keys():
            if kwargs['_uout'] == None:
                self.tau = self._gettau(self._fn)
            else:
                self.tau = self._gettau(kwargs['_uout'])
            kwargs.pop('_uout')
        else:
            self.tau = self._gettau(self._fn)

        # Get the utau
        # Check zero
        self.utau = np.zeros(len(self.tau))
        for i in range(len(self.tau)):
            self.utau[i] = sqrt_h0(self.tau[i])
        
        if self._dire is None:
            raise Exception('ERROR: In this class we should include _dire.')

        _block = getattr(self, f'_block{self._dire[0]}')

        # Make the class to an array
        for _var in self._list:
            if _var not in self._funlib._funlist:
                _blockx       = self._blockx[:]
                _blockx[0]   += self._per[_var][1]
                _blocky       = self._blocky[:]
                _blocky[0]   += self._per[_var][0]
                kwargs[_var] = _readHDF(_fn=self._fn, _var=_var,
                                        _blockz = self._blockz,
                                        _blocky = _blocky,
                                        _blockx = _blockx)
                kwargs[_var] = _avg.nor_all(kwargs[_var], self._dire[0])

            # Cf
            else:
                _inlist = self._funlib._indict[_var]
                args = []
                for _in in _inlist:
                    if hasattr(self, _in):
                        args.append(getattr(self, _in))
                    else:
                        _blockx       = self._blockx[:]
                        _blockx[0]   += self._per[_var][1]
                        _blocky       = self._blocky[:]
                        _blocky[0]   += self._per[_var][0]
                        args.append(_readHDF(_fn=self._fn, _var=_var, _blockz = self._blockz, _blocky = _blocky, _blockx = _blockx))
                fun_var = getattr(self._funlib, _var)
                kwargs[_var] = fun_var(*args)

        kwargs[self._dire] = _readHDF(_fn=self._fn, _var=self._dire, _blockz=_block, _blocky=None, _blockx=None)
        # If consider dz, this funtion is used to calculate intergal, so it's better to set block and stride = 1.
        # Zd is must
        kwargs[self._zd] = _readHDF(_fn=self._fn, _var=self._dire[0]+'d',
                                       _blockz=[2*_blockz[0], 2*_blockz[1], _blockz[2], 2*_block[3]],
                                       _blocky=None, _blockx=None)

        super(abcH5, self).__init__(**kwargs)

    def _gettau(self, _fn=None):
        if _fn is None:
            _fn = self._fn
        else:
            _fn = Path(_fn)
        try:
            _file  = h5py.File(_fn, 'r')
            _shape = _file['u'].shape
            _per   = [int(_shape[1] == self._sy+2), int(_shape[2] == self._sx+2)]
            _blockx       = self._blockx[:]
            _blockx[0]   += _per[1]
            _blocky       = self._blocky[:]
            _blocky[0]   += _per[0]
            u    = _readHDF(_fn=_fn, _var='u' , _blockz=[1, 1, 1 ,1], _blocky=_blocky, _blockx=_blockx)
            z1   = _readHDF(_fn=_fn, _var='zc', _blockz=[1, 1, 1 ,1])
        except:
            raise FileExistsError(f'The variable u does not exist in the {_fn}.')
        u1   = _avg.nor_all(u, self._dire[0])
        tau  = self.nu*u1/z1
        return np.array(tau)

    def _output(self, _fn):
        # Compare rules 
        # Rule 1. Direction(x, y, or z) is the the first one
        # Rule 2. The shorter length of the variable.
        # Rule 3. balance is the last variable
        def cmp_zmax(v1, v2):
            if v1 == 'balance':
                return 1
            if v2 == 'balance':
                return -1
            if v1[0] in ['x', 'y', 'z'] and v2[0] not in ['x', 'y', 'z']:
                return -1
            if v2[0] in ['x', 'y', 'z'] and v1[0] not in ['x', 'y', 'z']:
                return 1
            return len(v1) - len(v2)
            
        _filename = _fn
        if '.dat' not in _filename:
            _filename += '.xdmf'
        _list      = list(self.keys())
        _len       = len(self[self._dire])
        _head_str1 = ''
        _head_str2 = ''
        i = 0
        _list.sort(key=cmp_to_key(cmp_zmax))
        for var_str in _list:
            i += 1
            _head_str1 += '{:>14s}'.format('C'+str(i))
            _head_str2 += '{:>14s}'.format(var_str)
        _head_str1 += '\n'
        _head_str2 += '\n'
        if type(self.utau) == type(1.0):
            _title_head = f'{"Statistics of the data along with "+self._dire[0]+", Ret="+str(self.utau/self.nu):40s}\n'
        else:
            _title_head = f'{"Statistics of the data along with "+self._dire[0]+", Ret="+str(self.utau[0]/self.nu):40s}\n'
        _spl_head = 80*'-'+'\n'
        with open(_filename, 'w') as f:
            f.write(_title_head+_head_str1+_head_str2+_spl_head*2)
            for i in range(_len):
                for _item in _list:
                    if _item in ['rethe', 'redel', 'rex', 'retau', 'redeldi', 'redelen']:
                        f.write(f'{self[_item][i]:14.2e}')
                    elif _item in ['zc', 'zplus']:
                        f.write(f'{self[_item][i]:14.6f}')
                    else:
                        f.write(f'{self[_item][i]:14.6e}')
                f.write('\n')
            print('File generated complete')
