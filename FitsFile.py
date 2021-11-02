import numpy as np
import Image
from astropy.io import fits
import os

class FitsFile():
    """
    TODO
    """

    _image: Image.Image
    _header: fits.header.Header

    def __init__(self, image: Image.Image, header: fits.header.Header):
        self._image = image
        self._header = header
    
    def multiply_gain(self):
        """
        TODO
        """

        self._image *= self._header["EGAIN"]
        return self
    
    def cards(self):
        """
        TODO
        """

        return self._header.cards()
    
    def from_header(self, key: str):
        return self._header[key]
    
    def image(self):
        """
        TODO
        """

        return np.copy(self._image)

def from_file(fname: str) -> FitsFile:
    """
    TODO
    """

    if not os.path.exists(fname):
        raise FileNotFoundError(f"file '{fname}' does not exist")
    image = Image.from_array(fits.getdata(fname))

    header = fits.getheader(fname)
    
    return FitsFile(image, header)
