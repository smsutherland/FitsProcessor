import numpy as np
from glob import glob
from astropy.io import fits
from typing import Union, List

class SingleFrameReducer:
    """
    Processor for FITS data processing.

    Stores data relevant to the processing.
    """
    _bias_frame: np.ndarray = None
    _dark_current_frame: np.ndarray = None
    
    def set_bias_frames(self, file_name: Union[str, List[str]]) -> None:
        """
        """

        file_name_list = []
        if isinstance(file_name, list):
            for fname in file_name:
                file_name += glob(fname)
        else:
            file_name_list = glob(file_name)
        
        if len(file_name_list) == 0:
            raise Exception("No files specified or file not found.")
        
        bias_frames = [fits.getdata(fname)*fits.getheader(fname)["EGAIN"] for fname in file_name_list]
        self._bias_frame = np.mean(bias_frames, axis=0)

    def set_dark_current_frames(self, file_name: Union[str, List[str]]) -> None:
        """
        """

        if self._bias_frame is None:
            raise Exception("call set_bias_frames before calling this function")

        file_name_list = []
        if isinstance(file_name, list):
            for fname in file_name:
                file_name += glob(fname)
        else:
            file_name_list = glob(file_name)
        
        if len(file_name_list) == 0:
            raise Exception("No files specified or file not found.")
        
        dark_current_frames = np.array([fits.getdata(fname)*fits.getheader(fname)["EGAIN"] for fname in file_name_list])
        self.bias_subtract(dark_current_frames, out=dark_current_frames)
        for frame, exp_time in zip(dark_current_frames, [fits.getheader(fname)["EXPTIME"] for fname in file_name_list]):
            np.divide(frame, exp_time, out=frame)
        self._dark_current_frame = np.mean(dark_current_frames, axis=0)
    
    def bias_subtract(self, frame: np.ndarray, out: Union[None, np.ndarray] = None) -> np.ndarray:
        if self._bias_frame is None:
            raise Exception("call set_bias_frames before bias subtracting")
        
        return np.subtract(frame, self._bias_frame, out=out)

    def dark_subtract(self, frame: np.ndarray, exposure_time: float, out: Union[None, np.ndarray] = None) -> np.ndarray:
        if self._dark_current_frame is None:
            raise Exception("call set_dark_current_frames before dark subtracting")
        if self._bias_frame is None:
            raise Exception("call set_bias_frames before bias subtracting")
        
        return np.subtract(frame, self._bias_frame + exposure_time*self._dark_current_frame, out=out)

    def bias_frame(self) -> np.ndarray:
        return np.copy(self._bias_frame)
    
    def dark_current_frame(self) -> np.ndarray:
        return np.copy(self._dark_current_frame)
