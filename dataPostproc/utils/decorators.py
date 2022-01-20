from functools import wraps
from pathlib import Path
import h5py
import sys

#------ Decorator ------#
def _exist_file(_var_fn):
    def decorator(func):
        @wraps(func)
        def wrapper(**kwargs):
            if _var_fn not in kwargs.keys():
                print('Warning: The variable of filename is incorrect, maybe you should check it!')
            else:
                filename = Path(kwargs[_var_fn]).absolute().resolve()
                if not filename.exists():
                    print('ERROR: Target file doesn\'t exist. Please check your input file!')
                    raise FileExistsError
                if not h5py.is_hdf5(filename):
                    print('ERROR: Target file is not valid HDF5 file. Please check your input file!')
                    raise FileExistsError
                return func(**kwargs)
        return wrapper
    return decorator
