import h5py
import numpy as np
from .decorators import _exist_file

@_exist_file('_fn')
def _readHDF(_fn=None, _var=None, _blockz=None, _blocky=None, _blockx=None):
    '''
    readHDF: A function to read HDF5 file.
    You must privide the filename(_fn), and the variable(_var) you wanna read.

    blockx, blocky and blockz are selected choices.

    Details of blockx(yz) are blockx[start, stride, count, block]
    
    start  ---- The start point of the block
    stride ---- The length of two blocks
    count  ---- The count of the blocks
    block  ---- The size of one block
    '''
    with h5py.File(_fn, 'r') as f:
        sh_in = f[_var].shape
        dims = len(sh_in)
        if dims == 1:
            if _blockz == None:
                _blockz=[0, 1, sh_in[0], 1]
            if sh_in[0] == 1:
                _var_out = f[_var][0]
            else:
                _var_out = f[_var][h5py.MultiBlockSlice(_blockz[0], _blockz[1], _blockz[2], _blockz[3])][:]
        elif dims == 2:
            if _blockz == None:
                _blockz=[0, 1, sh_in[0], 1]
            if _blocky == None:
                _blocky=[0, 1, sh_in[1], 1]
            _var_out = f[_var][h5py.MultiBlockSlice(_blockz[0], _blockz[1], _blockz[2], _blockz[3]),
                             h5py.MultiBlockSlice(_blocky[0], _blocky[1], _blocky[2], _blocky[3])][:,:]
        elif dims == 3:
            if _blockz == None:
                _blockz=[0, 1, sh_in[0], 1]
            if _blocky == None:
                _blocky=[0, 1, sh_in[1], 1]
            if _blockx == None:
                _blockx=[0, 1, sh_in[2], 1]
            _var_out = f[_var][h5py.MultiBlockSlice(_blockz[0], _blockz[1], _blockz[2], _blockz[3]),
                             h5py.MultiBlockSlice(_blocky[0], _blocky[1], _blocky[2], _blocky[3]),
                             h5py.MultiBlockSlice(_blockx[0], _blockx[1], _blockx[2], _blockx[3])][:,:,:]
        f.close()
    return _var_out
