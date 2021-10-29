import numpy as np
from astropy.io import fits
from typing import Tuple, Union
import os

class FitsFile:
    """
    Container for fits file information, including the image and header.
    """

    _image: np.ndarray = None
    _dimensions: Tuple[int, int] = (0, 0)

    _header: dict

    def __init__(self, image: np.ndarray, header: dict):
        shape = image.shape
        if len(shape) != 2:
            raise Exception("image should be a 2-d array")
        
        self._image = image
        self._header = header
        self._dimensions = image.shape
    
    def __add__(self, other: Union["FitsFile", np.ndarray, float]) -> "FitsFile":
        """
        TODO
        """

        if self._image is None:
            raise ValueError("image must exist")
        
        if isinstance(value, "FitsFile"):
            if value._dimensions == self._dimensions:
                return FitsFile(self._image+value._image, self._header)
            else:
                raise ValueError("sides do not have same shape")
        elif isinstance(value, np.ndarray):
            if value.shape == self._dimensions:
                return FitsFile(self._image+value, self._header)
            else:
                raise ValueError("sides do not have same shape")
        else:
            value = float(value)
            return FitsFile(self._image+value, self._header)

    def __sub__(self, other: Union["FitsFile", np.ndarray, float]) -> "FitsFile":
        """
        TODO
        """
        
        return self + (-1*other)
    
    def __mul__(self, value: float) -> "FitsFile":
        """
        TODO
        """

        if self._image is None:
            raise ValueError("image must exist")
        value = float(value)
        return FitsFile(self._image*value, self._header)

    def __truediv__(self, value: float) -> "FitsFile":
        """
        TODO
        """

        return self * (1/value)

def from_file(fname: str) -> FitsFile:
    """
    TODO
    """

    if not os.path.exists(fname):
        raise FileNotFoundError(f"file '{fname} does not exist'")
    image = fits.getdata(fname)
    header = fits.getheader(fname)
    return FitsFile(image, header)
