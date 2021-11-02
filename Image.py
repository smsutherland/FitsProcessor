import numpy as np
from typing import Union, Tuple
import os
from astropy.io import fits

class Image(np.ndarray):
    """
    A 2-d np.ndarray storing floats representing an image
    """

    def __new__(cls, *args, **kwargs):
        super().__new__(cls, *args, **kwargs)

    def __array_finalize__(self, obj):
        # if len(self.shape) != 2:
        #     raise ValueError("Images must be 2-d")
        # find some way to ensure 2-d without breaking other functions like imshow or ravel
        pass
    
    # def to_array(self):
    #     return self.view(np.ndarray)

def from_array(arr: np.ndarray) -> Image:
    """
    TODO
    """
    
    if type(arr) != np.ndarray:
        arr = np.array(arr)
    return arr.copy().view(Image).astype(float)
