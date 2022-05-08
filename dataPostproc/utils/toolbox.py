import numpy as np
import sys

#-----------------------------------------#
#---------- Average Of The Data ----------#
#-----------------------------------------#
class _avg(object):
    '''
    AVG: A function to set avg

    avg3d(var, direction): AVG in 3D field.
        var: variable.
        direction: choose the direction.
        output: output the 2D fields.
    avg2d: AVG in 2D field.
        output: output the 1D field.
    avg1d: AVG in 1D field.
        output: output a variable.
    nor_all: From 3d field to 1d array
    '''
    def __init__(self):
        pass

    @classmethod
    def avg3d(cls, var, direction):
        if var.ndim != 3:
            print('Error: Dims of the array is {}, but it must be 3.'.format(var.ndim))
            sys.exit()

        if direction == 1:
            var_tar = np.zeros((var.shape[1], var.shape[2]))
            nloop   = var.shape[0]
            for i in range(nloop):
                var_tar = var_tar + var[i, :, :]

        if direction == 2:
            var_tar = np.zeros((var.shape[0], var.shape[2]))
            nloop   = var.shape[1]
            for i in range(nloop):
                var_tar = var_tar + var[:, i, :]

        if direction == 3:
            var_tar = np.zeros((var.shape[0], var.shape[1]))
            nloop   = var.shape[2]
            for i in range(nloop):
                var_tar = var_tar + var[:, :, i]

        return var_tar/nloop

    @classmethod
    def avg2d(cls, var, direction):
        if var.ndim != 2:
            print('Error: Dims of the array is {}, but it must be 2.'.format(var.ndim))
            sys.exit()

        if direction== 1:
            var_tar = np.zeros((var.shape[1]))
            nloop   = var.shape[0]
            for i in range(nloop):
                var_tar = var_tar + var[i, :]

        if direction == 2:
            var_tar = np.zeros((var.shape[0]))
            nloop   = var.shape[1]
            for i in range(nloop):
                var_tar = var_tar + var[:, i]
        
        return var_tar/nloop

    @classmethod
    def avg1d(cls, var):
        if var.ndim != 1:
            print('Error: Dims of the array is {}, but it must be 1.'.format(var.ndim))
            sys.exit()

        nloop = var.shape[0]
        for i in range(nloop):
            var_tar = var_tar + var[i, :]

        return var_tar/nloop
    
    @classmethod
    def nor_all(cls, var, _dire):
        _list = ['z', 'y', 'x']
        _num1 = _list.index(_list[_list.index(_dire)-1])
        _list.remove(_list[_num1])
        _num2 = _list.index(_list[_list.index(_dire)-1])
        return cls.avg2d(cls.avg3d(var, _num1+1), _num2+1)

#-----------------------------------------#
#--------- Funlib In X Direction ---------#
#-----------------------------------------#
class _funlib(object):
    '''
    Funlib in the x direction.
    '''
    def __init__(self):
        self._funlist = ['cf', 'retau']
        self._perdict = {'cf': 'u'}
        self._indict  = {'cf': ['tau']}

    @classmethod
    def cf(cls, tau):
        return 2*tau
