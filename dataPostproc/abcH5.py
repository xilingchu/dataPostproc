# pyright: reportInvalidTypeForm=false, reportAttributeAccessIssue=false, reportIndexIssue=false
# The h5py.File will return Groups/Dataset/Datatype according to the file. Just ignore the diagnostics.
from abc import ABC, abstractmethod
from pathlib import Path
from dataPostproc.utils.toolbox import _funlib
from dataPostproc.utils.decorators import _exist_file
import h5py


def _del_repeated(_list: list[str]) -> list[str]:
    """Remove duplicate items from a list while preserving order."""
    if not isinstance(_list, list):
        raise TypeError("Input must be a list.")
    return list(dict.fromkeys(_list))

@_exist_file('file_path')
def getVarlist(file_path: Path = Path('')) -> list[str]:
    """Retrieve a list of variable names from an HDF5 file.

    Args:
        file_path: Path to the HDF5 file. Defaults to an empty Path.

    Returns:
        A list of variable names (keys) in the HDF5 file.
    """
    with h5py.File(file_path, 'r') as f:
        return list(f.keys())

class requiredError(Exception):
    pass

class directionError(Exception):
    pass

class abcH5(ABC):
    def __init__(self, **kwargs):
        self._funlib  = _funlib()
        self._validate_required_args(kwargs)
        self._check_direction(kwargs)
        self._check_variables(kwargs)
        self._check_periodic(kwargs)

        # Validate required Error
        def _validate_required_args(self, kwargs):
            if '_fn' not in kwargs.keys() or '_list' not in kwargs.keys():
                raise requiredError('You must provide both _fn and _list in this class. Please recheck the code!')

        # Initialize the direction
        def _check_direction(self, kwargs):
            # Direction
            if '_dire' not in kwargs.keys():
                self._dire = 'x'
            else:
                self._dire = kwargs['_dire']
                kwargs.pop('_dire')

        # Define the variables
        def _check_variables(self, kwargs):
            # filename
            self._fn   = Path(kwargs['_fn']).expanduser().resolve()
            kwargs.pop('_fn')
            # Define the varlist
            self._varlist = getVarlist(self._fn)

            # Check the list and define the list
            _list = kwargs['_list'] 
            _list = _del_repeated(_list)
            kwargs.pop('_list')
            to_remove = []
            for _item in _list:
                if _item not in self._varlist and _item not in self._funlib._funlist:
                    print(f'Warning: Please check the variable {_item}, which is not in the list!')
                    print(self._varlist)
                    to_remove.append(_item)
            self._list = [item for item in _list if item not in to_remove]

        def _check_periodic(self):
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
                    if self._dire == 'x':
                        self._dire = 'xc'
                except:
                    raise directionError('The HDF5 file does not contain data for the x direction.')

            # Y-direction
            try:
                self._sy   = self._file['y'].shape[0]
                self._vary = 'y'
            except:
                try:
                    self._sy = self._file['yc'].shape[0]
                    self._vary = 'yc'
                    if self._dire == 'y':
                        self._dire = 'yc'
                except:
                    raise directionError('The HDF5 file does not contain data for the y direction.')

            # Z-direction
            try:
                self._sz   = self._file['z'].shape[0]
                self._varz = 'z'
            except:
                try:
                    self._sz = self._file['zc'].shape[0]
                    self._varz = 'zc'
                    if self._dire == 'z':
                        self._dire = 'zc'
                except:
                    raise directionError('The HDF5 file does not contain data for the z direction.')

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
            pass
