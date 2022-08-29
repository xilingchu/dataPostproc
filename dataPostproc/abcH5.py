from abc import ABC, abstractmethod
from pathlib import Path
from dataPostproc.utils.toolbox import _funlib
import h5py


class abcH5(ABC):
    def __init__(self, **kwargs):

        if '_dire' not in kwargs.keys():
            self._dire = 'x'

        # Direction
        _dire = kwargs['_dire']
        kwargs.pop('_dire')

        def getVarlist(_fn=''):
            with h5py.File(_fn, 'r') as f:
                _varlist = list(f.keys())
                return _varlist

        def _del_repeated(_list):
            for _item in _list:
                if _list.count(_item) > 1:
                    _list.pop(_item)
            return _list

        self._funlib  = _funlib()

        if '_fn' not in kwargs.keys() or '_list' not in kwargs.keys():
            raise Exception('You must have _fn or _dire in this class. Please recheck the code!')

        # filename
        self._fn   = Path(kwargs['_fn']).expanduser().resolve()
        if not self._fn.exists():
            raise FileExistsError('ERROR: Target file doesn\'t exist. Please check your input file!')
        if not h5py.is_hdf5(self._fn):
            raise FileExistsError('ERROR: Target file is not valid HDF5 file. Please check your input file!')
        kwargs.pop('_fn')

        # Block in three directions
        if '_blockx' in kwargs.keys():
            _blockx = kwargs['_blockx']
            kwargs.pop('_blockx')
        else:
            _blockx = None
        if '_blocky' in kwargs.keys():
            _blocky = kwargs['_blocky']
            kwargs.pop('_blocky')
        else:
            _blocky = None
        if '_blockz' in kwargs.keys():
            _blockz = kwargs['_blockz']
            kwargs.pop('_blockz')
        else:
            _blockz = None
        self._blockx = _blockx
        self._blocky = _blocky
        self._blockz = _blockz

        # Define the varlist
        self._varlist = getVarlist(_fn = self._fn)

        # Check the list and define the list
        _list = kwargs['_list'] 
        _list = _del_repeated(_list)
        kwargs.pop('_list')
        for _item in _list:
            if _item not in self._varlist and _item not in self._funlib._funlist:
                print('Warning: Please check the variable {}, which is not in the list!'.format(_item))
                print(self._varlist)
                _list.remove(_item)
        self._list = _list
        
        # Check if the list is periodic
        self._file = h5py.File(self._fn, 'r')
        # Judge the shape and the array.
        # X-direction
        try:
            self._sx   = self._file['x'].shape[0]
            self._varx = 'x'
        except:
            try:
                self._sx   = self._file['xc'].shape[0]
                self._varx = 'xc'
            except:
                raise Exception('The HDF5 file don\'t have array contains the data of the x direction.')

        # Y-direction
        try:
            self._sy   = self._file['y'].shape[0]
            self._vary = 'y'
        except:
            try:
                self._sy = self._file['yc'].shape[0]
                self._vary = 'yc'
            except:
                raise Exception('The HDF5 file don\'t have array contains the data of the y direction.')

        # Z-direction
        try:
            self._sz   = self._file['z'].shape[0]
            self._varz = 'z'
        except:
            try:
                self._sz = self._file['zc'].shape[0]
                self._varz = 'zc'
            except:
                raise Exception('The HDF5 file don\'t have array contains the data of the z direction.')

        self._per  = {}
        for _item in self._list:
            if _item not in self._funlib._funlist:
                _shape = self._file[_item].shape
                self._per[_item] = [int(_shape[1] == self._sy + 2), int(_shape[2] == self._sx + 2)]
            else:
                _var   = self._funlib._perdict[_item]
                _shape = self._file[_var].shape
                self._per[_item] = [int(_shape[1] == self._sy + 2), int(_shape[2] == self._sx + 2)]

        @abstractmethod
        def _output(self, _fn:str) -> None:
            '''
            _output: Implement by the other class to output file.
            -- Input: 
                - filename: The output name.
            -- Returns:
                Output the file.
            '''
            raise Exception("This output is incorrectly implemented.")
