import numpy as np
from astropy.io import fits
from typing import Tuple
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

def from_file(fname: str) -> FitsFile:
    """
    TODO
    """

    if not os.path.exists(fname):
        raise FileNotFoundError(f"file '{fname} does not exist'")
    image = fits.getdata(fname)
    header = fits.getheader(fname)
    return FitsFile(image, header)
