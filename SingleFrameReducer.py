import numpy as np
import Image
from glob import glob
from typing import Union, List

class SingleFrameReducer:
    """
    Processor for FITS data processing.

    Stores data relevant to the processing.
    """

    _bias_frame: Image.Image = None
    _dark_current_frame: Image.Image = None
    _normalized_flat_frame: Image.Image = None
    
    def set_bias_frames(self, file_name: Union[str, List[str]]) -> None:
        """
        TODO
        """

        file_name_list = []
        if isinstance(file_name, list):
            for fname in file_name:
                file_name += glob(fname)
        else:
            file_name_list = glob(file_name)
        
        if len(file_name_list) == 0:
            raise Exception("No files specified or file not found.")
        
        bias_frames = [Image.from_file(fname) for fname in file_name_list]
        self._bias_frame = np.mean(bias_frames, axis=0)

    def set_dark_current_frames(self, file_name: Union[str, List[str]]) -> None:
        """
        TODO
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
        
        dark_current_frames_full = [Image.from_file(fname, True) for fname in file_name_list]
        dark_current_frames_bias_subtracted = [self.bias_subtract(frame[0]) for frame in dark_current_frames_full]

        exposure_times = [frame[1]["EXPTIME"] for frame in dark_current_frames_full]
        for frame, exposure_time in zip(dark_current_frames_bias_subtracted, exposure_times):
            frame = frame/exposure_time
        self._dark_current_frame = np.mean(dark_current_frames_bias_subtracted, axis=0)
    
    def set_flat_frames(self, file_name: Union[str, List[str]]) -> None:
        """
        TODO
        """

        if self._bias_frame is None:
            raise Exception("call set_bias_frames before calling this function")
        if self._dark_current_frame is None:
            raise Exception("call set_dark_current_frames before calling this function")

        file_name_list = []
        if isinstance(file_name, list):
            for fname in file_name:
                file_name += glob(fname)
        else:
            file_name_list = glob(file_name)
        
        if len(file_name_list) == 0:
            raise Exception("No files specified or file not found.")
        
        flat_frames_full = [Image.from_file(fname, True) for fname in file_name_list]
        flat_frames_dark_subtracted = [self.dark_subtract(frame[0], frame[1]["EXPTIME"]) for frame in flat_frames_full]
        mean_flat_frame = np.mean(flat_frames_dark_subtracted, axis=0)
        self._normalized_flat_frame = mean_flat_frame/np.mean(mean_flat_frame)

    
    def bias_subtract(self, frame: Image.Image) -> Image.Image:
        """
        TODO
        """

        if self._bias_frame is None:
            raise Exception("call set_bias_frames before bias subtracting")
        
        return frame - self._bias_frame

    def dark_subtract(self, frame: Image.Image, exposure_time: float) -> Image.Image:
        """
        TODO
        """

        if self._bias_frame is None:
            raise Exception("call set_bias_frames before bias subtracting")
        if self._dark_current_frame is None:
            raise Exception("call set_dark_current_frames before dark subtracting")
        
        return self.bias_subtract(frame) - exposure_time*self._dark_current_frame
    
    def flatten(self, frame: Image.Image, exposure_time: float) -> Image.Image:
        """
        TODO
        """

        if self._bias_frame is None:
            raise Exception("call set_bias_frames before flattening")
        if self._dark_current_frame is None:
            raise Exception("call set_dark_current_frames before flattening")
        if self._normalized_flat_frame is None:
            raise Exception("set set_flat_frames before flattening")
        
        return self.dark_subtract(frame, exposure_time)/self._normalized_flat_frame

    def bias_frame(self) -> Image.Image:
        """
        TODO
        """

        return np.copy(self._bias_frame)
    
    def dark_current_frame(self) -> Image.Image:
        """
        TODO
        """

        return np.copy(self._dark_current_frame)
    
    def flat_frame(self) -> Image.Image:
        """
        TODO
        """

        return np.copy(self._normalized_flat_frame)

