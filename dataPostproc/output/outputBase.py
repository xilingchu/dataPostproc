from dataPostproc.utils import _avg, _readHDF, _exist_file
from pathlib import Path
from functools import cmp_to_key
import h5py
import math

#----- Basic Class -----#
# For build a var dictionary.
class varDict(dict):
    '''
    varDict: A object of dictionary.
    Variable you must input:
        _fn  :    The file name of the hdf5 file.
        _dire: This variable define the direction of the x, y or z
    -- Function:
        getutau: This function can get utau in the x-direction.
        output : Output the data in a text file.
    '''
    def __init__(self, **kwargs):
        @_exist_file('_fn')
        def getVarlist(_fn=''):
            with h5py.File(_fn, 'r') as f:
                _varlist = list(f.keys())
                return _varlist

        def _del_repeated(_list):
            for _item in _list:
                if _list.count(_item) > 1:
                    _list.pop(_item)
            return _list

        # Dictionary of the direction
        if '_fn' not in kwargs.keys() or '_dire' not in kwargs.keys():
            print('You must have _fn or _dire in this class. Please recheck the code!')
            raise PermissionError

        # Remove the useless kwargs
        _fn   = Path(kwargs['_fn']).expanduser().resolve()
        _list = kwargs['_list']
        self.__dire__ = kwargs['_dire']
        self.__fn__   = _fn
        kwargs.pop('_fn')
        kwargs.pop('_list')
        kwargs.pop('_dire')
        _blockx = None; _blocky = None; _blockz = None
        if '_blockx' in kwargs.keys():
            if kwargs['_blockx'] is not None:
                _blockx = kwargs['_blockx']
            kwargs.pop('_blockx')
        if '_blocky' in kwargs.keys():
            if kwargs['_blocky'] is not None:
                _blocky = kwargs['_blocky']
            kwargs.pop('_blocky')
        if '_blockz' in kwargs.keys():
            if kwargs['_blockz'] is not None:
                _blockz = kwargs['_blockz']
            kwargs.pop('_blockz')
        self.__blockx__=_blockx; self.__blocky__=_blocky; self.__blockz__=_blockz

        # Get the varlist
        _varlist = getVarlist(_fn=_fn)
        _list = _del_repeated(_list)
        self.__varlist__ = _varlist
        for _item in _list:
            if _item not in _varlist:
                print('Warning: Please check the variable {}, which is not in the list!'.format(_item))
                print(_varlist)
                _list.remove(_item)

        # Determine the direction of the array
        _block = getattr(self, '__block{}__'.format(self.__dire__))
        if self.__dire__ not in _varlist:
            _dire = '{}c'.format(self.__dire__)
        else:
            _dire = self.__dire__

        # Make the class to an array
        kwargs[_dire] = _readHDF(_fn=_fn, _var=_dire, _blockz=_block, _blocky=None, _blockx=None)
        for k in _list:
            kwargs[k] = _readHDF(_fn=_fn, _var=k, _blockz = _blockz, _blocky = _blocky, _blockx = _blockx)
            kwargs[k] = _avg.nor_all(kwargs[k], self.__dire__)

        self.__dire__ = _dire

        super(varDict, self).__init__(**kwargs)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError('The key {} doesn\'t exist in {}'.format(key, self.__class__.__name__))

    def _getutau(self, _fn=None):
        if _fn is None:
            _fn = self.__fn__
        else:
            _fn = Path(_fn)
        try:
            u    = _readHDF(_fn=_fn, _var='u' , _blockz=[1, 1, 1 ,1], _blocky=self.__blocky__, _blockx=self.__blockx__)
            z1   = _readHDF(_fn=_fn, _var='zc', _blockz=[1, 1, 1 ,1], _blocky=self.__blocky__, _blockx=self.__blockx__)
        except:
            raise FileExistsError('The variable u does not exist in the {}.'.format(_fn))
        u1   = _avg.nor_all(u, 'z')
        tau  = self.nu*u1/z1
        return math.sqrt(tau)

    def _output(self, _ofile):
        # Compare rules 
        # Rule 1. Direction(x, y, or z) is the the first one
        # Rule 2. The shorter length of the variable.
        # Rule 3. balance is the last variable
        def cmp_zmax(v1, v2):
            if v2[0] in ['x', 'y', 'z'] and v1[0] not in ['x', 'y', 'z']:
                return 1
            elif v2[0] not in ['x', 'y', 'z'] and v1[0] in ['x', 'y', 'z']: 
                return -1
            elif v1 == 'balance':
                return 1
            elif v2 == 'balance':
                return -1
            else:
                if len(v2) < len(v1):
                    return 1
                elif len(v2) > len(v1):
                    return -1
            return (v1 > v2) - (v1 < v2)
            
        _list      = list(self.keys())
        _filename  = '{}.dat'.format(_ofile)
        _len       = len(self[self.__dire__])
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
        _title_head = '{:40s}'.format('Statistics of the data along with {}'.format(self.__dire__[0]))+'\n'
        _spl_head = 80*'-'+'\n'
        with open(_filename, 'w') as f:
            f.write(_title_head+_head_str1+_head_str2+_spl_head*2)
            for i in range(_len):
                for _item in _list:
                    if _item in ['rethe', 'redel', 'rex', 'retau', 'redeldi', 'redelen']:
                        f.write('{:14.2e}'.format(self[_item][i]))
                    elif _item in ['zc', 'zplus']:
                        f.write('{:14.6f}'.format(self[_item][i]))
                    else:
                        f.write('{:14.6e}'.format(self[_item][i]))
                f.write('\n')
            print('File generated complete')
            f.close()
