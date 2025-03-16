from functools import wraps
from pathlib import Path
import h5py
import logging
from typing import Callable, Dict, Any

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Custom Exceptions
class InvalidFilenameError(Exception):
    pass

class InvalidHDF5FileError(Exception):
    pass

# Decorator
def _exist_file(_var_fn: str) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(**kwargs: Dict[str, Any]) -> Any:
            if _var_fn not in kwargs:
                logger.warning("The variable of filename is incorrect. Please check it!")
                raise InvalidFilenameError(f"Missing required argument: {_var_fn}")

            filename = Path(str(kwargs[_var_fn])).resolve()
            if not filename.exists():
                logger.error("Target file doesn't exist. Please check your input file!")
                raise FileNotFoundError(f"File not found: {filename}")

            if not h5py.is_hdf5(filename):
                logger.error("Target file is not a valid HDF5 file. Please check your input file!")
                raise InvalidHDF5FileError(f"Invalid HDF5 file: {filename}")

            return func(**kwargs)
        return wrapper
    return decorator
